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
from pathlib import Path
from typing import List, NamedTuple
import srepkg.entry_points_builder as epb
import srepkg.shared_data_structures.named_tuples as nt
from srepkg.error_handling.error_messages import SrepkgBuilderError


class CopyInfo(NamedTuple):
    src: Path
    dest: Path


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
            sys.exit(SrepkgBuilderError.FileNotFoundForCopy.msg)


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


class TaskCatalog:

    def __init__(self, info: nt.TaskBuilderInfo):
        self._info = info
        self._entry_points_builder = epb.EntryPointsBuilder \
            .for_srepkg_task_list_builder(self._info)

    def build_srepkg_cfg(self):
        srepkg_cfg = configparser.ConfigParser()
        srepkg_cfg.read(self._info.src_paths.srepkg_setup_cfg)
        srepkg_cfg.set("options.entry_points", "console_scripts",
                       self._entry_points_builder.get_cfg_cse_str())
        srepkg_cfg.set("metadata", "name", self._info.repkg_paths.srepkg.name)
        srepkg_cfg.set("metadata", "version", self._info.orig_pkg_info.version)

        with open(self._info.repkg_paths.srepkg_setup_cfg, "w") as sr_cfg_file:
            srepkg_cfg.write(sr_cfg_file)

    def build_inner_pkg_install_cfg(self):
        ipi_config = configparser.ConfigParser()
        ipi_config.add_section("metadata")
        ipi_config.set("metadata", "name", self._info.repkg_paths.srepkg.name)
        with open(self._info.repkg_paths.inner_pkg_install_cfg, 'w') as icf:
            ipi_config.write(icf)

    def create_srepkg_init(self):
        with self._info.repkg_paths.srepkg_init.open(mode='a'):
            pass

    def build_entry_pts(self):
        self._entry_points_builder.build_entry_pts()

    def build_distribution(self):
        zipfile_name = "-".join(
            [
                self._info.repkg_paths.srepkg.name,
                self._info.orig_pkg_info.version
            ]
        )

        shutil.make_archive(
            base_name=str(self._info.dist_out_dir / zipfile_name),
            format="zip",
            root_dir=str(self._info.repkg_paths.srepkg.parent.absolute())
        )

        print(
            f"Original package '{self._info.orig_pkg_info.pkg_name}' has been "
            f"re-packaged as '{self._info.repkg_paths.srepkg.name}'\n"
        )

        print(
            f"The re-packaged version has been saved as source "
            f"distribution archive file: "
            f'{str(self._info.dist_out_dir) + "/" + zipfile_name}'
        )

        print(
            f"'{self._info.repkg_paths.srepkg.name}' can be installed using: "
            f"pip install "
            f'{str(self._info.dist_out_dir) + "/" + zipfile_name}\n'
        )

        print(
            f"After installation, '{self._info.repkg_paths.srepkg.name}' will "
            f"provide command line access to the following commands:"
        )
        for cse in self._info.orig_pkg_info.entry_pts:
            print(cse.command)

    @property
    def task_catalog(self):
        return {
            'copy_inner_pkg': _DirectCopyDir(
                CopyInfo(
                    src=self._info.orig_pkg_info.root_path,
                    dest=self._info.repkg_paths.srepkg
                ),
                ignore_patterns=[
                    "*.git", "*.gitignore", "*.idea", "*__pycache__"]
            ),
            'copy_entry_module': _DirectCopyFile(
                CopyInfo(
                    src=self._info.src_paths.entry_module,
                    dest=self._info.repkg_paths.entry_module
                )),
            'copy_inner_pkg_installer': _DirectCopyFile(
                CopyInfo(
                    src=self._info.src_paths.inner_pkg_installer,
                    dest=self._info.repkg_paths.inner_pkg_installer
                )),
            'copy_srepkg_setup_py': _DirectCopyFile(
                CopyInfo(
                    src=self._info.src_paths.srepkg_setup_py,
                    dest=self._info.repkg_paths.srepkg_setup_py
                )),
            'write_manifest': _WriteFromTemplate(
                CopyInfo(
                    src=self._info.src_paths.manifest_template,
                    dest=self._info.repkg_paths.manifest
                ),
                substitution_map={
                    "srepkg_name": self._info.repkg_paths.srepkg.name,
                }
            ),
            'create_srepkg_init': _CallMethod(self.create_srepkg_init),
            'build_entry_pts': _CallMethod(self.build_entry_pts),
            'build_srepkg_cfg': _CallMethod(self.build_srepkg_cfg),
            'build_inner_pkg_install_cfg': _CallMethod(
                self.build_inner_pkg_install_cfg),
            'build_distribution': _CallMethod(self.build_distribution)
        }


class Builder(abc.ABC):

    @abc.abstractmethod
    def build(self):
        pass


class SrepkgBuilder:

    def __init__(self, task_catalog: TaskCatalog, task_order: List[str]):
        # self._construction_tasks = construction_tasks
        self._task_catalog = task_catalog
        self._task_order = task_order

    def _validate_task_order(self):
        assert all([task in self._task_catalog.task_catalog for task in self._task_order])
        return self

    def _arrange_tasks(self):
        self._validate_task_order()
        return [
            self._task_catalog.task_catalog[task_name] for task_name in
            self._task_order
        ]

    def build(self):
        ordered_tasks = self._validate_task_order()._arrange_tasks()

        for task in ordered_tasks:
            task.execute()
