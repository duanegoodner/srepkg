"""
Contains classes responsible for building sdist and/or wheel from the venv
(happens after original package has been installed in venv)
"""

import abc
import configparser
import logging
import shutil
import string
from dataclasses import dataclass
from pathlib import Path
import tarfile
import tempfile
from typing import Callable, List, NamedTuple
from zipfile import ZIP_DEFLATED, ZipFile

import inner_pkg_installer.inner_pkg_installer as ipi
import inner_pkg_installer.yaspin_updater as yu
import srepkg.cs_entry_pts as cse
import srepkg.dist_builder as db
import srepkg.repackager_data_structs as re_ds
import srepkg.repackager_interfaces as re_int


class TemplateWriteOp(NamedTuple):
    src_filename: str
    dest_filename: str
    replacement_map: dict


class SrepkgDistWriter(abc.ABC):
    """
    Interface with method for creating a distribution of a SRE package.
    """

    def __init__(
        self,
        orig_pkg_summary: re_ds.ConstructionDirSummary,
        dist_out_dir: Path,
    ):
        self._orig_pkg_summary = orig_pkg_summary
        self._dist_out_dir = dist_out_dir

    @abc.abstractmethod
    def write_dist(self) -> str:
        pass


class SrepkgSdistWriter(SrepkgDistWriter):
    """
    Creates a source distribution of SRE package.
    """

    @property
    def src_path(self) -> Path:
        return self._orig_pkg_summary.srepkg_root

    @property
    def exclude_paths(self) -> List[Path]:
        return [
            item
            for item in list((self.src_path / "orig_dist").iterdir())
            if item != self._orig_pkg_summary.src_for_srepkg_sdist
        ]

    @property
    def files_to_copy(self) -> List[Path]:
        return [
            path
            for path in list(self.src_path.rglob("*"))
            if path not in self.exclude_paths
        ]

    # Not needed; using .tar.gz for sdist
    # def write_to_zip(self, zip_name: str):
    #     with ZipFile(zip_name, "w", ZIP_DEFLATED) as zf:
    #         for file in self.files_to_copy:
    #             zf.write(file, file.relative_to(self.src_path.parent))

    def write_to_tar_gz(self, tar_gz_path: Path):
        with tarfile.open(tar_gz_path, "w:gz") as tar:
            for file in self.files_to_copy:
                tar.add(file, arcname=file.relative_to(self.src_path.parent))

    def write_dist(self):
        with yu.yaspin_log_updater(
            msg="Building srepkg sdist", logger=logging.getLogger(__name__)
        ):

            tar_filename = (
                f"{self._orig_pkg_summary.srepkg_name}-"
                f"{self._orig_pkg_summary.pkg_version}.tar.gz"
            )

            tar_sdist_path = self._dist_out_dir / tar_filename
            self.write_to_tar_gz(tar_gz_path=tar_sdist_path)

        logging.getLogger(f"std_out.{__name__}").info(
            f"\t{self._orig_pkg_summary.srepkg_name} sdist saved as: "
            f"{str(tar_sdist_path)}"
        )
        return str(tar_sdist_path)


class SrepkgWheelWriter(SrepkgDistWriter):
    """
    Creates a wheel distribution of SRE package.
    """

    def write_dist(self):
        with yu.yaspin_log_updater(
            msg="Building srepkg wheel", logger=logging.getLogger(__name__)
        ) as updater:
            wheel_path = db.DistBuilder(
                distribution="wheel",
                source_dir=self._orig_pkg_summary.srepkg_root,
                output_directory=self._dist_out_dir,
            ).build()

        logging.getLogger(f"std_out.{__name__}").info(
            f"\t{self._orig_pkg_summary.srepkg_name} wheel saved as: {wheel_path}"
        )

        return wheel_path


@dataclass
class CompleterProperties:
    components_dir: Path
    templates_dir: Path
    dist_writer_type: Callable[..., SrepkgDistWriter]


