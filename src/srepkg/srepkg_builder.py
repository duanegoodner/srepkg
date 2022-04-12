"""
Contains the SrepkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a
Srepkg.
"""

from typing import List, Callable, NamedTuple
from pathlib import Path
from enum import Enum
import string
import shutil
import sys
import configparser
import srepkg.shared_utils as su


# TODO modify copy order / folder structure to ensure no possible overwrite


class SrepkgBuilderErrorMsg(NamedTuple):
    msg: str


class SrepkgBuilderErrors(SrepkgBuilderErrorMsg, Enum):
    OrigPkgPathNotFound = SrepkgBuilderErrorMsg(
        msg='Original package path not found')
    DestPkgPathExits = SrepkgBuilderErrorMsg(
        msg='Intended Srepkg destination path already exists')
    ControlComponentsNotFound = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy sub-package '
            'srepkg_control_components. Sub-package not found'
    )
    ControlComponentsExist = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy sub-package '
            'srepkg_control_components. Destination path already exists.'
    )
    FileNotFoundForCopy = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy. Source file not found.'
    )
    CopyDestinationPathExists = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy. Destination path already exists'
    )


class SrcDestPair(NamedTuple):
    src: Path
    dest: Path


class TemplateFileWriter:

    def __init__(self, substitution_map: dict):
        self._substitution_map = substitution_map

    def write_file(self, template_file: Path, dest_path: Path):
        with template_file.open(mode='r') as tf:
            template_text = tf.read()
        template = string.Template(template_text)
        result = template.substitute(self._substitution_map)
        with dest_path.open(mode='w') as output_file:
            output_file.write(result)


