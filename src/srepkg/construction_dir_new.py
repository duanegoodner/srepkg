import abc
import shutil

import pkginfo
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, NamedTuple

import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.dist_archive_file_tools as cft
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.repackager_new_interfaces as re_int
from srepkg.utils.cd_context_manager import dir_change_to

DEFAULT_DIST_CLASSES = (pkginfo.SDist, pkginfo.Wheel)
DEFAULT_SREPKG_SUFFIX = "srepkg"


@dataclass
class DistInfo:
    path: Path
    dist_obj: pkginfo.Distribution


@dataclass
class OrigSrcSummary:
    pkg_name: str
    pkg_version: str
    dists: List[DistInfo]

    @property
    def has_wheel(self):
        return any([isinstance(dist.dist_obj, pkginfo.Wheel) for dist in
                    self.dists])

    @property
    def has_sdist(self):
        return any([isinstance(dist.dist_obj, pkginfo.SDist) for dist in
                    self.dists])


class PkgNameVersion(NamedTuple):
    pkg_name: str
    pkg_version: str


class DistNameType(NamedTuple):
    file_name: str
    dist_type: Callable[..., pkginfo.Distribution]


class PkgDistInfo(NamedTuple):
    pkg_inf: PkgNameVersion
    dist_inf: DistNameType


class PkgWithFoundDists(NamedTuple):
    pkg_inf: PkgNameVersion
    all_dists: List[DistNameType]


class DistTypesStatus(NamedTuple):
    found: List[Callable[..., pkginfo.Distribution]]
    missing: List[Callable[..., pkginfo.Distribution]]


class ConstructionDirSummary(NamedTuple):
    pkg_with_found_dists: PkgWithFoundDists
    dist_types_status: DistTypesStatus


class ConstructionDir(re_int.SettleableSrepkgDirInterface,
                      osp_int.WritableSrepkgDirInterface):
    @abc.abstractmethod
    def __init__(
            self,
            construction_dir_arg: Path,
            srepkg_name_arg: str = None,
            supported_dist_types:
            tuple[Callable[..., pkginfo.Distribution]] = DEFAULT_DIST_CLASSES):
        self._root = construction_dir_arg
        self._srepkg_root = construction_dir_arg / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg_inner = self._srepkg_root / uuid.uuid4().hex
        self._srepkg_inner.mkdir()
        self._custom_srepkg_name = srepkg_name_arg
        self._supported_dist_types = supported_dist_types

    @property
    def root(self):
        return self._root

    @property
    def root_contents(self):
        return list(self._root.iterdir())

    @property
    def srepkg_root(self):
        return self._srepkg_root

    @property
    def srepkg_root_contents(self):
        return list(self._srepkg_root.iterdir())

    @property
    def srepkg_inner(self):
        return self._srepkg_inner

    @property
    def srepkg_inner_contents(self):
        return list(self._srepkg_inner.iterdir())

    @property
    def supported_dist_types(self):
        return self._supported_dist_types

    def _rename_sub_dirs(self, srepkg_root_new: str, srepkg_inner_new: str):
        new_srepkg_root_path = Path(self._root / srepkg_root_new)
        new_srepkg_root_path.mkdir()
        new_srepkg_inner_path = Path(self._root / srepkg_root_new / srepkg_inner_new)
        new_srepkg_inner_path.mkdir()
        for item in self._srepkg_inner.iterdir():
            shutil.move(item, new_srepkg_inner_path)
        self._srepkg_inner.rmdir()
        self._srepkg_inner = new_srepkg_inner_path

        for item in self._srepkg_root.iterdir():
            shutil.move(item, new_srepkg_root_path)
        self._srepkg_root.rmdir()
        self._srepkg_root = new_srepkg_root_path

    def _update_sub_dir_names(self, discovered_pkg_name: str):
        if self._custom_srepkg_name:
            srepkg_name = self._custom_srepkg_name
        else:
            srepkg_name = f"{discovered_pkg_name}{DEFAULT_SREPKG_SUFFIX}"

        self._rename_sub_dirs(
            srepkg_root_new=f"{discovered_pkg_name}_as_{srepkg_name}",
            srepkg_inner_new=srepkg_name)

    def finalize(self):
        # construction_dir_summary = ConstructionDirReviewer(self).get_summary()
        construction_dir_summary = ConstructionDirReviewer(self) \
            .get_existing_dists_summary()

        if (not construction_dir_summary.has_wheel) and \
                construction_dir_summary.has_sdist:
            SdistToWheelConverter(self, construction_dir_summary).build_wheel()

        self._update_sub_dir_names(
            discovered_pkg_name=construction_dir_summary.pkg_name)