class SrepkgCompleter(abc.ABC):
    """
    Interface (with many concrete methods) for handling file copying and
    modification to prepare of dist creation, and creating distribution.
    """

    def __init__(
        self,
        orig_pkg_summary: re_ds.ConstructionDirSummary,
        dist_out_dir: Path,
        repkg_components: Path = Path(__file__).parent.absolute()
        / "repackaging_components",
    ):
        self._orig_pkg_summary = orig_pkg_summary
        self._dist_out_dir = dist_out_dir
        self._repkg_components = repkg_components

    @property
    @abc.abstractmethod
    def _props(self) -> CompleterProperties:
        pass

    @property
    def _dist_writer(self) -> SrepkgDistWriter:
        return self._props.dist_writer_type(
            orig_pkg_summary=self._orig_pkg_summary,
            dist_out_dir=self._dist_out_dir,
        )

    @property
    def _template_write_ops(self) -> List[TemplateWriteOp]:
        return [
            TemplateWriteOp(
                src_filename="MANIFEST.in.template",
                dest_filename="MANIFEST.in",
                replacement_map={
                    "srepkg_name": self._orig_pkg_summary.srepkg_name
                },
            )
        ]

    def _copy_ready_components(self):
        for item in self._props.components_dir.iterdir():
            if item.is_dir():
                shutil.copytree(
                    item, self._orig_pkg_summary.srepkg_root / item.name
                )
            else:
                shutil.copy2(item, self._orig_pkg_summary.srepkg_root)

    def _write_from_templates(self):
        for item in self._template_write_ops:
            with (self._props.templates_dir / item.src_filename).open(
                mode="r"
            ) as t:
                template_text = t.read()
            template = string.Template(template_text)
            result = template.substitute(item.replacement_map)
            with (
                self._orig_pkg_summary.srepkg_root / item.dest_filename
            ).open(mode="w") as f:
                f.write(result)

    @property
    def _srepkg_cfg_components(self) -> List[Path]:
        return [
            self._orig_pkg_summary.srepkg_root / "base_setup.cfg",
            self._props.templates_dir / "cmd_class.cfg",
        ]

    def _write_srepkg_setup_cfg(self):
        config = configparser.ConfigParser()
        config.read(src_path for src_path in self._srepkg_cfg_components)
        with (self._orig_pkg_summary.srepkg_root / "setup.cfg").open(
            mode="w"
        ) as cfg_file:
            config.write(cfg_file)

    def _restore_construction_dir_to(self, initial_contents: List[Path]):
        cur_dirs = [
            item
            for item in list(self._orig_pkg_summary.srepkg_root.rglob("*"))
            if item.is_dir()
        ]

        for item in cur_dirs:
            if item not in initial_contents:
                shutil.rmtree(item, ignore_errors=True)

        cur_files = [
            item
            for item in list(self._orig_pkg_summary.srepkg_root.rglob("*"))
            if not item.is_dir()
        ]

        for item in cur_files:
            if item not in initial_contents:
                item.unlink()

    @abc.abstractmethod
    def _extra_construction_tasks(self):
        pass

    def _write_dist(self):
        return self._dist_writer.write_dist()

    def build_and_cleanup(self) -> str:
        """
        Builds distribution and cleans up directory used for dist building.
        Returns: Path to the created distribution.
        """
        initial_contents = list(self._orig_pkg_summary.srepkg_root.rglob("*"))
        self._copy_ready_components()
        self._write_from_templates()
        self._write_srepkg_setup_cfg()
        self._extra_construction_tasks()
        dist_path = self._write_dist()
        self._restore_construction_dir_to(initial_contents)

        return dist_path


class SrepkgWheelCompleter(SrepkgCompleter):
    """
    Completes construction of a wheel distribution.
    """

    @property
    def _props(self) -> CompleterProperties:
        return CompleterProperties(
            components_dir=self._repkg_components
            / "wheel_completer_components",
            dist_writer_type=SrepkgWheelWriter,
            templates_dir=self._repkg_components / "wheel_completer_templates",
        )

    def _install_inner_pkg(self):
        ipi.InnerPkgInstaller(
            venv_path=self._orig_pkg_summary.srepkg_inner / "srepkg_venv",
            orig_pkg_dist=self._orig_pkg_summary.src_for_srepkg_wheel,
        ).iso_install_inner_pkg()

    def _extra_construction_tasks(self):
        self._install_inner_pkg()


