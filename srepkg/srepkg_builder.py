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

    def __init__(self, src_paths: pcalc.BuilderSrcPaths,
                 repkg_paths: pcalc.BuilderDestPaths):
        """
        Construct a new SrepkgBuilder
        :param src_paths: BuilderSrcPaths object built by path_calculator module
        :param repkg_paths: BuilderDestPaths object built by path_calculator
        module
        """
        self._src_paths = src_paths
        self._repkg_paths = repkg_paths

    @property
    def src_paths(self):
        return self._src_paths

    @property
    def repkg_paths(self):
        return self._repkg_paths

    @property
    def header_subs(self):
        """Substitution dictionary for writing srepkg_header.py"""
        return {'pkg_name': self._src_paths.orig_pkg.name}

    def copy_inner_package(self):
        """Copies original package to SRE-package directory"""
        try:
            shutil.copytree(self._src_paths.orig_pkg, self._repkg_paths.root,
                            ignore=shutil.ignore_patterns(*self._ignore_types))
        except (OSError, FileNotFoundError, FileExistsError, Exception) as e_in:
            print('Error when attempting to copy original package '
                  'to new location.')
            exit(1)

    def copy_srepkg_components(self):
        """Copies srepkg components and driver to SRE-package directory"""
        try:
            shutil.copytree(self._src_paths.srepkg_components,
                            self._repkg_paths.srepkg_components)
        except (OSError, FileNotFoundError, FileExistsError, Exception) as e_s:
            print('Error when attempting to copy srepkg_components.')
            exit(1)

    def build_sr_cfg(self):
        orig_config = configparser.ConfigParser()
        orig_config.read(self._src_paths.orig_setup_cfg)

        orig_config_ep_cs_list = \
            orig_config['options.entry_points']['console_scripts'] \
            .strip().splitlines()

        sr_config_ep_cs_list = [
            epcs.orig_to_sr_line(orig_line, str(self._repkg_paths.entry_points))
            for orig_line in orig_config_ep_cs_list
        ]

        sr_config = configparser.ConfigParser()
        sr_config.read(self._src_paths.setup_cfg_outer)
        sr_config['options.entry_points']['console_scripts'] =\
            '\n' + '\n'.join(sr_config_ep_cs_list)

        with open(self._repkg_paths.setup_cfg_outer, 'w') as sr_configfile:
            sr_config.write(sr_configfile)

    def simple_file_copy(self, paths_attr: str):
        """Copies file from source to SRE-package based on attribute name
        in _src_paths and _repkg_paths. Requires same attribute name in each"""
        try:
            shutil.copy2(getattr(self._src_paths, paths_attr),
                         getattr(self._repkg_paths, paths_attr))
        except FileNotFoundError:
            print(f'Unable to find file when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._repkg_paths, paths_attr))}')
        except FileExistsError:
            print(f'File already exists at '
                  f'{str(getattr(self._repkg_paths, paths_attr))}.')
        except (OSError, Exception) as simple_copy_e:
            print(f'Error when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._repkg_paths, paths_attr))}')

    def modify_inner_pkg(self):
        """
        Bundle of all methods that modify the inner (aka original) package
        inside the SRE-package.
        """
        # self.move_orig_safe_main()
        # self.simple_file_copy('main_inner')
        self._repkg_paths.setup_py_inner.rename(
            self._repkg_paths.setup_py_inner.parent / 'setup_off.py')

        self._repkg_paths.setup_cfg_inner.rename(
            self._repkg_paths.setup_cfg_inner.parent / 'setup_off.cfg')

    def add_srepkg_layer(self):
        """
        Encapsulates work required to wrap srepkg file structure around modified
        copy of inner package.
        """

        self.copy_srepkg_components()
        # write_file_from_template('main_outer.py.template',
        #                          self._repkg_paths.main_outer,
        #                          self.main_outer_subs)
        write_file_from_template('pkg_name.py.template',
                                 self._repkg_paths.header, self.header_subs)

        self.simple_file_copy('setup_py_outer')
        self.simple_file_copy('init')
        self.build_sr_cfg()

    def build_srepkg(self):
        """
        Encapsulates all steps needed to build SRE-package, and displays
        original package and SRE-package paths when complete.
        """
        self.copy_inner_package()
        self.modify_inner_pkg()
        self.build_sr_cfg()

        # self.add_srepkg_layer()

        print(f'SRE-package built from: {self._src_paths.orig_pkg}\n'
              f'SRE-package saved in: {self._repkg_paths.root}\n')