#         TODO call rename_sub_dirs now that pkg name is known
#         TODO change name of build_missing items to something like update...


class CustomConstructionDir(ConstructionDir):
    def __init__(self, construction_dir_arg: Path, srepkg_name_arg: str = None):
        super().__init__(construction_dir_arg, srepkg_name_arg)

    def settle(self):
        print(
            f"An uncompressed copy of {self._srepkg_inner.name} has been saved "
            f"in {str(self._srepkg_root)}")


class TempConstructionDir(ConstructionDir):
    def __init__(self, srepkg_name_arg: str = None):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name), srepkg_name_arg)

    def settle(self):
        self._temp_dir_obj.cleanup()


class SdistToWheelConverter:
    def __init__(
            self,
            construction_dir: ConstructionDir,
            construction_dir_summary: OrigSrcSummary):
        self._construction_dir = construction_dir
        self._construction_dir_summary = construction_dir_summary
        self._compressed_file_extractor = cft.CompressedFileExtractor()

    @property
    def _unpacked_src_dir_name(self):
        pkg_name = self._construction_dir_summary.pkg_name
        pkg_version = self._construction_dir_summary.pkg_version
        return f"{pkg_name}-{pkg_version}"

    def _get_build_from_dist(self):
        try:
            build_from_dist = next(
                dist for dist in self._construction_dir_summary.dists if
                isinstance(dist.dist_obj, pkginfo.sdist.SDist))
        except StopIteration:
            raise ce.NoSDistForWheelConstruction(
                self._construction_dir.srepkg_root)

        return build_from_dist

    def build_wheel(self):
        build_from_dist = self._get_build_from_dist()
        temp_unpack_dir_obj = tempfile.TemporaryDirectory()
        unpack_root = Path(temp_unpack_dir_obj.name)

        self._compressed_file_extractor.extract(
            build_from_dist.path, unpack_root)

        with dir_change_to(str(unpack_root / self._unpacked_src_dir_name)):
            subprocess.call([
                sys.executable, '-m', 'build', '--outdir',
                str(self._construction_dir.srepkg_inner), '--wheel'])

        temp_unpack_dir_obj.cleanup()


# class DistConverter:
#     _supported_dist_types = DEFAULT_DIST_CLASSES
#
#     _dist_type_build_args = {
#         pkginfo.SDist: '--sdist',
#         pkginfo.Wheel: '--wheel'
#     }
#
#     def __init__(
#             self,
#             construction_dir: ConstructionDir,
#             construction_dir_summary: ConstructionDirSummary):
#         self._construction_dir = construction_dir
#         self._construction_dir_summary = construction_dir_summary
#         self._compressed_file_extractor = cft.CompressedFileExtractor()
#
#     @property
#     def _unpacked_src_dir_name(self):
#         pkg_name = self._construction_dir_summary \
#         .pkg_with_found_dists.pkg_inf \
#             .pkg_name
#         pkg_version = self._construction_dir_summary.pkg_with_found_dists \
#             .pkg_inf.pkg_version
#         return f"{pkg_name}-{pkg_version}"
#
#     def _validate_dist_types_status(self):
#
#         if any([item not in self._supported_dist_types for item in
#                 self._construction_dir_summary.dist_types_status.missing]):
#             raise ce.TargetDistTypeNotSupported
#
#         if len(self._construction_dir_summary.dist_types_status.missing) > 0 \
#                 and not any([item in self._supported_dist_types for item in
#                              self._construction_dir_summary.dist_types_status
#                             .found]):
#             raise ce.NoSupportedSrcDistTypes
#
#         return self
#
#     def build_missing_dist_types(self):
#         build_from_dist = \
#             self._construction_dir_summary.dist_types_status.found[
#                 [item in self._supported_dist_types for item in
#                  self._construction_dir_summary.dist_types_status.found].index(
#                     True)]
#
#         build_from_filename = [
#             item.file_name for item in self._construction_dir_summary
#                 .pkg_with_found_dists.all_dists if
#             item.dist_type == build_from_dist][0]
#         temp_unpack_dir_obj = tempfile.TemporaryDirectory()
#         unpack_dir = Path(temp_unpack_dir_obj.name)
#
#         existing_dist = self._construction_dir.srepkg_inner / \
#                         build_from_filename
#
#         self._compressed_file_extractor.extract(existing_dist, unpack_dir)
#
#         for missing_dist in self._construction_dir_summary.dist_types_status \
#                 .missing:
#             with dir_change_to(str(unpack_dir / self._unpacked_src_dir_name)):
#                 subprocess.call([
#                     sys.executable, '-m', 'build', '--outdir',
#                     str(self._construction_dir.srepkg_inner),
#                     self._dist_type_build_args[missing_dist]])
#
#         temp_unpack_dir_obj.cleanup()
#
#         return self


