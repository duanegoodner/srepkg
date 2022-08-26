import abc
import sys

import build
import configparser
import shutil
import string
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, NamedTuple
from zipfile import ZIP_DEFLATED, ZipFile
import inner_pkg_installer.inner_pkg_installer as ipi
import srepkg.cs_entry_pts as cse
import srepkg.repackager_interfaces as re_int
import srepkg.repackager_data_structs as re_ds
import srepkg.srepkg_builder_int as sb_new_int


class SrcID(Enum):
    MANIFEST_TEMPLATE = auto()
    SREPKG_SETUP_CFG_STARTER = auto()
    SREPKG_BASE_SETUP_CFG = auto()
    SETUP_PY = auto()
    ENTRY_PT_TEMPLATE = auto()
    INNER_PKG_INSTALLER = auto()
    CMD_CLASS_CFG = auto()
    CMD_CLASSES = auto()


class DestID(Enum):
    CMD_CLASSES = auto()
    INNER_PKG_INSTALLER = auto()
    INNER_PKG_INSTALL_CFG = auto()
    MANIFEST = auto()
    SREPKG_BASE_SETUP_CFG = auto()
    SREPKG_SETUP_CFG = auto()
    SETUP_PY = auto()
    SREPKG_INIT = auto()
    SREPKG_ENTRY_PTS_DIR = auto()
    SREPKG_VENV = auto()


class SimpleCopyPair(NamedTuple):
    src: SrcID
    dst: DestID


class SrepkgCompleter(sb_new_int.SrepkgCompleterInterface):
    def __init__(self,
                 orig_pkg_summary: re_ds.ConstructionDirSummary):
        self._orig_pkg_summary = orig_pkg_summary

    @property
    @abc.abstractmethod
    def _gen_component_src_dir(self) -> Path:
        pass

    # @property
    # @abc.abstractmethod
    # def _orig_src_dist(self) -> Union[Path, None]:
    #     return

    @property
    def _gen_sources(self) -> Dict[SrcID, Path]:
        return {
            SrcID.MANIFEST_TEMPLATE:
                self._gen_component_src_dir / 'MANIFEST.in.template',
            SrcID.SETUP_PY: self._gen_component_src_dir / 'setup.py',
            SrcID.SREPKG_BASE_SETUP_CFG:
                self._orig_pkg_summary.srepkg_root / 'base_setup.cfg'
        }

    @property
    @abc.abstractmethod
    def _extra_sources(self) -> Dict[SrcID, Path]:
        pass

    @property
    def _all_sources(self):
        return {**self._gen_sources, **self._extra_sources}

    @property
    def _gen_dests(self):
        srepkg_root = self._orig_pkg_summary.srepkg_root
        return {
            DestID.SREPKG_SETUP_CFG: srepkg_root / 'setup.cfg',
            DestID.SETUP_PY: srepkg_root / 'setup.py',
            DestID.MANIFEST: srepkg_root / 'MANIFEST.in',
        }

    @property
    @abc.abstractmethod
    def _extra_dests(self) -> Dict[DestID, Path]:
        pass

    @property
    def _all_dests(self) -> Dict[DestID, Path]:
        return {**self._gen_dests, **self._extra_dests}

    @property
    @abc.abstractmethod
    def _simple_copy_pairs(self) -> List[SimpleCopyPair]:
        pass

    def _simple_copy_ops(self):
        for pair in self._simple_copy_pairs:
            shutil.copy2(
                src=self._all_sources[pair.src],
                dst=self._all_dests[pair.dst])

    @property
    @abc.abstractmethod
    def _srepkg_cfg_components(self) -> List[SrcID]:
        pass

    def _build_srepkg_cfg(self):
        config = configparser.ConfigParser()
        config.read([self._all_sources[src_id] for src_id in
                     self._srepkg_cfg_components])
        with self._all_dests[DestID.SREPKG_SETUP_CFG] \
                .open(mode="w") as cfg_file:
            config.write(cfg_file)

    def _build_manifest(self):
        with self._gen_sources[SrcID.MANIFEST_TEMPLATE].open(mode="r") as tf:
            template_text = tf.read()
        template = string.Template(template_text)
        result = template.substitute(
            {"srepkg_name": self._orig_pkg_summary.srepkg_name})
        with self._gen_dests[DestID.MANIFEST].open(mode="w") as manifest_file:
            manifest_file.write(result)

    @abc.abstractmethod
    def _adjust_base_pkg(self):
        pass

    @abc.abstractmethod
    def _build_srepkg_dist(self, output_dir: Path):
        pass

    def _restore_construction_dir_to(self, initial_contents: List[Path]):
        cur_dirs = [item for item in
                    list(self._orig_pkg_summary.srepkg_root.rglob('*')) if
                    item.is_dir()]

        for item in cur_dirs:
            if item not in initial_contents:
                shutil.rmtree(item, ignore_errors=True)

        cur_files = [item for item in
                     list(self._orig_pkg_summary.srepkg_root.rglob('*')) if
                     not item.is_dir()]

        for item in cur_files:
            if item not in initial_contents:
                item.unlink()

    def build_and_cleanup(self, output_dir: Path):
        initial_contents = list(self._orig_pkg_summary.srepkg_root.rglob('*'))
        self._adjust_base_pkg()
        self._build_srepkg_dist(output_dir=output_dir)
        self._restore_construction_dir_to(initial_contents)


