import abc
import shutil

import pkginfo
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import List

import wheel_inspect

import srepkg.srepkg_builder_new_ds_and_int as sb_new_int
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.dist_archive_file_tools as cft
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.retriever_provider_shared_interface as rp_shared_int
from srepkg.utils.cd_context_manager import dir_change_to

DEFAULT_DIST_CLASSES = (pkginfo.SDist, pkginfo.Wheel)
DEFAULT_SREPKG_SUFFIX = "srepkg"


# @dataclass
# class DistInfo:
#     path: Path
#     dist_obj: pkginfo.Distribution
#
#
# @dataclass
# class OrigPkgSrcSummary:
#     pkg_name: str
#     pkg_version: str
#     dists: List[DistInfo]
#     entry_pts: sb_new_int.PkgCSEntryPoints = None
#
#     @property
#     def has_wheel(self):
#         return any([type(dist.dist_obj) == pkginfo.Wheel for dist in
#                     self.dists])
#
#     @property
#     def wheel_path(self):
#         if self.has_wheel:
#             return [dist.path for dist in self.dists if type(dist.dist_obj) ==
#                     pkginfo.Wheel][0]
#
#     @property
#     def has_sdist(self):
#         return any([type(dist.dist_obj) == pkginfo.SDist for dist in
#                     self.dists])


class ConstructionDir(
        rp_shared_int.OrigPkgReceiver, osp_int.ManageableConstructionDir,
        sb_new_int.SrepkgComponentReceiver):
    def __init__(self, construction_dir_arg: Path, srepkg_name_arg: str = None):
        self._root = construction_dir_arg
        self._srepkg_root = construction_dir_arg / uuid.uuid4().hex
        self._srepkg_inner = self._srepkg_root / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg_inner.mkdir()
        self._custom_srepkg_name = srepkg_name_arg
        self._supported_dist_types = DEFAULT_DIST_CLASSES
        self._srepkg_name = None
        self._orig_pkg_src_summary = None

    @property
    def _root_contents(self):
        return list(self._root.iterdir())

    @property
    def srepkg_root(self):
        return self._srepkg_root

    @property
    def _srepkg_root_contents(self):
        return list(self._srepkg_root.iterdir())

    @property
    def orig_pkg_dest(self) -> Path:
        return self._srepkg_inner

    @property
    def srepkg_name(self) -> str:
        return self._srepkg_name

    @property
    def srepkg_inner(self):
        return self._srepkg_inner

    @property
    def srepkg_inner_contents(self):
        return list(self._srepkg_inner.iterdir())

    @property
    def supported_dist_types(self):
        return self._supported_dist_types

    @property
    def orig_pkg_src_summary(self):
        return self._orig_pkg_src_summary

    @orig_pkg_src_summary.setter
    def orig_pkg_src_summary(
            self,
            construction_dir_summary: sb_new_int.OrigPkgSrcSummary):
        self._orig_pkg_src_summary = construction_dir_summary

    @property
    def orig_pkg_entry_pts(self) -> sb_new_int.PkgCSEntryPoints:
        return self._orig_pkg_src_summary.entry_pts

    def _rename_sub_dirs(self, srepkg_root_new: str, srepkg_inner_new: str):
        new_srepkg_root_path = Path(self._root / srepkg_root_new)
        new_srepkg_root_path.mkdir()
        new_srepkg_inner_path = Path(
            self._root / srepkg_root_new / srepkg_inner_new)
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

    def _extract_cs_entry_pts_from_wheel(self):
        wheel_data = wheel_inspect.inspect_wheel(
            self._orig_pkg_src_summary.wheel_path)

        cs_entry_pts = []
        wheel_inspect_epcs = \
            wheel_data['dist_info']['entry_points']['console_scripts']
        for key, value in wheel_inspect_epcs.items():
            cs_entry_pts.append(
                sb_new_int.CSEntryPoint(
                    command=key,
                    module=value['module'],
                    attr=value['attr'],
                    extras=value['extras']
                )
            )
        return sb_new_int.PkgCSEntryPoints(cs_entry_pts=cs_entry_pts)

    def finalize(self):
        prelim_orig_pkg_src_summary = ConstructionDirReviewer(self) \
            .get_existing_dists_summary()

        if (not prelim_orig_pkg_src_summary.has_wheel) and \
                prelim_orig_pkg_src_summary.has_sdist:
            SdistToWheelConverter(self,
                                  prelim_orig_pkg_src_summary).build_wheel()

        self._orig_pkg_src_summary = ConstructionDirReviewer(self) \
            .get_existing_dists_summary()

        self._orig_pkg_src_summary.entry_pts =\
            self._extract_cs_entry_pts_from_wheel()

        self._update_sub_dir_names(
            discovered_pkg_name=prelim_orig_pkg_src_summary.pkg_name)

    @abc.abstractmethod
    def settle(self):
        pass


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
            construction_dir_summary: sb_new_int.OrigPkgSrcSummary):
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


class ConstructionDirReviewer:

    def __init__(
            self,
            construction_dir: ConstructionDir):
        self._construction_dir = construction_dir

    def _get_dist_info(self, dist_path: Path):
        for dist_class in self._construction_dir.supported_dist_types:
            try:
                dist_obj = dist_class(dist_path)
                return sb_new_int.DistInfo(path=dist_path, dist_obj=dist_obj)
            except ValueError:
                pass

    def _get_existing_dists(self) -> List[sb_new_int.DistInfo]:
        existing_dists = []

        for item in self._construction_dir.srepkg_inner_contents:
            item_info = self._get_dist_info(item)
            if item_info:
                existing_dists.append(item_info)

        return existing_dists

    def _validate_existing_dists(
            self,
            existing_dists: List[sb_new_int.DistInfo]):
        if not existing_dists:
            raise ce.MissingOrigPkgContent(str(
                self._construction_dir.srepkg_inner))

        unique_pkgs = [(dist.dist_obj.name, dist.dist_obj.version) for dist in
                       existing_dists]
        if len(set(unique_pkgs)) > 1:
            raise ce.MultiplePackagesPresent

        unique_pkg = unique_pkgs[0]

        return sb_new_int.OrigPkgSrcSummary(
            pkg_name=unique_pkg[0],
            pkg_version=unique_pkg[1],
            dists=existing_dists)

    def get_existing_dists_summary(self) -> sb_new_int.OrigPkgSrcSummary:

        existing_dists = self._get_existing_dists()
        return self._validate_existing_dists(existing_dists)
