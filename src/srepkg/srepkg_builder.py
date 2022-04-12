"""
Contains the SrepkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a
Srepkg.
"""

from typing import List, Callable
from pathlib import Path
import string
import shutil
import configparser
import srepkg.shared_utils as su


# TODO modify copy order / folder structure to ensure no possible overwrite



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
        except (OSError, FileNotFoundError, FileExistsError, Exception):
            print('Error when attempting to copy original package '
                  'to new location.')
            exit(1)

    def copy_srepkg_control_components(self):
        """Copies srepkg components and driver to SRE-package directory"""
        try:
            shutil.copytree(self._src_paths.srepkg_control_components,
                            self._repkg_paths.srepkg_control_components)
        except (OSError, FileNotFoundError, FileExistsError, Exception):
            print('Error when attempting to copy srepkg_control_components.')
            exit(1)

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

    def simple_file_copy(self, src_key: str, dest_key: str):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(getattr(self._src_paths, src_key),
                         getattr(self._repkg_paths, dest_key))
        except FileNotFoundError:
            print(f'Unable to find file when attempting to copy from'
                  f'{str(getattr(self._src_paths, src_key))} to '
                  f'{str(getattr(self._repkg_paths, dest_key))}')
            exit(1)

        except FileExistsError:
            print(f'File already exists at '
                  f'{str(getattr(self._repkg_paths, dest_key))}.')
            exit(1)
        except (OSError, Exception):
            print(f'Error when attempting to copy from'
                  f'{str(getattr(self._src_paths, src_key))} to '
                  f'{str(getattr(self._repkg_paths, dest_key))}')
            exit(1)

    def template_file_write_by_keys(self, src_key: str, dest_key: str):
        self._template_file_writer.write_file(
            getattr(self._src_paths, src_key),
            getattr(self._repkg_paths, dest_key)
        )

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
            direct_copy_files: List[su.named_tuples.SrcDestShortcutPair] = None,
            template_file_writes: List[su.named_tuples.SrcDestShortcutPair] = None):

        if call_methods is not None:
            for method in call_methods:
                method()

        if direct_copy_files is not None:
            for direct_copy in direct_copy_files:
                self.simple_file_copy(src_key=direct_copy.src_key,
                                      dest_key=direct_copy.dest_key)

        if template_file_writes is not None:
            for write_op in template_file_writes:
                self.template_file_write_by_keys(
                    src_key=write_op.src_key,
                    dest_key=write_op.dest_key
                )

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
                su.named_tuples.SrcDestShortcutPair(
                    src_key='srepkg_init', dest_key='srepkg_init'
                ),
                su.named_tuples.SrcDestShortcutPair(
                    src_key='main_outer', dest_key='main_outer'
                )
            ],
            template_file_writes=[
                su.named_tuples.SrcDestShortcutPair(
                    src_key='pkg_names_template', dest_key='pkg_names_mid'
                )
            ]
        )

        # outer layer
        self.build_srepkg_layer(
            call_methods=[self.build_sr_cfg],
            direct_copy_files=[
                su.named_tuples.SrcDestShortcutPair(
                    src_key='inner_pkg_installer',
                    dest_key='inner_pkg_installer'
                ),
                su.named_tuples.SrcDestShortcutPair(
                    src_key='srepkg_setup_py', dest_key='srepkg_setup_py'
                ),
            ],
            template_file_writes=[
                su.named_tuples.SrcDestShortcutPair(
                    src_key='pkg_names_template', dest_key='pkg_names_outer'
                ),
                su.named_tuples.SrcDestShortcutPair(
                    src_key='manifest_template',
                    dest_key='manifest'
                )
            ]
        )

        print(f'SRE-package built from:'
              f'{self._orig_pkg_info.root_path / self._orig_pkg_info.pkg_name}'
              f'S\nRE-package saved in: {self._repkg_paths.root}\n')







