import abc
import logging
import pkginfo
import tempfile
import uuid
from pathlib import Path
from typing import List

from yaspin import yaspin

import srepkg.dist_builder as db
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.dist_archive_file_tools as cft
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.repackager_data_structs as rp_ds
import srepkg.wheel_modifier as wm
import srepkg.utils.wheel_entry_point_extractor as we_pe

from inner_pkg_installer import yaspin_updater as yu

DEFAULT_DIST_CLASSES = (pkginfo.SDist, pkginfo.Wheel)
DEFAULT_SREPKG_SUFFIX = "srepkg"


class ConstructionDir(osp_int.ManageableConstructionDir):
    """
    Class for managing directory where SRE package is built.
    """

    def __init__(
        self, construction_dir_command: Path, srepkg_name_command: str = None
    ):
        self._root = construction_dir_command
        self._srepkg_root = construction_dir_command / uuid.uuid4().hex
        self._srepkg_inner = self._srepkg_root / uuid.uuid4().hex
        self._srepkg_root.mkdir(exist_ok=True, parents=True)
        self._srepkg_inner.mkdir(exist_ok=True, parents=True)
        (self._srepkg_root / "orig_dist").mkdir()
        self._custom_srepkg_name = srepkg_name_command
        self._supported_dist_types = DEFAULT_DIST_CLASSES
        self._srepkg_name = None
        self._summary = None

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
        return self._srepkg_root / "orig_dist"

    @property
    def _orig_pkg_dists_contents(self) -> List[Path]:
        return list(self.orig_pkg_dists.iterdir())

    def _get_dist_info(self, dist_path: Path):
        for dist_class in self.supported_dist_types:
            try:
                dist_obj = dist_class(dist_path)
                return rp_ds.DistInfo(path=dist_path, dist_obj=dist_obj)
            except ValueError:
                pass

    @property
    def dists(self):
        return [
            self._get_dist_info(entry)
            for entry in self._orig_pkg_dists_contents
        ]

    @property
    def _unique_orig_pkgs(self):
        unique_pkgs = {
            rp_ds.UniquePkg(
                # DistInfo changes any "_" to "-" in pkg name. Undo that.
                name=dist.dist_obj.name.replace("-", "_"),
                version=dist.dist_obj.version,
            )
            for dist in self.dists
        }
        if len(unique_pkgs) > 1:
            raise ce.MultiplePackagesPresent(self.dists)
        return unique_pkgs

    @property
    def orig_pkg_name(self):
        if self._unique_orig_pkgs:
            return list(self._unique_orig_pkgs)[0].name

    @property
    def pypi_version(self):
        if self._unique_orig_pkgs:
            return list(self._unique_orig_pkgs)[0].version

    @property
    def has_wheel(self):
        return any(
            [type(dist.dist_obj) == pkginfo.Wheel for dist in self.dists]
        )

    @property
    def wheel_path(self):
        if self.has_wheel:
            return [
                dist.path
                for dist in self.dists
                if type(dist.dist_obj) == pkginfo.Wheel
            ][0]

    @property
    def has_sdist(self):
        return any(
            [type(dist.dist_obj) == pkginfo.SDist for dist in self.dists]
        )

    # @property
    # def srepkg_name(self) -> str:
    #     return self._srepkg_name

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

        self._srepkg_inner.replace(
            self._srepkg_inner.parent.absolute() / srepkg_inner_new
        )
        self._srepkg_root.replace(
            self._srepkg_root.parent.absolute() / srepkg_root_new
        )

        self._srepkg_root = (
            self._srepkg_root.parent.absolute() / srepkg_root_new
        )
        self._srepkg_inner = self._srepkg_root / srepkg_inner_new

    def _update_srepkg_and_dir_names(self, discovered_pkg_name: str):
        if self._custom_srepkg_name:
            srepkg_name = self._custom_srepkg_name
        else:
            srepkg_name = f"{discovered_pkg_name}{DEFAULT_SREPKG_SUFFIX}"

        self._rename_sub_dirs(
            srepkg_root_new=f"{discovered_pkg_name}_as_{srepkg_name}",
            srepkg_inner_new=srepkg_name,
        )

        self._srepkg_name = srepkg_name

    def _ensure_valid_console_script_names(self):
        wheel_dist_info = wm.WheelDistInfo(wheel_path=self.wheel_path)
        if wheel_dist_info.has_console_script_name_with_dash:
            wm.WheelEntryPointsModifier(
                wheel_path=self.wheel_path
            ).modify_and_rebuild()

    def _extract_cs_entry_pts_from_wheel(self):
        return we_pe.WheelEntryPointExtractor(
            self.wheel_path
        ).get_entry_points()

    def _ensure_have_wheel(self):
        if not self.has_sdist and not self.has_wheel:
            raise ce.MissingOrigPkgContent(str(self.orig_pkg_dists))
        if not self.has_wheel and self.has_sdist:
            SdistToWheelConverter(self).build_wheel()

    def _set_summary(self):

        self._summary = rp_ds.ConstructionDirSummary(
            pkg_name=self.orig_pkg_name,
            pkg_version=self.pypi_version,
            srepkg_name=self._srepkg_name,
            srepkg_root=self._srepkg_root,
            orig_pkg_dists=self.orig_pkg_dists,
            srepkg_inner=self._srepkg_inner,
            dists=self.dists,
            entry_pts=self._extract_cs_entry_pts_from_wheel(),
        )

    def finalize(self):
        self._ensure_have_wheel()
        self._update_srepkg_and_dir_names(
            discovered_pkg_name=self.orig_pkg_name
        )

        self._ensure_valid_console_script_names()
        self._set_summary()
        return self._summary

    @abc.abstractmethod
    def settle(self):
        pass


