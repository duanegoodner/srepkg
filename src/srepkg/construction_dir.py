import abc
import build
import pkginfo
import sys
import tempfile
import uuid
from pathlib import Path
from typing import List

import wheel_inspect

import srepkg.srepkg_builder_ds_and_int as sb_int
import srepkg.srepkg_builder_data_structs as sb_ds
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.dist_archive_file_tools as cft
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.retriever_provider_shared_interface as rp_shared_int

DEFAULT_DIST_CLASSES = (pkginfo.SDist, pkginfo.Wheel)
DEFAULT_SREPKG_SUFFIX = "srepkg"


class ConstructionDir(
    rp_shared_int.OrigPkgReceiver, osp_int.ManageableConstructionDir,
    sb_int.SrepkgComponentReceiver):
    def __init__(self,
                 construction_dir_command: Path,
                 srepkg_name_command: str = None):
        self._root = construction_dir_command
        self._srepkg_root = construction_dir_command / uuid.uuid4().hex
        self._srepkg_inner = self._srepkg_root / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg_inner.mkdir()
        (self._srepkg_root / 'orig_dist').mkdir()
        self._custom_srepkg_name = srepkg_name_command
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
    def orig_pkg_dists(self) -> Path:
        return self._srepkg_root / 'orig_dist'

    @property
    def _orig_pkg_dists_contents(self) -> List[Path]:
        return list(self.orig_pkg_dists.iterdir())

    def _get_dist_info(self, dist_path: Path):
        for dist_class in self.supported_dist_types:
            try:
                dist_obj = dist_class(dist_path)
                return sb_ds.DistInfo(path=dist_path, dist_obj=dist_obj)
            except ValueError:
                pass

    @property
    def dists(self):
        return [self._get_dist_info(entry) for entry in
                self._orig_pkg_dists_contents]

    @property
    def _unique_orig_pkgs(self):
        unique_pkgs = {
            sb_ds.UniquePkg(
                # DistInfo changes any "_" to "-" in pkg name. Undo that.
                name=dist.dist_obj.name.replace("-", "_"),
                version=dist.dist_obj.version)
            for dist in self.dists}
        if len(unique_pkgs) > 1:
            raise ce.MultiplePackagesPresent(self.dists)
        return unique_pkgs

    @property
    def orig_pkg_name(self):
        if self._unique_orig_pkgs:
            return list(self._unique_orig_pkgs)[0].name  # .replace("-", "_")

    @property
    def orig_pkg_version(self):
        if self._unique_orig_pkgs:
            return list(self._unique_orig_pkgs)[0].version

    @property
    def has_wheel(self):
        return any([type(dist.dist_obj) == pkginfo.Wheel for dist in
                    self.dists])

    @property
    def wheel_path(self):
        if self.has_wheel:
            return [dist.path for dist in self.dists if type(dist.dist_obj) ==
                    pkginfo.Wheel][0]

    # @property
    # def has_platform_indep_wheel(self):
    #     return self.has_wheel and \
    #            ('any' in parse_wheel_filename(self.wheel_path.name)
    #             .platform_tags)

    @property
    def has_sdist(self):
        return any([type(dist.dist_obj) == pkginfo.SDist for dist in
                    self.dists])

    # @property
    # def sdist_path(self):
    #     if self.has_sdist:
    #         return [dist.path for dist in self.dists if type(dist.dist_obj) ==
    #                 pkginfo.SDist][0]

    # @property
    # def src_for_srepkg_wheel(self) -> Union[Path, None]:
    #     if self.has_wheel:
    #         return self.wheel_path
    #     if self.has_sdist:
    #         return self.sdist_path

    # @property
    # def src_for_srepkg_sdist(self) -> Union[Path, None]:
    #     if self.has_platform_indep_wheel:
    #         return self.wheel_path
    #     if self.has_sdist:
    #         return self.sdist_path

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

    def _rename_sub_dirs(self, srepkg_root_new: str, srepkg_inner_new: str):

        self._srepkg_inner.replace(
            self._srepkg_inner.parent.absolute() / srepkg_inner_new)
        self._srepkg_root.replace(
            self._srepkg_root.parent.absolute() / srepkg_root_new)

        self._srepkg_root = self._srepkg_root.parent.absolute() / \
                            srepkg_root_new
        self._srepkg_inner = self._srepkg_root / srepkg_inner_new

    def _update_srepkg_and_dir_names(self, discovered_pkg_name: str):
        if self._custom_srepkg_name:
            srepkg_name = self._custom_srepkg_name
        else:
            srepkg_name = f"{discovered_pkg_name}{DEFAULT_SREPKG_SUFFIX}"

        self._rename_sub_dirs(
            srepkg_root_new=f"{discovered_pkg_name}_as_{srepkg_name}",
            srepkg_inner_new=srepkg_name)

        self._srepkg_name = srepkg_name

    def _extract_cs_entry_pts_from_wheel(self):
        wheel_data = wheel_inspect.inspect_wheel(
            self.wheel_path)

        cs_entry_pts = []
        wheel_inspect_epcs = \
            wheel_data['dist_info']['entry_points']['console_scripts']
        for key, value in wheel_inspect_epcs.items():
            cs_entry_pts.append(
                sb_ds.CSEntryPoint(
                    command=key,
                    module=value['module'],
                    attr=value['attr'],
                )
            )
        return sb_ds.PkgCSEntryPoints(cs_entry_pts=cs_entry_pts)

    def finalize(self):
        if not self.has_sdist and not self.has_wheel:
            raise ce.MissingOrigPkgContent(str(self.orig_pkg_dists))
        if not self.has_wheel and self.has_sdist:
            SdistToWheelConverter(self).build_wheel()
        self._update_srepkg_and_dir_names(
            discovered_pkg_name=self.orig_pkg_name)

        self._orig_pkg_src_summary = sb_ds.OrigPkgSrcSummary(
            pkg_name=self.orig_pkg_name,
            pkg_version=self.orig_pkg_version,
            dists=self.dists,
            entry_pts=self._extract_cs_entry_pts_from_wheel()
        )

    @abc.abstractmethod
    def settle(self):
        pass


class CustomConstructionDir(ConstructionDir):
    def __init__(self,
                 construction_dir_command: Path,
                 srepkg_name_command: str = None):
        super().__init__(construction_dir_command, srepkg_name_command)

    def settle(self):
        print(
            f"An uncompressed copy of {self._srepkg_inner.name} has been saved "
            f"in {str(self._srepkg_root)}")


class TempConstructionDir(ConstructionDir):
    def __init__(self, srepkg_name_command: str = None):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(
            construction_dir_command=Path(self._temp_dir_obj.name),
            srepkg_name_command=srepkg_name_command)

    def settle(self):
        self._temp_dir_obj.cleanup()


class SdistToWheelConverter:
    def __init__(
            self,
            construction_dir: ConstructionDir):
        self._construction_dir = construction_dir
        self._compressed_file_extractor = cft.CompressedFileExtractor()

    @property
    def _unpacked_src_dir_name(self):
        pkg_name = self._construction_dir.orig_pkg_name
        pkg_version = self._construction_dir.orig_pkg_version
        return f"{pkg_name}-{pkg_version}"

    def _get_build_from_dist(self):
        try:
            build_from_dist = next(
                dist for dist in self._construction_dir.dists if
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

        dist_builder = build.ProjectBuilder(
            srcdir=str(unpack_root / self._unpacked_src_dir_name),
            python_executable=sys.executable
        )

        dist_builder.build(
            distribution='wheel',
            output_directory=str(self._construction_dir.orig_pkg_dists)
        )

        temp_unpack_dir_obj.cleanup()