class ConstructionDirReviewer:

    def __init__(
            self,
            construction_dir: ConstructionDir):
        self._construction_dir = construction_dir

    def _get_dist_info(self, dist_path: Path):
        for dist_class in self._construction_dir.supported_dist_types:
            try:
                dist_obj = dist_class(dist_path)
                return DistInfo(path=dist_path, dist_obj=dist_obj)
                # return PkgDistInfo(
                #     pkg_inf=PkgNameVersion(
                #         pkg_name=dist_obj.name, pkg_version=dist_obj.version),
                #     dist_inf=DistNameType(
                #         file_name=dist_path.name, dist_type=dist_class))
            except ValueError:
                pass

    # def _validate_dists_info(
    #         self,
    #         existing_dists: List[DistInfo]):
    #     # dists_info: dict[PkgNameVersion, List[DistNameType]]):
    #     if not existing_dists:
    #         # if not dists_info:
    #         raise ce.MissingOrigPkgContent(str(
    #             self._construction_dir.srepkg_inner))
    #     # if len(dists_info) > 1:
    #     #     raise ce.MultiplePackagesPresent
    #
    #     unique_pkgs = [(dist.dist_obj.name, dist.dist_obj.version) for dist in
    #                    existing_dists]
    #     if len(set(unique_pkgs)) > 1:
    #         raise ce.MultiplePackagesPresent
    #
    #     unique_pkg = unique_pkgs[0]
    #
    #     return OrigSrcSummary(
    #         pkg_name=unique_pkg[0],
    #         pkg_version=unique_pkg[1],
    #         dists=existing_dists)

    # unique_pkg_version = list(dists_info.keys())[0]
    #
    # if len(dists_info[unique_pkg_version]) == 0:
    #     raise ce.MissingOrigPkgContent
    #
    # return self

    def _get_existing_dists(self) -> List[DistInfo]:
        # current_dists_info = {}
        existing_dists = []

        for item in self._construction_dir.srepkg_inner_contents:
            item_info = self._get_dist_info(item)
            if item_info:
                existing_dists.append(item_info)
                # current_dists_info.setdefault(
                #     item_info.pkg_inf, [])
                # current_dists_info[item_info.pkg_inf].append(item_info.dist_inf)

        return existing_dists
        #
        # self._validate_dists_info(current_dists_info)
        #
        # return PkgWithFoundDists(
        #     pkg_inf=list(current_dists_info.keys())[0],
        #     all_dists=list(current_dists_info.values())[0])

    def _validate_existing_dists(
            self,
            existing_dists: List[DistInfo]):
        if not existing_dists:
            raise ce.MissingOrigPkgContent(str(
                self._construction_dir.srepkg_inner))

        unique_pkgs = [(dist.dist_obj.name, dist.dist_obj.version) for dist in
                       existing_dists]
        if len(set(unique_pkgs)) > 1:
            raise ce.MultiplePackagesPresent

        unique_pkg = unique_pkgs[0]

        return OrigSrcSummary(
            pkg_name=unique_pkg[0],
            pkg_version=unique_pkg[1],
            dists=existing_dists)

    def get_existing_dists_summary(self) -> OrigSrcSummary:

        existing_dists = self._get_existing_dists()
        return self._validate_existing_dists(existing_dists)

    # def _id_missing_dist_types(
    #         self,
    #         existing_dists_info: PkgWithFoundDists) -> DistTypesStatus:
    #     dist_types_found = [
    #         item.dist_type for item in existing_dists_info.all_dists]
    #
    #     missing_dist_types = [dist_type for dist_type in
    #                           self._construction_dir.supported_dist_types if
    #                           dist_type not in dist_types_found]
    #
    #     return DistTypesStatus(found=dist_types_found,
    #                            missing=missing_dist_types)
    #
    # def get_summary(self):
    #     existing_dists_info = self._get_existing_dists_info()
    #     dist_types_found = [
    #         item.dist_type for item in existing_dists_info.all_dists]
    #     missing_dist_types = [dist_type for dist_type in
    #                           self._construction_dir.supported_dist_types if
    #                           dist_type not in dist_types_found]
    #
    #     dist_types_status = DistTypesStatus(
    #         found=dist_types_found,
    #         missing=missing_dist_types)
    #
    #     return ConstructionDirSummary(
    #         pkg_with_found_dists=existing_dists_info,
    #         dist_types_status=dist_types_status)