class SrepkgSdistCompleter(SrepkgCompleter):

    @property
    def _gen_component_src_dir(self) -> Path:
        return Path(__file__).parent.absolute() / \
               'repackaging_components' / 'sdist_completer_components'

    # @property
    # def _orig_src_dist(self) -> Union[Path, None]:
    #     return self._construction_dir.construction_dir_summary.src_for_srepkg_sdist

    @property
    def _extra_sources(self) -> Dict[SrcID, Path]:
        ipi_sub_pkg = Path(__file__).parent.parent.absolute() / \
                      'inner_pkg_installer'
        return {
            SrcID.INNER_PKG_INSTALLER:
                ipi_sub_pkg / 'inner_pkg_installer.py',
            SrcID.CMD_CLASSES: ipi_sub_pkg / 'cmd_classes.py',
            SrcID.CMD_CLASS_CFG: ipi_sub_pkg / 'cmd_class.cfg'
        }

    @property
    def _extra_dests(self) -> Dict[DestID, Path]:
        srepkg_root = self._orig_pkg_summary.srepkg_root
        return {
            DestID.INNER_PKG_INSTALLER:
                srepkg_root / 'inner_pkg_installer.py',
            DestID.INNER_PKG_INSTALL_CFG:
                srepkg_root / 'inner_pkg_install.cfg',
            DestID.CMD_CLASSES: srepkg_root / 'cmd_classes.py'
        }

    @property
    def _simple_copy_pairs(self) -> List[SimpleCopyPair]:
        return [
            SimpleCopyPair(
                src=SrcID.SETUP_PY,
                dst=DestID.SETUP_PY),
            SimpleCopyPair(
                src=SrcID.INNER_PKG_INSTALLER,
                dst=DestID.INNER_PKG_INSTALLER),
            SimpleCopyPair(
                src=SrcID.CMD_CLASSES,
                dst=DestID.CMD_CLASSES)
        ]

    @property
    def _srepkg_cfg_components(self) -> List[SrcID]:
        return [SrcID.SREPKG_BASE_SETUP_CFG, SrcID.CMD_CLASS_CFG]

    def _build_inner_pkg_install_cfg(self):

        metadata = {
            "srepkg_name": self._orig_pkg_summary.srepkg_name,
            "dist_dir": "orig_dist",
            "sdist_src": self._orig_pkg_summary.src_for_srepkg_sdist.name
        }

        ipi_config = configparser.ConfigParser()
        ipi_config.add_section("metadata")

        for (key, value) in metadata.items():
            ipi_config.set("metadata", key, value)

        with self._all_dests[DestID.INNER_PKG_INSTALL_CFG] \
                .open(mode="w") as ipi_cfg_file:
            ipi_config.write(ipi_cfg_file)

    def _adjust_base_pkg(self):
        self._simple_copy_ops()
        self._build_manifest()
        self._build_srepkg_cfg()
        self._build_inner_pkg_install_cfg()

    @staticmethod
    def zip_dir(zip_name: str, src_path: Path, exclude_paths: List[Path]):
        with ZipFile(zip_name, 'w', ZIP_DEFLATED) as zf:
            for file in list(src_path.rglob('*')):
                if file not in exclude_paths:
                    zf.write(file, file.relative_to(src_path.parent))

    def _build_srepkg_dist(self, output_dir: Path):
        exclude_paths = list(
            (self._orig_pkg_summary.srepkg_root / 'orig_dist').iterdir())
        exclude_paths.remove(self._orig_pkg_summary.src_for_srepkg_sdist)

        output_filename = \
            f"{self._orig_pkg_summary.srepkg_name}-" \
            f"{self._orig_pkg_summary.pkg_version}.zip"

        self.zip_dir(zip_name=str(output_dir / output_filename),
                     src_path=self._orig_pkg_summary.srepkg_root,
                     exclude_paths=exclude_paths)


