import abc
import pkginfo
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Callable, List, NamedTuple, Type

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


class OrigPkgDistReviewer:
    _dist_classes = [pkginfo.SDist, pkginfo.Wheel]

    def __init__(
            self,
            srepkg_content_path: Path,
            target_dist_types:
            tuple[Callable[..., pkginfo.Distribution]] = DEFAULT_DIST_CLASSES):
        self._srepkg_content_path = srepkg_content_path
        self._target_dist_types = target_dist_types

    @property
    def _srepkg_contents(self):
        return list(self._srepkg_content_path.iterdir())

    def _get_dist_name_version(self, dist_path: Path):
        for dist_class in self._target_dist_types:
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
            raise ce.MissingOrigPkgContent(str(self._srepkg_content_path))
        if len(dists_info) > 1:
            raise ce.MultiplePackagesPresent

        unique_pkg_version = list(dists_info.keys())[0]

        if len(dists_info[unique_pkg_version]) == 0:
            raise ce.MissingOrigPkgContent

    def get_existing_dists_info(self) -> PkgWithFoundDists:
        current_dists_info = {}

        for item in self._srepkg_contents:
            item_info = self._get_dist_name_version(item)
            if item_info:
                current_dists_info.setdefault(
                    item_info.pkg_inf, [])
                current_dists_info[item_info.pkg_inf].append(item_info.dist_inf)

        self._validate_dists_info(current_dists_info)

        return PkgWithFoundDists(
            pkg_inf=list(current_dists_info.keys())[0],
            all_dists=list(current_dists_info.values())[0])


class OriginalSourceCompleter:

    def __init__(
            self,
            srepkg_content_path: Path,
            required_dist_types:
            tuple[Callable[..., pkginfo.Distribution]] = DEFAULT_DIST_CLASSES):
        self._srepkg_content_path = srepkg_content_path
        self._required_dist_types = required_dist_types

    def _id_missing_dist_types(
            self,
            existing_dists_info: PkgWithFoundDists) -> \
            DistTypesStatus:
        dist_types_found = [
            item.dist_type for item in existing_dists_info.all_dists]

        missing_dist_types = [dist_type for dist_type in
                              self._required_dist_types if dist_type
                              not in dist_types_found]

        return DistTypesStatus(found=dist_types_found,
                               missing=missing_dist_types)

    def build_missing_dist_types(self):
        existing_dists_info = OrigPkgDistReviewer(self._srepkg_content_path) \
            .get_existing_dists_info()
        dist_types_status = self._id_missing_dist_types(existing_dists_info)

        dist_converter = DistConverter(
            srepkg_content_path=self._srepkg_content_path,
            existing_dists_info=existing_dists_info,
            dist_types_status=dist_types_status)

        dist_converter.build_missing_dist_types()


class DistConverter:
    _supported_dist_types = DEFAULT_DIST_CLASSES

    _dist_type_build_args = {
        pkginfo.SDist: '--sdist',
        pkginfo.Wheel: '--wheel'
    }

    def __init__(
            self,
            srepkg_content_path: Path,
            existing_dists_info: PkgWithFoundDists,
            dist_types_status: DistTypesStatus):
        self._srepkg_content_path = srepkg_content_path
        self._existing_dists_info = existing_dists_info
        self._dist_types_status = dist_types_status
        self._compressed_file_extractor = cft.CompressedFileExtractor()

    def _validate_dist_types_status(self):

        if any([item not in self._supported_dist_types for item in
                self._dist_types_status.missing]):
            raise ce.TargetDistTypeNotSupported

        if len(self._dist_types_status.missing) > 0 and not any([
            item in self._supported_dist_types for item
            in self._dist_types_status.found]):
            raise ce.NoSupportedSrcDistTypes

        return self

    def build_missing_dist_types(self):
        build_from_dist = self._dist_types_status.found[
            [item in self._supported_dist_types for item in
             self._dist_types_status.found].index(True)]

        build_from_filename = [
            item.file_name for item in self._existing_dists_info.all_dists if
            item.dist_type == build_from_dist][0]
        temp_unpack_dir_obj = tempfile.TemporaryDirectory()
        unpack_dir = Path(temp_unpack_dir_obj.name)

        existing_dist = self._srepkg_content_path / build_from_filename

        self._compressed_file_extractor.extract(existing_dist, unpack_dir)

        for missing_dist in self._dist_types_status.missing:
            with dir_change_to(str(unpack_dir)):
                subprocess.call([
                    sys.executable, '-m', 'build', '--outdir',
                    str(self._srepkg_content_path),
                    self._dist_type_build_args[missing_dist]])

        temp_unpack_dir_obj.cleanup()

        return self


class ConstructionDir(re_int.SettleableSrepkgDirInterface,
                      osp_int.WritableSrepkgDirInterface):
    @abc.abstractmethod
    def __init__(self, construction_dir: Path):
        self._construction_dir = construction_dir
        self._srepkg_root = construction_dir / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg = self._srepkg_root / uuid.uuid4().hex
        self._srepkg.mkdir()

    @property
    def srepkg_root_path(self):
        return self._srepkg_root

    @property
    def srepkg_content_path(self):
        return self._srepkg

    def rename_sub_dirs(self, srepkg_root: str, srepkg: str):
        self._srepkg.rename(self._srepkg.parent.absolute() / srepkg)
        self._srepkg_root.rename(self._srepkg_root.parent.absolute()
                                 / srepkg_root)
        self._srepkg_root = self._srepkg_root.parent.absolute() / srepkg_root
        self._srepkg = self._srepkg_root / srepkg

    def build_missing_items(self):
        source_completer = OriginalSourceCompleter(srepkg_content_path=self._srepkg)
        source_completer.build_missing_dist_types()


class CustomConstructionDir(ConstructionDir):
    def __init__(self, construction_dir: Path):
        super().__init__(construction_dir)

    def settle(self):
        print(f"An uncompressed copy of {self._srepkg.name} has been saved in "
              f"{str(self._srepkg_root)}")


class TempConstructionDir(ConstructionDir):
    def __init__(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name))

    def settle(self):
        self._temp_dir_obj.cleanup()