class CustomConstructionDir(ConstructionDir):
    """
    Sublcass of ConstructionDir used when SrepkgCommand specifies a build
    location.
    """

    def __init__(
        self, construction_dir_command: Path, srepkg_name_command: str = None
    ):
        super().__init__(construction_dir_command, srepkg_name_command)

    def settle(self):
        print(
            f"An uncompressed copy of {self._srepkg_inner.name} has been saved "
            f"in {str(self._srepkg_root)}"
        )


class TempConstructionDir(ConstructionDir):
    """
    Sublcass of ConstructionDir used when SrepkgCommand does not specify a
    build location (and temp dir is used).
    """

    def __init__(self, srepkg_name_command: str = None):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(
            construction_dir_command=Path(self._temp_dir_obj.name),
            srepkg_name_command=srepkg_name_command,
        )

    def _set_summary(self):
        super()._set_summary()
        self._summary._temp_dir_obj = self._temp_dir_obj

    def settle(self):
        self._temp_dir_obj.cleanup()


class SdistToWheelConverter:
    """
    Converts a SDist to Wheel. Use this when original package is only in
    SDist form, so we can install with wheel into venv.
    """

    def __init__(self, construction_dir: ConstructionDir):
        self._construction_dir = construction_dir
        self._compressed_file_extractor = cft.CompressedFileExtractor()

    @property
    def _unpacked_src_dir_name(self):
        pkg_name = self._construction_dir.orig_pkg_name
        pkg_version = self._construction_dir.pypi_version
        return f"{pkg_name}-{pkg_version}"

    def _get_build_from_dist(self):
        try:
            build_from_dist = next(
                dist
                for dist in self._construction_dir.dists
                if isinstance(dist.dist_obj, pkginfo.sdist.SDist)
            )
        except StopIteration:
            raise ce.NoSDistForWheelConstruction(
                self._construction_dir.srepkg_root
            )

        return build_from_dist

    def build_wheel(self):

        build_from_dist = self._get_build_from_dist()

        with yu.yaspin_log_updater(
            msg=f"Converting {build_from_dist.path.name} to a wheel",
            logger=logging.getLogger(__name__),
        ) as updater:
            temp_unpack_dir_obj = tempfile.TemporaryDirectory()
            unpack_root = Path(temp_unpack_dir_obj.name)

            self._compressed_file_extractor.extract(
                build_from_dist.path, unpack_root
            )

            wheel_path = db.DistBuilder(
                distribution="wheel",
                source_dir=unpack_root / self._unpacked_src_dir_name,
                output_directory=self._construction_dir.orig_pkg_dists,
            ).build()

            temp_unpack_dir_obj.cleanup()

        completed_msg = f"\tBuilt wheel {wheel_path.name}"
        logging.getLogger(f"std_out.{__name__}").info(completed_msg)
