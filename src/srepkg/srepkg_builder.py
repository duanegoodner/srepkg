"""
Contains the SrepkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a
Srepkg.
"""

from pathlib import Path
import string
import pkgutil
import shutil
import configparser
import srepkg.shared_utils as su


# TODO modify copy order / folder structure to ensure no possible overwrite

def write_file_from_template(template_name: str, dest_path: Path, subs: dict):
    """
    Helper function used by SrepkgBuilder to write files to SRE-package paths
    based on template files and user-specified substitution pattern(s).
    
    :param template_name: name of template file (not full path)
    :param dest_path: Path object referencing destination file
    :param subs: dictionary of template_key: replacement_string entries.
    """
    # loader = pkgutil.get_loader('srepkg.repackaging_components.template_files')
    # template_file_sub_dir = ''
    #
    # template_files_loc = Path(loader.path).parent.absolute() / template_file_sub_dir
    #
    # template_file = template_files_loc / template_name
    #
    # with template_file.open(mode='r') as tf:
    #     template_text = tf.read()

    template_text = pkgutil.get_data(
        'srepkg.repackaging_components',
        '/template_files/' + template_name).decode()

    template = string.Template(template_text)
    result = template.substitute(subs)
    with dest_path.open(mode='w') as output_file:
        output_file.write(result)


class TemplateFileWriter:

    def __init__(self, templates_dir: Path, substitution_map: dict):
        self._templates_dir = templates_dir
        self._substitution_map = substitution_map

    @classmethod
    def from_pkg_data_dir(cls, pkg: str, data_dir: str, substitution_map: dict):
        pkg_path = Path(pkgutil.get_loader(pkg).path).parent
        template_dir_path = pkg_path / data_dir

        return cls(template_dir_path, substitution_map)

    def write_file(self, template_file_name: str, dest_path: Path):
        with (self._templates_dir / template_file_name).open(mode='r') as tf:
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
        self._template_file_writer = TemplateFileWriter.from_pkg_data_dir(
            pkg='srepkg.repackaging_components',
            data_dir='template_files',
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

    # @property
    # def entry_module_subs(self):
    #     return {
    #         'pkg_name': self._orig_pkg_info.pkg_name,
    #         'controller_import_path':
    #             self._repkg_paths.srepkg.name +
    #             '.srepkg_control_components.srepkg_controller'
    #     }

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

    def inner_pkg_setup_off(self):
        """
        Bundle of all methods that modify the inner (aka original) package
        inside the SRE-package.
        """

        self._repkg_paths.inner_setup_py_active.rename(
            self._repkg_paths.inner_setup_py_inactive)

        self._repkg_paths.inner_setup_cfg_active.rename(
            self._repkg_paths.inner_setup_cfg_inactive)

    def enable_dash_m_entry(self):
        self._repkg_paths.main_inner.rename(self._repkg_paths.main_inner_orig)
        shutil.copy2(self._src_paths.main_inner, self._repkg_paths.main_inner)

        self._template_file_writer.write_file(
            template_file_name='pkg_names.py.template',
            dest_path=self._repkg_paths.pkg_names_inner)

        # file_writer = TemplateFileWriter.from_pkg_data_dir(
        #     pkg='srepkg.repackaging_components',
        #     data_dir='template_files',
        #     substitution_map=self.pkg_names_subs
        # )
        #
        # file_writer.write_file(template_file_name='pkg_names.py.template',
        #                        dest_path=self._repkg_paths.pkg_names_inner)

        self.rebuild_inner_cfg_cse()

    def rebuild_inner_cs_lines(self):
        orig_inner_main = self._orig_pkg_info.pkg_name + '.' + '__main__'

        return [
            su.ep_console_script.build_cs_line(entry_pt) if
            entry_pt.module_path != orig_inner_main else
            su.ep_console_script.build_cs_line(
                entry_pt, with_redirect=True,
                new_path=self._orig_pkg_info.pkg_name + '.' + 'orig_main')
            for entry_pt in self._orig_pkg_info.entry_pts
        ]

    def rebuild_inner_cfg_cse(self):
        inner_config = configparser.ConfigParser()
        inner_config.read(self._repkg_paths.inner_setup_cfg_inactive)
        inner_config['options.entry_points']['console_scripts'] = \
            '\n' + '\n'.join(self.rebuild_inner_cs_lines())
        with open(self._repkg_paths.inner_setup_cfg_inactive,
                  'w') as inner_cf_file:
            inner_config.write(inner_cf_file)

    def add_srepkg_layer(self):
        """
        Encapsulates work required to wrap srepkg file structure around modified
        copy of inner package.
        """

        self.copy_srepkg_control_components()

        self.simple_file_copy(src_key='srepkg_setup_py',
                              dest_key='srepkg_setup_py')
        self.simple_file_copy(src_key='srepkg_init', dest_key='srepkg_init')
        self.simple_file_copy(src_key='inner_pkg_installer',
                              dest_key='inner_pkg_installer')
        self.simple_file_copy(src_key='main_outer', dest_key='main_outer')

        self._template_file_writer.write_file(
            'pkg_names.py.template', self._repkg_paths.pkg_names_outer)
        self._template_file_writer.write_file(
            'pkg_names.py.template', self._repkg_paths.pkg_names_mid)
        self._template_file_writer.write_file(
            'MANIFEST.in.template', self._repkg_paths.manifest)


        # write_file_from_template('pkg_names.py.template',
        #                          self._repkg_paths.pkg_names_outer,
        #                          self.pkg_names_subs)
        # write_file_from_template('pkg_names.py.template',
        #                          self._repkg_paths.pkg_names_mid,
        #                          self.pkg_names_subs)
        # write_file_from_template('MANIFEST.in.template',
        #                          self._repkg_paths.manifest,
        #                          self.pkg_names_subs)
        self.build_sr_cfg()

        self._repkg_paths.srepkg_entry_points.mkdir()
        self.write_entry_point_init()

        for entry_pt in self._orig_pkg_info.entry_pts:
            self.write_entry_point_file(entry_pt)

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """
        self.copy_inner_package()

        # TODO only need one of these (they do same thing)

        self.inner_pkg_setup_off()

        self.build_sr_cfg()

        self.add_srepkg_layer()

        if self._repkg_paths.main_inner.exists():
            self.enable_dash_m_entry()

        print(f'SRE-package built from:'
              f'{self._orig_pkg_info.root_path / self._orig_pkg_info.pkg_name}'
              f'S\nRE-package saved in: {self._repkg_paths.root}\n')
