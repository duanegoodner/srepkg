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
import srepkg.config_builder as cb


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
    def entry_module_subs(self):
        return {
            'pkg_name':
                self._repkg_paths.srepkg.name,
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
            self.repkg_paths.srepkg_entry_points.name + '.' + orig_cse.funct,
            funct=orig_cse.funct
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

    def simple_file_copy(self, paths_attr: str):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(getattr(self.src_paths, paths_attr),
                         getattr(self.repkg_paths, paths_attr))
        except FileNotFoundError:
            print(f'Unable to find file when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._repkg_paths, paths_attr))}')
        except FileExistsError:
            print(f'File already exists at '
                  f'{str(getattr(self._repkg_paths, paths_attr))}.')
        except (OSError, Exception):
            print(f'Error when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._repkg_paths, paths_attr))}')

    def modify_inner_pkg(self):
        """
        Bundle of all methods that modify the inner (aka original) package
        inside the SRE-package.
        """

        self.repkg_paths.orig_pkg_setup_py.rename(
            self.repkg_paths.orig_pkg_setup_py.parent / 'setup_off.py')

        self.repkg_paths.orig_pkg_setup_cfg.rename(
            self.repkg_paths.orig_pkg_setup_cfg.parent / 'setup_off.cfg')

    def add_srepkg_layer(self):
        """
        Encapsulates work required to wrap srepkg file structure around modified
        copy of inner package.
        """

        self.copy_srepkg_components()
        write_file_from_template('srepkg_entry.py.template',
                                 self._repkg_paths.srepkg_entry_module,
                                 self.entry_module_subs)

        self.simple_file_copy('srepkg_setup_py')
        self.simple_file_copy('srepkg_init')
        self.build_sr_cfg()

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """
        self.copy_inner_package()
        self.modify_inner_pkg()
        self.build_sr_cfg()

        self.add_srepkg_layer()

        print(f'SRE-package built from:'
              f'{self.orig_pkg_info.root_path / self.orig_pkg_info.pkg_name}\n'
              f'SRE-package saved in: {self.repkg_paths.root}\n')