class SrepkgSdistCompleter(SrepkgCompleter):
    """
    Completes construction of a sdist distribution.
    """

    @property
    def _props(self) -> CompleterProperties:
        return CompleterProperties(
            components_dir=self._repkg_components
            / "sdist_completer_components",
            dist_writer_type=SrepkgSdistWriter,
            templates_dir=self._repkg_components / "sdist_completer_templates",
        )

    def _build_ipi_cfg(self):
        metadata = {
            "srepkg_name": self._orig_pkg_summary.srepkg_name,
            "dist_dir": "orig_dist",
            "sdist_src": self._orig_pkg_summary.src_for_srepkg_sdist.name,
        }

        ipi_config = configparser.ConfigParser()
        ipi_config.add_section("metadata")

        for key, value in metadata.items():
            ipi_config.set("metadata", key, value)

        with (
            self._orig_pkg_summary.srepkg_root / "inner_pkg_install.cfg"
        ).open(mode="w") as ipi_cfg_file:
            ipi_config.write(ipi_cfg_file)

    def _extra_construction_tasks(self):
        self._build_ipi_cfg()


class SrepkgBuilder(re_int.SrepkgBuilderInterface):
    """
    Builds sdist and wheel distribution of SRE package and output file and entry-point
    info to terminal.
    """

    def __init__(
        self,
        construction_dir_summary: re_ds.ConstructionDirSummary,
        output_dir: Path,
        srepkg_completers: List[SrepkgCompleter] = None,
    ):
        if srepkg_completers is None:
            srepkg_completers = []
        self._srepkg_completers = srepkg_completers
        self._construction_dir_summary = construction_dir_summary
        self._output_dir = output_dir
        self._base_setup_cfg = configparser.ConfigParser()
        self._base_setup_cfg.read(
            Path(__file__).parent
            / "repackaging_components"
            / "base_templates"
            / "base_setup.cfg"
        )

    def _simple_construction_tasks(self):
        (
            self._construction_dir_summary.srepkg_inner / "srepkg_entry_points"
        ).mkdir()
        (self._construction_dir_summary.srepkg_inner / "__init__.py").touch()

        return self

    def _build_entry_points(self):
        cse.EntryPointsBuilder(
            orig_pkg_entry_pts=self._construction_dir_summary.entry_pts,
            entry_pt_template=Path(__file__).parent
            / "repackaging_components"
            / "base_templates"
            / "generic_entry.py",
            srepkg_entry_pt_dir=self._construction_dir_summary.srepkg_inner
            / "srepkg_entry_points",
            srepkg_name=self._construction_dir_summary.srepkg_inner.name,
            srepkg_config=self._base_setup_cfg,
            generic_entry_funct_name="entry_funct",
        ).build_entry_pts()

        return self

    def _write_srepkg_cfg_non_entry_data(self):
        metadata = {
            "name": self._construction_dir_summary.srepkg_name,
            "version": self._construction_dir_summary.pkg_version,
        }

        for key, value in metadata.items():
            self._base_setup_cfg.set("metadata", key, value)

        return self

    def _build_base_setup_cfg(self):
        with (
            self._construction_dir_summary.srepkg_root / "base_setup.cfg"
        ).open(mode="w") as cfg_file:
            self._base_setup_cfg.write(cfg_file)

        return self

    def _build_srepkg_base(self):
        self._simple_construction_tasks()
        self._build_entry_points()
        self._write_srepkg_cfg_non_entry_data()
        self._build_base_setup_cfg()

    def _complete_dists(self):
        dist_paths = []

        for completer in self._srepkg_completers:
            dist_paths.append(completer.build_and_cleanup())

        return dist_paths

    def build(self):
        self._build_srepkg_base()
        dist_paths = self._complete_dists()

        entry_pts_message = "\n".join(
            [
                f"\t• {entry_point.command}"
                for entry_point in self._construction_dir_summary.entry_pts.cs_entry_pts
            ]
        )

        qualifier = (
            "either of the following commands:"
            if len(self._srepkg_completers) == 2
            else "the command:"
        )

        commands = "\n".join(
            [f"\t• pip install {dist_path}" for dist_path in dist_paths]
        )

        logging.getLogger(f"std_out.{__name__}").info(
            f"\n{self._construction_dir_summary.srepkg_name} can be installed "
            f"using {qualifier}\n{commands}"
            f"\nUpon installation, {self._construction_dir_summary.srepkg_name} "
            f"will provide access to the following command line entry points: "
            f"\n{entry_pts_message}"
        )
