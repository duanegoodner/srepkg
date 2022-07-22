import abc
import pkginfo
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Callable, List, NamedTuple

import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.dist_archive_file_tools as cft
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.repackager_new_interfaces as re_int
from srepkg.utils.cd_context_manager import dir_change_to

DEFAULT_DIST_CLASSES = (pkginfo.SDist, pkginfo.Wheel)


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
            required_dist_types:
            tuple[Callable[..., pkginfo.Distribution]] = DEFAULT_DIST_CLASSES):
        self._root = construction_dir_arg
        self._srepkg_root = construction_dir_arg / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg_inner = self._srepkg_root / uuid.uuid4().hex
        self._srepkg_inner.mkdir()
        self._required_dist_types = required_dist_types

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
    def required_dist_types(self):
        return self._required_dist_types

    def rename_sub_dirs(self, srepkg_root: str, srepkg_inner: str):
        self._srepkg_inner.rename(self._srepkg_inner.parent.absolute() / srepkg_inner)
        self._srepkg_root.rename(self._srepkg_root.parent.absolute()
                                 / srepkg_root)
        self._srepkg_root = self._srepkg_root.parent.absolute() / srepkg_root
        self._srepkg_inner = self._srepkg_root / srepkg_inner

    def build_missing_items(self):
        construction_dir_summary = ConstructionDirReviewer(self).get_summary()
        DistConverter(
            construction_dir=self,
            construction_dir_summary=construction_dir_summary) \
            .build_missing_dist_types()


class CustomConstructionDir(ConstructionDir):
    def __init__(self, construction_dir_arg: Path):
        super().__init__(construction_dir_arg)

    def settle(self):
        print(
            f"An uncompressed copy of {self._srepkg_inner.name} has been saved "
            f"in {str(self._srepkg_root)}")


class TempConstructionDir(ConstructionDir):
    def __init__(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name))

    def settle(self):
        self._temp_dir_obj.cleanup()


class DistConverter:
    _supported_dist_types = DEFAULT_DIST_CLASSES

    _dist_type_build_args = {
        pkginfo.SDist: '--sdist',
        pkginfo.Wheel: '--wheel'
    }

    def __init__(
            self,
            construction_dir: ConstructionDir,
            construction_dir_summary: ConstructionDirSummary):
        self._construction_dir = construction_dir
        self._construction_dir_summary = construction_dir_summary
        self._compressed_file_extractor = cft.CompressedFileExtractor()

    def _validate_dist_types_status(self):

        if any([item not in self._supported_dist_types for item in
                self._construction_dir_summary.dist_types_status.missing]):
            raise ce.TargetDistTypeNotSupported

        if len(self._construction_dir_summary.dist_types_status.missing) > 0 \
                and not any([item in self._supported_dist_types for item in
                             self._construction_dir_summary.dist_types_status
                            .found]):
            raise ce.NoSupportedSrcDistTypes

        return self

    def build_missing_dist_types(self):
        build_from_dist = \
            self._construction_dir_summary.dist_types_status.found[
                [item in self._supported_dist_types for item in
                 self._construction_dir_summary.dist_types_status.found].index(
                    True)]

        build_from_filename = [
            item.file_name for item in self._construction_dir_summary
                .pkg_with_found_dists.all_dists if
            item.dist_type == build_from_dist][0]
        temp_unpack_dir_obj = tempfile.TemporaryDirectory()
        unpack_dir = Path(temp_unpack_dir_obj.name)

        existing_dist = self._construction_dir.srepkg_inner /\
            build_from_filename

        self._compressed_file_extractor.extract(existing_dist, unpack_dir)

        for missing_dist in self._construction_dir_summary.dist_types_status\
                .missing:
            with dir_change_to(str(unpack_dir)):
                subprocess.call([
                    sys.executable, '-m', 'build', '--outdir',
                    str(self._construction_dir.srepkg_inner),
                    self._dist_type_build_args[missing_dist]])

        temp_unpack_dir_obj.cleanup()

        return self


class ConstructionDirReviewer:

    def __init__(
            self,
            construction_dir: ConstructionDir):
        self._construction_dir = construction_dir

    def _get_dist_name_version(self, dist_path: Path):
        for dist_class in self._construction_dir.required_dist_types:
            try:
                dist_info = dist_class(dist_path)
                return PkgDistInfo(
                    pkg_inf=PkgNameVersion(
                        pkg_name=dist_info.name, pkg_version=dist_info.version),
                    dist_inf=DistNameType(
                        file_name=dist_path.name, dist_type=dist_class))
            except ValueError:
                pass

    def _validate_dists_info(
            self,
            dists_info: dict[PkgNameVersion, List[DistNameType]]):
        if not dists_info:
            raise ce.MissingOrigPkgContent(str(
                self._construction_dir.srepkg_inner))
        if len(dists_info) > 1:
            raise ce.MultiplePackagesPresent

        unique_pkg_version = list(dists_info.keys())[0]

        if len(dists_info[unique_pkg_version]) == 0:
            raise ce.MissingOrigPkgContent

        return self

    def _get_existing_dists_info(self) -> PkgWithFoundDists:
        current_dists_info = {}

        for item in self._construction_dir.srepkg_inner_contents:
            item_info = self._get_dist_name_version(item)
            if item_info:
                current_dists_info.setdefault(
                    item_info.pkg_inf, [])
                current_dists_info[item_info.pkg_inf].append(item_info.dist_inf)

        self._validate_dists_info(current_dists_info)

        return PkgWithFoundDists(
            pkg_inf=list(current_dists_info.keys())[0],
            all_dists=list(current_dists_info.values())[0])

    def _id_missing_dist_types(
            self,
            existing_dists_info: PkgWithFoundDists) -> DistTypesStatus:
        dist_types_found = [
            item.dist_type for item in existing_dists_info.all_dists]

        missing_dist_types = [dist_type for dist_type in
                              self._construction_dir.required_dist_types if
                              dist_type not in dist_types_found]

        return DistTypesStatus(found=dist_types_found,
                               missing=missing_dist_types)

    def get_summary(self):
        existing_dists_info = self._get_existing_dists_info()
        dist_types_found = [
            item.dist_type for item in existing_dists_info.all_dists]
        missing_dist_types = [dist_type for dist_type in
                              self._construction_dir.required_dist_types if
                              dist_type not in dist_types_found]

        dist_types_status = DistTypesStatus(
            found=dist_types_found,
            missing=missing_dist_types)

        return ConstructionDirSummary(
            pkg_with_found_dists=existing_dists_info,
            dist_types_status=dist_types_status)
