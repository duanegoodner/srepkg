"""
Contains the SrepkgBuilder class that creates a copy of the original package
and wraps the copied package with a file structure that forces it to run as a
Srepkg.
"""
import abc
import configparser
import shutil
import string
import sys
from abc import ABC

from typing import List, Callable, NamedTuple
from pathlib import Path
from enum import Enum, auto

import srepkg.entry_points_builder as epb
import custom_datatypes.builder_src_paths as bsp
import custom_datatypes.builder_dest_paths as bdp
import custom_datatypes.named_tuples as nt


class SrepkbBuilderError(nt.ErrorMsg, Enum):
    OrigPkgPathNotFound = nt.ErrorMsg(
        msg="Original package path not found"
    )
    DestPkgPathExits = nt.ErrorMsg(
        msg="Intended Srepkg destination path already exists"
    )
    ControlComponentsNotFound = nt.ErrorMsg(
        msg="Error when attempting to copy sub-package "
            "srepkg_control_components. Sub-package not found"
    )
    ControlComponentsExist = nt.ErrorMsg(
        msg="Error when attempting to copy sub-package "
            "srepkg_control_components. Destination path already exists."
    )
    FileNotFoundForCopy = nt.ErrorMsg(
        msg="Error when attempting to copy. Source file not found."
    )
    CopyDestinationPathExists = nt.ErrorMsg(
        msg="Error when attempting to copy. Destination path already exists"
    )


class CopyInfo(NamedTuple):
    src: Path
    dest: Path


class TemplateFileWriter:
    def __init__(self, substitution_map: dict):
        self._substitution_map = substitution_map

    def write_file(self, template_file: Path, dest_path: Path):
        with template_file.open(mode="r") as tf:
            template_text = tf.read()
        template = string.Template(template_text)
        result = template.substitute(self._substitution_map)
        with dest_path.open(mode="w") as output_file:
            output_file.write(result)


class ConstructionTaskType(Enum):
    DIRECT_COPY_FILE: auto()
    DIRECT_COPY_DIR: auto()
    CALL_METHOD: auto()
    WRITE_FROM_TEMPLATE: auto()


class _ConstructionTask(abc.ABC):

    @abc.abstractmethod
    def execute(self):
        pass


class _Copy(_ConstructionTask, abc.ABC):
    def __init__(self, copy_info: CopyInfo):
        self._copy_info = copy_info

    @abc.abstractmethod
    def _copy_operation(self):
        pass

    def execute(self):
        try:
            self._copy_operation()
        except FileNotFoundError:
            print(
                f"Unable to find file when attempting to copy from"
                f"{str(self._copy_info.src)} to {str(self._copy_info.dest)}"
            )
            sys.exit(SrepkbBuilderError.FileNotFoundForCopy.msg)


class _DirectCopyDir(_Copy):
    def __init__(self, copy_info,
                 ignore_patterns: List[str] = None):
        super().__init__(copy_info)
        if ignore_patterns is None:
            ignore_patterns = []
        self._ignore_patterns = ignore_patterns

    def _copy_operation(self):
        shutil.copytree(self._copy_info.src, self._copy_info.dest,
                        ignore=shutil.ignore_patterns(*self._ignore_patterns),
                        dirs_exist_ok=True)


class _DirectCopyFile(_Copy):
    def __init__(self, copy_info: CopyInfo):
        super().__init__(copy_info)

    def _copy_operation(self):
        shutil.copy2(self._copy_info.src, self._copy_info.dest)


class _WriteFromTemplate(_Copy):
    def __init__(self, copy_info: CopyInfo, substitution_map: dict):
        super().__init__(copy_info)
        self._substitution_map = substitution_map

    def _copy_operation(self):
        with self._copy_info.src.open(mode="r") as tf:
            template_text = tf.read()
        template = string.Template(template_text)
        result = template.substitute(self._substitution_map)
        with self._copy_info.dest.open(mode="w") as output_file:
            output_file.write(result)


class _CallMethod(_ConstructionTask):
    def __init__(self, call_method: callable):
        self._call_method = call_method

    def execute(self):
        self._call_method()


class _TaskListBuilder(abc.ABC):

    @abc.abstractmethod
    def build_task_list(self) -> List[_ConstructionTask]:
        pass


