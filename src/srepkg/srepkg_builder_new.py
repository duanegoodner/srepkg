import abc
import configparser
import shutil
import string
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import srepkg.cs_entry_pts as cse
import srepkg.repackager_new_interfaces as re_new_int
import srepkg.srepkg_builder_new_ds_and_int as sb_new_int
# import \
#     srepkg.repackaging_components_new.partially_built.generic_entry as entry_funct


class SrcID(Enum):
    SREPKG_ROOT = auto()
    SREPKG_INNER = auto()
    MANIFEST_TEMPLATE = auto()
    SREPKG_SETUP_CFG_STARTER = auto()
    ENTRY_PT_TEMPLATE = auto()


class DestinationID(Enum):
    SREPKG_ROOT = auto()
    INNER_PKG_INSTALL_CFG = auto()
    MANIFEST = auto()
    SREPKG_SETUP_CFG = auto()
    SREPKG_INNER = auto()
    SREPKG_INIT = auto()
    SREPKG_ENTRY_PTS_DIR = auto()
    SREPKG_ENTRY_POINTS_INIT = auto()


@dataclass
class SrepkgBuilderSources:
    repkg_components: Path

    @property
    def paths(self) -> dict[SrcID, Path]:
        return {
            SrcID.SREPKG_ROOT:
                self.repkg_components / 'srepkg_root',
            SrcID.SREPKG_INNER:
                self.repkg_components / 'srepkg_inner',
            SrcID.MANIFEST_TEMPLATE:
                self.repkg_components / 'partially_built' /
                'MANIFEST.in.template',
            SrcID.SREPKG_SETUP_CFG_STARTER:
                self.repkg_components / 'partially_built' / 'starter_setup.cfg',
            SrcID.ENTRY_PT_TEMPLATE:
                self.repkg_components / 'partially_built' / 'generic_entry.py'
        }


@dataclass
class SrepkgBuilderDestinations:
    srepkg_root: Path
    srepkg_inner: Path

    @property
    def paths(self) -> dict[DestinationID, Path]:
        return {
            DestinationID.SREPKG_ROOT:
                self.srepkg_root,
            DestinationID.SREPKG_INNER:
                self.srepkg_inner,
            DestinationID.INNER_PKG_INSTALL_CFG:
                self.srepkg_root / 'inner_pkg_install.cfg',
            DestinationID.MANIFEST:
                self.srepkg_root / 'MANIFEST.in',
            DestinationID.SREPKG_SETUP_CFG:
                self.srepkg_root / 'setup.cfg',
            DestinationID.SREPKG_INIT:
                self.srepkg_inner / '__init__.py',
            DestinationID.SREPKG_ENTRY_PTS_DIR:
                self.srepkg_inner / 'srepkg_entry_points',
            DestinationID.SREPKG_ENTRY_POINTS_INIT:
                self.srepkg_inner / 'srepkg_entry_points/__init__.py'
        }


class SrepkgBuilder(re_new_int.SrepkgBuilderInterface):

    def __init__(self, construction_dir: sb_new_int.SrepkgComponentReceiver):
        self._construction_dir = construction_dir
        self._sources = SrepkgBuilderSources(
            repkg_components=Path(__file__).parent.absolute() /
                             'repackaging_components_new')
        self._destinations = SrepkgBuilderDestinations(
            srepkg_root=construction_dir.srepkg_root,
            srepkg_inner=construction_dir.srepkg_inner)
        self._srepkg_config = configparser.ConfigParser()
        self._srepkg_config.read(
            self._sources.paths[SrcID.SREPKG_SETUP_CFG_STARTER])

    @staticmethod
    def _copy_contents_to_existing_dir(src: Path, dest: Path):
        assert src.is_dir() and dest.is_dir()
        for item in src.iterdir():
            if item.is_dir():
                shutil.copytree(item, dest / item.name)
            else:
                shutil.copy2(item, dest)

    def _simple_construction_tasks(self):
        self._copy_contents_to_existing_dir(
            src=self._sources.paths[SrcID.SREPKG_INNER],
            dest=self._destinations.paths[DestinationID.SREPKG_INNER])
        self._copy_contents_to_existing_dir(
            src=self._sources.paths[SrcID.SREPKG_ROOT],
            dest=self._destinations.paths[DestinationID.SREPKG_ROOT])
        self._destinations.paths[DestinationID.SREPKG_INIT].touch()

        return self

    def _build_entry_points(self):
        cse.EntryPointsBuilder(
            orig_pkg_entry_pts=self._construction_dir
                .orig_pkg_src_summary.entry_pts,
            entry_pt_template=self._sources.paths[SrcID.ENTRY_PT_TEMPLATE],
            srepkg_entry_pt_dir=self._destinations
                .paths[DestinationID.SREPKG_ENTRY_PTS_DIR],
            srepkg_name=self._construction_dir.srepkg_inner.name,
            srepkg_config=self._srepkg_config,
            generic_entry_funct_name='entry_funct'
        ).build_entry_pts()

        return self

    def _write_srepkg_cfg_non_entry_data(self):
        self._srepkg_config.set(
            "metadata", "name", self._construction_dir.srepkg_name)
        self._srepkg_config.set("metadata", "version", self._construction_dir
                                .orig_pkg_src_summary.pkg_version)

        return self

    def _build_srepkg_cfg(self):
        with self._destinations.paths[DestinationID.SREPKG_SETUP_CFG].open(
                mode="w") as cfg_file:
            self._srepkg_config.write(cfg_file)

        return self

    def _build_inner_pkg_install_cfg(self):
        ipi_config = configparser.ConfigParser()
        ipi_config.add_section("metadata")
        ipi_config.set(
            "metadata", "srepkg_name", self._construction_dir.srepkg_name)
        ipi_config.set(
            "metadata", "sdist_src",
            self._construction_dir.orig_pkg_src_summary.wheel_path.name)
        # ipi_config.set(
        #     "metadata", "name", self._construction_dir.srepkg_inner.name)
        with self._destinations.paths[DestinationID.INNER_PKG_INSTALL_CFG] \
                .open(mode="w") as icf:
            ipi_config.write(icf)

        return self

    def _build_srepkg_manifest(self):
        with self._sources.paths[SrcID.MANIFEST_TEMPLATE].open(mode="r") as tf:
            template_text = tf.read()
        template = string.Template(template_text)
        result = template.substitute(
            {"srepkg_name": self._construction_dir.srepkg_name})
        with self._destinations.paths[DestinationID.MANIFEST] \
                .open(mode="w") as output_file:
            output_file.write(result)

        return self

    # change to a concrete method while developing build scheme(s)
    # @abc.abstractmethod
    def build(self):
        self._simple_construction_tasks() \
            ._build_entry_points() \
            ._write_srepkg_cfg_non_entry_data() \
            ._build_srepkg_cfg() \
            ._build_inner_pkg_install_cfg() \
            ._build_srepkg_manifest()


class WheelWheelBuilder(SrepkgBuilder):

    def build(self):
        pass


class SdistWheelBuilder(SrepkgBuilder):

    def build(self):
        pass


class SdistSdistBuilder(SrepkgBuilder):

    def build(self):
        pass