class SrepkgWheelCompleter(SrepkgCompleter):

    @property
    def _gen_component_src_dir(self) -> Path:
        return Path(__file__).parent.absolute() / \
               'repackaging_components' / 'wheel_completer_components'

    # @property
    # def _orig_src_dist(self) -> Union[Path, None]:
    #     return self._construction_dir.construction_dir_summary.src_for_srepkg_wheel

    @property
    def _extra_sources(self):
        return {
            SrcID.CMD_CLASSES: self._gen_component_src_dir / 'cmd_classes.py',
            SrcID.CMD_CLASS_CFG: self._gen_component_src_dir / 'cmd_class.cfg'
        }

    @property
    def _extra_dests(self) -> Dict[DestID, Path]:
        return {
            DestID.SREPKG_VENV: self._orig_pkg_summary.srepkg_inner /
            'srepkg_venv',
            DestID.CMD_CLASSES: self._orig_pkg_summary.srepkg_root /
            'cmd_classes.py'
        }

    @property
    def _simple_copy_pairs(self):
        return [
            SimpleCopyPair(
                src=SrcID.SETUP_PY,
                dst=DestID.SETUP_PY),
            SimpleCopyPair(
                src=SrcID.CMD_CLASSES,
                dst=DestID.CMD_CLASSES)
        ]

    @property
    def _srepkg_cfg_components(self) -> List[SrcID]:
        return [SrcID.SREPKG_BASE_SETUP_CFG, SrcID.CMD_CLASS_CFG]

    def _install_inner_pkg(self):
        ipi.InnerPkgInstaller(
            venv_path=self._all_dests[DestID.SREPKG_VENV],
            orig_pkg_dist=self._orig_pkg_summary.src_for_srepkg_wheel
        ).iso_install_inner_pkg()

    def _build_srepkg_dist(self, output_dir: Path):
        dist_builder = build.ProjectBuilder(
            srcdir=self._orig_pkg_summary.srepkg_root,
            python_executable=sys.executable)

        dist_builder.build(
            distribution='wheel',
            output_directory=str(output_dir)
        )

    def _adjust_base_pkg(self):
        self._simple_copy_ops()
        self._build_manifest()
        self._build_srepkg_cfg()
        self._install_inner_pkg()


class SrepkgBuilder(re_int.SrepkgBuilderInterface):

    def __init__(
            self,
            construction_dir_summary: re_ds.ConstructionDirSummary,
            output_dir: Path,
            srepkg_completers: List[SrepkgCompleter] = None
    ):
        if srepkg_completers is None:
            srepkg_completers = []
        self._srepkg_completers = srepkg_completers
        # self._construction_dir = construction_dir
        self._construction_dir_summary = construction_dir_summary
        self._output_dir = output_dir
        self._base_setup_cfg = configparser.ConfigParser()
        self._base_setup_cfg.read(
            self._sources[SrcID.SREPKG_SETUP_CFG_STARTER])

    @property
    def _sources(self):
        return {
            SrcID.SREPKG_SETUP_CFG_STARTER:
                Path(__file__).parent / 'repackaging_components' /
                'base_components' / 'starter_setup.cfg',
            SrcID.ENTRY_PT_TEMPLATE:
                Path(__file__).parent / 'repackaging_components' /
                'base_components' / 'generic_entry.py'
        }

    @property
    def _destinations(self):
        return {
            DestID.SREPKG_BASE_SETUP_CFG:
                self._construction_dir_summary.srepkg_root / 'base_setup.cfg',
            DestID.SREPKG_INIT:
                self._construction_dir_summary.srepkg_inner / '__init__.py',
            DestID.SREPKG_ENTRY_PTS_DIR:
                self._construction_dir_summary.srepkg_inner / 'srepkg_entry_points',
        }

    def _simple_construction_tasks(self):
        self._destinations[DestID.SREPKG_ENTRY_PTS_DIR].mkdir()
        self._destinations[DestID.SREPKG_INIT].touch()

        return self

    def _build_entry_points(self):
        cse.EntryPointsBuilder(
            orig_pkg_entry_pts=self._construction_dir_summary.entry_pts,
            entry_pt_template=self._sources[
                SrcID.ENTRY_PT_TEMPLATE],
            srepkg_entry_pt_dir=self._destinations[
                DestID.SREPKG_ENTRY_PTS_DIR],
            srepkg_name=self._construction_dir_summary.srepkg_inner.name,
            srepkg_config=self._base_setup_cfg,
            generic_entry_funct_name='entry_funct'
        ).build_entry_pts()

        return self

    def _write_srepkg_cfg_non_entry_data(self):
        metadata = {
            "name": self._construction_dir_summary.srepkg_name,
            "version": self._construction_dir_summary.pkg_version
        }

        for (key, value) in metadata.items():
            self._base_setup_cfg.set("metadata", key, value)

        return self

    def _build_base_setup_cfg(self):
        with self._destinations[DestID.SREPKG_BASE_SETUP_CFG] \
                .open(mode="w") as cfg_file:
            self._base_setup_cfg.write(cfg_file)

        return self

    def build(self):
        self._simple_construction_tasks() \
            ._build_entry_points() \
            ._write_srepkg_cfg_non_entry_data() \
            ._build_base_setup_cfg()

        for completer in self._srepkg_completers:
            completer.build_and_cleanup(self._output_dir)

        # self._construction_dir.settle()
