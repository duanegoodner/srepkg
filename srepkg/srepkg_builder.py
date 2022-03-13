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
import srepkg.path_calculator as pcalc
import srepkg.ep_console_script as epcs


# TODO modify copy order / folder structure to ensure no possible overwrite

def write_file_from_template(template_name: str, dest_path: Path, subs: dict):
    """
    Helper function used by SrepkgBuilder to write files to SRE-package paths
    based on template files and user-specified substitution pattern(s).
    
    :param template_name: name of template file (not full path)
    :param dest_path: Path object referencing destination file
    :param subs: dictionary of template_key: replacement_string entries.
    """
    template_text = pkgutil.get_data(
        'srepkg.install_components', template_name).decode()
    template = string.Template(template_text)
    result = template.substitute(subs)
    with dest_path.open(mode='w') as output_file:
        output_file.write(result)


class SrepkgBuilder:
    """
    Encapsulates  methods for creating a SRE-packaged version of an existing
    package.
    """

    # file patterns that are not copied into the SRE-packaged app
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']

    def __init__(self, orig_pkg_info: pcalc.OrigPkgInfo,
                 src_paths: pcalc.BuilderSrcPaths,
                 repkg_paths: pcalc.BuilderDestPaths):
        """
        Construct a new SrepkgBuilder
        :param src_paths: BuilderSrcPaths object built by path_calculator module
        :param repkg_paths: BuilderDestPaths object built by path_calculator
        module
        """
        self._orig_pkg_info = orig_pkg_info
        self._src_paths = src_paths
        self._repkg_paths = repkg_paths

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

    @property
    def entry_module_subs(self):
        return {
            'pkg_name':
                self._orig_pkg_info.pkg_name,
            'controller_import_path':
                self._repkg_paths.srepkg.name +
                '.srepkg_components.srepkg_controller'
        }

    def copy_inner_package(self):
        """Copies original package to SRE-package directory"""
        try:
            shutil.copytree(self.orig_pkg_info.root_path,
                            self.repkg_paths.srepkg,
                            ignore=shutil.ignore_patterns(*self._ignore_types))
        except (OSError, FileNotFoundError, FileExistsError, Exception):
            print('Error when attempting to copy original package '
                  'to new location.')
            exit(1)

    def copy_srepkg_components(self):
        """Copies srepkg components and driver to SRE-package directory"""
        try:
            shutil.copytree(self.src_paths.srepkg_components,
                            self.repkg_paths.srepkg_components)
        except (OSError, FileNotFoundError, FileExistsError, Exception):
            print('Error when attempting to copy srepkg_components.')
            exit(1)

    def orig_cse_to_sr_cse(self, orig_cse: epcs.CSEntry):
        return epcs.CSEntry(
            command=orig_cse.command + '_sr',
            module_path=self.repkg_paths.srepkg.name + '.' +
            self.repkg_paths.srepkg_entry_points.name + '.' + orig_cse.command,
            funct='entry_funct'
        )

    def build_sr_cfg(self):
        sr_config = configparser.ConfigParser()
        sr_config.read(self.src_paths.srepkg_setup_cfg)
        sr_config_ep_cs_list = [self.orig_cse_to_sr_cse(orig_cse) for orig_cse
                                in self.orig_pkg_info.entry_pts]
        sr_config_cs_lines = [epcs.build_cs_line(sr_cse) for sr_cse in
                              sr_config_ep_cs_list]
        sr_config['options.entry_points']['console_scripts'] = \
            '\n' + '\n'.join(sr_config_cs_lines)

        sr_config['metadata']['name'] = self.repkg_paths.srepkg.name

        with open(self.repkg_paths.srepkg_setup_cfg, 'w') as sr_configfile:
            sr_config.write(sr_configfile)

    def write_entry_point_file(self, orig_cse: epcs.CSEntry):
        # entry_point_subs = {
        #     'entry_module': self._repkg_paths.srepkg.name +
        #                     '.srepkg_components.entry_points',
        #     'entry_command': orig_cse.command
        # }

        shutil.copy2(self._src_paths.entry_point_template,
                     self._repkg_paths.srepkg_entry_points /
                     (orig_cse.command + '.py'))

        #
        # write_file_from_template('entry_point.py.template',
        #                          self._repkg_paths.srepkg_entry_points /
        #                          (orig_cse.command + '.py'), entry_point_subs)

    def write_entry_point_init(self):
        entry_pt_imports = [
            f'import {self._repkg_paths.srepkg.name}.srepkg_entry_points.' \
            f'{cse.command}' for cse in self.orig_pkg_info.entry_pts
        ]

        with open(self._repkg_paths.srepkg_entry_points_init, 'w') as ent_init:
            for import_entry in entry_pt_imports:
                ent_init.write(import_entry + '\n')
            ent_init.write('\n')

    def simple_file_copy(self, src_key: str, dest_key: str):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(getattr(self.src_paths, src_key),
                         getattr(self.repkg_paths, dest_key))
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

    def inner_pkg_install_inhibit(self):
        """
        Bundle of all methods that modify the inner (aka original) package
        inside the SRE-package.
        """

        self.repkg_paths.orig_pkg_setup_py.rename(
            self.repkg_paths.orig_pkg_setup_py.parent / 'setup_off.py')

        self.repkg_paths.orig_pkg_setup_cfg.rename(
            self.repkg_paths.orig_pkg_setup_cfg.parent / 'setup_off.cfg')

    def enable_dash_m_entry(self):
        self.repkg_paths.main_inner.rename(self.repkg_paths.main_inner_orig)
        shutil.copy2(self._src_paths.main_inner, self._repkg_paths.main_inner)

        write_file_from_template('pkg_names.py.template',
                                 self._repkg_paths.pkg_names_inner,
                                 self.pkg_names_subs)

    def add_srepkg_layer(self):
        """
        Encapsulates work required to wrap srepkg file structure around modified
        copy of inner package.
        """

        self.copy_srepkg_components()

        self.simple_file_copy(src_key='srepkg_setup_py',
                              dest_key='srepkg_setup_py')
        self.simple_file_copy(src_key='srepkg_init', dest_key='srepkg_init')
        self.simple_file_copy(src_key='inner_pkg_installer',
                              dest_key='inner_pkg_installer')
        self.simple_file_copy(src_key='main_outer', dest_key='main_outer')

        write_file_from_template('pkg_names.py.template',
                                 self._repkg_paths.pkg_names_outer,
                                 self.pkg_names_subs)
        write_file_from_template('pkg_names.py.template',
                                 self._repkg_paths.pkg_names_mid,
                                 self.pkg_names_subs)
        write_file_from_template('MANIFEST.in.template',
                                 self._repkg_paths.manifest,
                                 self.pkg_names_subs)
        self.build_sr_cfg()

        self._repkg_paths.srepkg_entry_points.mkdir()
        self.write_entry_point_init()
        # self.simple_file_copy(src_key='srepkg_init',
        #                       dest_key='srepkg_entry_points_init')

        for entry_pt in self.orig_pkg_info.entry_pts:
            self.write_entry_point_file(entry_pt)

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """
        self.copy_inner_package()
        self.inner_pkg_install_inhibit()
        self.build_sr_cfg()

        self.add_srepkg_layer()

        if self._repkg_paths.main_inner.exists():
            self.enable_dash_m_entry()

        print(f'SRE-package built from:'
              f'{self.orig_pkg_info.root_path / self.orig_pkg_info.pkg_name}\n'
              f'SRE-package saved in: {self.repkg_paths.root}\n')