class SrepkgTaskListBuilder(_TaskListBuilder):

    def __init__(self, orig_pkg_info: nt.OrigPkgInfo,
                 src_paths: bsp.BuilderSrcPaths,
                 repkg_paths: bdp.BuilderDestPaths,
                 info: nt.SrepkgTaskListBuilderInfo,
                 dist_out_dir: Path):
        self._orig_pkg_info = orig_pkg_info
        self._src_paths = src_paths
        self._repkg_paths = repkg_paths
        self._info = info
        # self._dist_out_dir = dist_out_dir

    @property
    def _direct_file_copy_info(self):
        return {
            'entry_module': CopyInfo(
                src=self._info.src_paths.entry_module,
                dest=self._info.repkg_paths.entry_module
            ),
            'inner_pkg_installer': CopyInfo(
                src=self._info.src_paths.inner_pkg_installer,
                dest=self._info.repkg_paths.inner_pkg_installer
            ),
            'srepkg_setup_py': CopyInfo(
                src=self._info.src_paths.srepkg_setup_py,
                dest=self._info.repkg_paths.srepkg_setup_py
            )
        }

    def _create_srepkg_init(self):
        with self._info.repkg_paths.srepkg_init.open(mode='a'):
            pass

    def _build_entry_pts(self):
        epb.EntryPointsBuilder.from_srepkg_builder_init_args(
            orig_pkg_info=self._orig_pkg_info,
            src_paths=self._src_paths,
            repkg_paths=self._repkg_paths
        ).build_entry_pts()

    @property
    def _create_srepkg_init_task(self):
        return _CallMethod(self._create_srepkg_init)

    def _build_entry_points(self):
        epb.EntryPointsBuilder.from_srepkg_builder_init_args(
            orig_pkg_info=self._orig_pkg_info,
            src_paths=self._src_paths,
            repkg_paths=self._repkg_paths
        ).build_entry_pts()

    @property
    def _build_entry_points_task(self):
        return _CallMethod(self._build_entry_points)

    @property
    def _copy_entry_pt_runner(self):
        return _DirectCopyFile(
            CopyInfo(src=self._src_paths.entry_module,
                     dest=self._repkg_paths.entry_module))

    def build_task_list(self) -> List[_ConstructionTask]:
        return [
            self._copy_inner_pkg_task,
            self._create_srepkg_init_task,
            self._build_entry_points_task,
            self._copy_entry_pt_runner,


        ]


