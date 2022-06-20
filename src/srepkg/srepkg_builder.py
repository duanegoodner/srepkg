"""
Contains the SrepkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a
Srepkg.
"""
import configparser
import shutil
import string
import sys

from typing import List, Callable, NamedTuple
from pathlib import Path
from enum import Enum

import srepkg.distribution_buillder as db
import srepkg.entry_points_builder as epb
import custom_datatypes.builder_src_paths as bsp
import custom_datatypes.builder_dest_paths as bdp
import custom_datatypes.named_tuples as nt


class SrepkgBuilderErrorMsg(NamedTuple):
    msg: str


class SrepkgBuilderErrors(SrepkgBuilderErrorMsg, Enum):
    OrigPkgPathNotFound = SrepkgBuilderErrorMsg(
        msg='Original package path not found')
    DestPkgPathExits = SrepkgBuilderErrorMsg(
        msg='Intended Srepkg destination path already exists')
    ControlComponentsNotFound = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy sub-package '
            'srepkg_control_components. Sub-package not found')
    ControlComponentsExist = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy sub-package '
            'srepkg_control_components. Destination path already exists.')
    FileNotFoundForCopy = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy. Source file not found.')
    CopyDestinationPathExists = SrepkgBuilderErrorMsg(
        msg='Error when attempting to copy. Destination path already exists')


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

    _build_errors = SrepkgBuilderErrors

    def __init__(self, orig_pkg_info: nt.OrigPkgInfo,
                 src_paths: bsp.BuilderSrcPaths,
                 repkg_paths: bdp.BuilderDestPaths,
                 dist_out_dir: Path):
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
        self._entry_points_builder = epb.EntryPointsBuilder \
            .from_srepkg_builder_init_args(
                orig_pkg_info=orig_pkg_info,
                src_paths=src_paths,
                repkg_paths=repkg_paths)
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
            shutil.copytree(self._orig_pkg_info.root_path,
                            self._repkg_paths.srepkg)
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

    def build_sr_cfg(self):
        sr_config = configparser.ConfigParser()
        sr_config.read(self._src_paths.srepkg_setup_cfg)

        sr_config['options.entry_points']['console_scripts'] = \
            self._entry_points_builder.get_cfg_cse_str()

        sr_config['metadata']['name'] = self._repkg_paths.srepkg.name

        sr_config['metadata']['version'] = self._orig_pkg_info.version

        with open(self._repkg_paths.srepkg_setup_cfg, 'w') as sr_configfile:
            sr_config.write(sr_configfile)

    def write_entry_point_file(self, orig_cse: nt.CSEntry):

        shutil.copy2(self._src_paths.entry_point_template,
                     self._repkg_paths.srepkg_entry_points /
                     (orig_cse.command + '.py'))

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

    def build_inner_layer(self):
        self.build_srepkg_layer(
            call_methods=[self.copy_inner_package])

    def build_mid_layer(self):
        self.build_srepkg_layer(
            call_methods=[self.copy_srepkg_control_components,
                          self._entry_points_builder.build_entry_pts],
            direct_copy_files=[
                SrcDestPair(src=self._src_paths.srepkg_init,
                            dest=self._repkg_paths.srepkg_init),
            ],
            template_file_writes=[
                SrcDestPair(
                    src=self._src_paths.pkg_names_template,
                    dest=self._repkg_paths.pkg_names_mid)
            ])

    def build_outer_layer(self):
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
            ])

    def build_distribution(self):

        dist_builder = db.DistributionBuilder(
            pkg_src=self._repkg_paths.root.absolute(),
            archive_format='zip',
            output_dir=self._dist_out_dir,
            # TODO need better method and location for logging

        )
        return dist_builder.write_archive()

    def output_summary(self, archive_filename: str):
        print(f'Original package \'{self._orig_pkg_info.pkg_name}\' has been '
              f're-packaged as \'{self._repkg_paths.srepkg.name}\'\n')
        print(f'The re-packaged version has been saved as source '
              f'distribution archive file:\n'
              f'{str(Path.cwd()) + "/" + archive_filename}')
        print(f'\'{self._repkg_paths.srepkg.name}\' can be installed using:\n'
              f'pip install {str(Path.cwd()) + "/" + archive_filename}\n')
        print(f'After installation, \'{self._repkg_paths.srepkg.name}\' will '
              f'provide command line access to the following commands:')
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