class SrepkgBuilder:
    """
    Encapsulates  methods for creating a SRE-packaged version of an existing
    package.
    """

    # file patterns that are not copied into the SRE-packaged app
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']
    _build_errors = SrepkgBuilderErrors

    def __init__(self, orig_pkg_info: su.named_tuples.OrigPkgInfo,
                 src_paths: su.named_tuples.BuilderSrcPaths,
                 repkg_paths: su.named_tuples.BuilderDestPaths):
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
                'inner_pkg_name': self._orig_pkg_info.pkg_name,
                'sre_pkg_name': self._repkg_paths.srepkg.name,
            }
        )

    @property
    def orig_pkg_info(self):
        return self._orig_pkg_info

    @property
    def src_paths(self):
        return self._src_paths

    @property
    def repkg_paths(self):
        return self._repkg_paths

    @property
    def pkg_names_subs(self):
        return {
            'inner_pkg_name': self._orig_pkg_info.pkg_name,
            'sre_pkg_name': self._repkg_paths.srepkg.name,
        }

    def copy_inner_package(self):
        """Copies original package to SRE-package directory"""
        try:
            shutil.copytree(self._orig_pkg_info.root_path,
                            self._repkg_paths.srepkg,
                            ignore=shutil.ignore_patterns(*self._ignore_types))
        except FileNotFoundError:
            sys.exit(self._build_errors.OrigPkgPathNotFound.msg)
        except FileExistsError:
            sys.exit(self._build_errors.DestPkgPathExits.msg)

    def copy_srepkg_control_components(self):
        """Copies srepkg components and driver to SRE-package directory"""
        try:
            shutil.copytree(self._src_paths.srepkg_control_components,
                            self._repkg_paths.srepkg_control_components)
        except FileNotFoundError:
            sys.exit(self._build_errors.ControlComponentsNotFound.msg)
        except FileExistsError:
            sys.exit(self._build_errors.ControlComponentsExist.msg)

    def orig_cse_to_sr_cse(self, orig_cse: su.named_tuples.CSEntry):
        return su.named_tuples.CSEntry(
            command=orig_cse.command,
            module_path=self._repkg_paths.srepkg.name + '.' +
            self._repkg_paths.srepkg_entry_points.name + '.' + orig_cse.command,
            funct='entry_funct'
        )

    def build_sr_cfg(self):
        sr_config = configparser.ConfigParser()
        sr_config.read(self._src_paths.srepkg_setup_cfg)
        sr_config_ep_cs_list = [self.orig_cse_to_sr_cse(orig_cse) for orig_cse
                                in self._orig_pkg_info.entry_pts]
        sr_config_cs_lines = [su.ep_console_script.build_cs_line(sr_cse) for
                              sr_cse in sr_config_ep_cs_list]
        sr_config['options.entry_points']['console_scripts'] = \
            '\n' + '\n'.join(sr_config_cs_lines)

        sr_config['metadata']['name'] = self._repkg_paths.srepkg.name

        with open(self._repkg_paths.srepkg_setup_cfg, 'w') as sr_configfile:
            sr_config.write(sr_configfile)

    def write_entry_point_file(self, orig_cse: su.named_tuples.CSEntry):

        shutil.copy2(self._src_paths.entry_point_template,
                     self._repkg_paths.srepkg_entry_points /
                     (orig_cse.command + '.py'))

    def write_entry_point_init(self):
        entry_pt_imports = [
            f'import {self._repkg_paths.srepkg.name}.srepkg_entry_points.'
            f'{cse.command}' for cse in self._orig_pkg_info.entry_pts
        ]

        with open(self._repkg_paths.srepkg_entry_points_init, 'w') as ent_init:
            for import_entry in entry_pt_imports:
                ent_init.write(import_entry + '\n')
            ent_init.write('\n')

    def simple_file_copy(self, src_dest: SrcDestPair):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(*src_dest)
        except FileNotFoundError:
            print(f'Unable to find file when attempting to copy from'
                  f'{str(src_dest.src)} to {str(src_dest.dest)}')
            sys.exit(self._build_errors.FileNotFoundForCopy.msg)
        except FileExistsError:
            print(f'File already exists at {str(src_dest.src)}.')
            sys.exit(self._build_errors.CopyDestinationPathExists.msg)

    def inner_pkg_setup_off(self):
        """
        Bundle of all methods that modify the inner (aka original) package
        inside the SRE-package.
        """

        self._repkg_paths.inner_setup_py_active.rename(
            self._repkg_paths.inner_setup_py_inactive)

        self._repkg_paths.inner_setup_cfg_active.rename(
            self._repkg_paths.inner_setup_cfg_inactive)

    def build_srepkg_entry_pts(self):
        self._repkg_paths.srepkg_entry_points.mkdir()
        self.write_entry_point_init()
        for entry_pt in self._orig_pkg_info.entry_pts:
            self.write_entry_point_file(entry_pt)

    def build_srepkg_layer(
            self,
            call_methods: List[Callable] = None,
            direct_copy_files: List[SrcDestPair] = None,
            template_file_writes: List[SrcDestPair] = None):

        if call_methods is not None:
            for method in call_methods:
                method()

        if direct_copy_files is not None:
            for direct_copy_pair in direct_copy_files:
                self.simple_file_copy(direct_copy_pair)

        if template_file_writes is not None:
            for write_op in template_file_writes:
                self._template_file_writer.write_file(*write_op)

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """

        # inner layer
        self.build_srepkg_layer(
            call_methods=[self.copy_inner_package, self.inner_pkg_setup_off]
        )

        # mid layer
        self.build_srepkg_layer(
            call_methods=[self.copy_srepkg_control_components,
                          self.build_srepkg_entry_pts],
            direct_copy_files=[
                SrcDestPair(src=self._src_paths.srepkg_init,
                            dest=self._repkg_paths.srepkg_init),
                SrcDestPair(
                    src=self._src_paths.main_outer,
                    dest=self._repkg_paths.main_outer)
            ],
            template_file_writes=[
                SrcDestPair(
                    src=self._src_paths.pkg_names_template,
                    dest=self._repkg_paths.pkg_names_mid)
            ]
        )

        # outer layer
        self.build_srepkg_layer(
            call_methods=[self.build_sr_cfg],
            direct_copy_files=[
                SrcDestPair(
                    src=self._src_paths.inner_pkg_installer,
                    dest=self._repkg_paths.inner_pkg_installer),
                SrcDestPair(
                    src=self._src_paths.srepkg_setup_py,
                    dest=self._repkg_paths.srepkg_setup_py),
            ],
            template_file_writes=[
                SrcDestPair(
                    src=self._src_paths.pkg_names_template,
                    dest=self._repkg_paths.pkg_names_outer
                ),
                SrcDestPair(
                    src=self._src_paths.manifest_template,
                    dest=self._repkg_paths.manifest)
            ]
        )

        print(f'SRE-package built from:'
              f'{self._orig_pkg_info.root_path / self._orig_pkg_info.pkg_name}'
              f'S\nRE-package saved in: {self._repkg_paths.root}\n')