class SrepkgBuilder:
    """
    Encapsulates  methods for creating a SRE-packaged version of an existing
    package.
    """

    _build_errors = SrepkbBuilderError

    # file patterns that are not copied into the SRE-packaged app
    _ignore_types = ["*.git", "*.gitignore", "*.idea", "*__pycache__"]

    def __init__(
            self,
            orig_pkg_info: nt.OrigPkgInfo,
            src_paths: bsp.BuilderSrcPaths,
            repkg_paths: bdp.BuilderDestPaths,
            dist_out_dir: Path,
    ):
        """
        Construct a new SrepkgBuilder
        :param src_paths: BuilderSrcPaths namedtuple
        :param repkg_paths: BuilderDestPaths named tuple
        module
        """
        self._orig_pkg_info = orig_pkg_info
        self._src_paths = src_paths
        self._repkg_paths = repkg_paths
        self._template_file_writer = TemplateFileWriter(
            substitution_map={
                "srepkg_name": self._repkg_paths.srepkg.name,
            }
        )
        self._entry_points_builder = (
            epb.EntryPointsBuilder.from_srepkg_builder_init_args(
                orig_pkg_info=orig_pkg_info,
                src_paths=src_paths,
                repkg_paths=repkg_paths,
            )
        )
        self._dist_out_dir = dist_out_dir

    @property
    def orig_pkg_info(self):
        return self._orig_pkg_info

    @property
    def src_paths(self):
        return self._src_paths

    @property
    def repkg_paths(self):
        return self._repkg_paths

    def copy_inner_package(self):
        """Copies original package to SRE-package directory"""

        try:
            shutil.copytree(
                self._orig_pkg_info.root_path,
                self._repkg_paths.srepkg,
                ignore=shutil.ignore_patterns(*self._ignore_types),
            )
        except FileNotFoundError:
            sys.exit(self._build_errors.OrigPkgPathNotFound.msg)
        except FileExistsError:
            sys.exit(self._build_errors.DestPkgPathExits.msg)

    def build_srepkg_cfg(self):
        sr_config = configparser.ConfigParser()
        sr_config.read(self._src_paths.srepkg_setup_cfg)

        sr_config["options.entry_points"][
            "console_scripts"
        ] = self._entry_points_builder.get_cfg_cse_str()

        sr_config["metadata"]["name"] = self._repkg_paths.srepkg.name

        sr_config["metadata"]["version"] = self._orig_pkg_info.version

        with open(self._repkg_paths.srepkg_setup_cfg, "w") as sr_configfile:
            sr_config.write(sr_configfile)

    def build_inner_pkg_install_cfg(self):
        ipi_config = configparser.ConfigParser()
        ipi_config.add_section("metadata")
        ipi_config.set("metadata", "name", self._repkg_paths.srepkg.name)
        # ipi_config["metadata"]["name"] = self._repkg_paths.srepkg.name
        with open(self._repkg_paths.inner_pkg_install_cfg, 'w') \
                as ipi_config_file:
            ipi_config.write(ipi_config_file)

    def create_srepkg_init(self):
        with self._repkg_paths.srepkg_init.open(mode='a'):
            pass

    def write_entry_point_file(self, orig_cse: nt.CSEntryPt):

        shutil.copy2(
            self._src_paths.entry_point_template,
            self._repkg_paths.srepkg_entry_points / (orig_cse.command + ".py"),
        )

    def simple_file_copy(self, src_dest: CopyInfo):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(*src_dest)
        except FileNotFoundError:
            print(
                f"Unable to find file when attempting to copy from"
                f"{str(src_dest.src)} to {str(src_dest.dest)}"
            )
            sys.exit(self._build_errors.FileNotFoundForCopy.msg)
        except FileExistsError:
            print(f"File already exists at {str(src_dest.src)}.")
            sys.exit(self._build_errors.CopyDestinationPathExists.msg)

    def inh_build(self):

        SrePkgConstructionTask(
            ConstructionTaskType.DIRECT_COPY_DIR,
            src_path=self._orig_pkg_info.root_path,
            dest_path=self._repkg_paths.srepkg,
            not_found_response=self._build_errors.OrigPkgPathNotFound.msg,
            ignore=shutil.ignore_patterns(*self._ignore_types)
        ).execute()

        SrePkgConstructionTask(
            ConstructionTaskType.CALL_METHOD,
            call_method=self.create_srepkg_init
        ).execute()

        SrePkgConstructionTask(
            ConstructionTaskType.CALL_METHOD,
            call_method=self._entry_points_builder.build_entry_pts,
        )

    def build_srepkg_layer(
            self,
            call_methods: List[Callable] = None,
            direct_copy_files: List[CopyInfo] = None,
            template_file_writes: List[CopyInfo] = None,
    ):

        if call_methods is not None:
            for method in call_methods:
                method()

        if direct_copy_files is not None:
            for direct_copy_pair in direct_copy_files:
                self.simple_file_copy(direct_copy_pair)

        if template_file_writes is not None:
            for write_op in template_file_writes:
                self._template_file_writer.write_file(*write_op)

    def build_inner_layer(self):
        self.build_srepkg_layer(call_methods=[self.copy_inner_package])

    def build_mid_layer(self):
        self.build_srepkg_layer(
            call_methods=[
                self._entry_points_builder.build_entry_pts,
                self.create_srepkg_init
            ],
            direct_copy_files=[
                CopyInfo(
                    src=self._src_paths.entry_module,
                    dest=self._repkg_paths.entry_module
                )
            ],
        )

    def build_outer_layer(self):
        self.build_srepkg_layer(
            call_methods=[
                self.build_srepkg_cfg, self.build_inner_pkg_install_cfg],
            direct_copy_files=[
                CopyInfo(
                    src=self._src_paths.inner_pkg_installer,
                    dest=self._repkg_paths.inner_pkg_installer,
                ),
                CopyInfo(
                    src=self._src_paths.srepkg_setup_py,
                    dest=self._repkg_paths.srepkg_setup_py,
                ),
            ],
            template_file_writes=[
                CopyInfo(
                    src=self._src_paths.manifest_template,
                    dest=self._repkg_paths.manifest,
                ),
            ],
        )

    def build_distribution(self):

        zipfile_name = "-".join(
            [self._repkg_paths.srepkg.name, self._orig_pkg_info.version]
        )

        shutil.make_archive(
            base_name=str(self._dist_out_dir / zipfile_name),
            format="zip",
            root_dir=str(self._repkg_paths.srepkg.parent.absolute()),
        )

        return zipfile_name

    def output_summary(self, archive_filename: str):
        print(
            f"Original package '{self._orig_pkg_info.pkg_name}' has been "
            f"re-packaged as '{self._repkg_paths.srepkg.name}'\n"
        )
        print(
            f"The re-packaged version has been saved as source "
            f"distribution archive file: "
            f'{str(self._dist_out_dir) + "/" + archive_filename}'
        )
        print(
            f"'{self._repkg_paths.srepkg.name}' can be installed using: "
            f"pip install "
            f'{str(self._dist_out_dir) + "/" + archive_filename}\n'
        )
        print(
            f"After installation, '{self._repkg_paths.srepkg.name}' will "
            f"provide command line access to the following commands:"
        )
        for cse in self._orig_pkg_info.entry_pts:
            print(cse.command)

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """

        self.build_inner_layer()
        self.build_mid_layer()
        self.build_outer_layer()
        archive = self.build_distribution()
        self.output_summary(archive)
