"""
Contains the HpkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a Hpkg.
"""

from pathlib import Path
import shutil
import srepkg.path_calculator as pcalc
from srepkg.utilities import write_file_from_template


class HpkgBuilder:
    """
    Hpkg encapsulates the file paths and methods for creating a Hpkg version
    of an existing package.
    """

    # file patterns that are not copied into the hpkg
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']

    install_components = Path(__file__).parent.absolute() / 'install_components'

    def __init__(self, src_paths: pcalc.BuildSrcPaths, h_paths: pcalc.BuildDestPaths):
        """
        Construct a new HpkgBuilder
        :param src_paths: BuildSrcPaths object built by path_calculator module
        :param h_paths: BuildDestPaths object built by path_calculator module
        """
        self._src_paths = src_paths
        self._h_paths = h_paths

    @property
    def setup_subs(self):
        return {'pkg_name_srepkg': self._src_paths.orig_pkg.name + 'srepkg'}

    @property
    def header_subs(self):
        return {'pkg_name': self._src_paths.orig_pkg.name}

    @property
    def main_outer_subs(self):
        return {
            'header_import_path':
                self._src_paths.orig_pkg.name +
                'srepkg.srepkg_components.srepkg_header',
            'controller_import_path':
                self._src_paths.orig_pkg.name +
                'srepkg.srepkg_components.srepkg_controller'
        }

    def copy_inner_package(self):
        """Copies original package to H-package directory"""

        try:
            shutil.copytree(self._src_paths.orig_pkg, self._h_paths.root,
                            ignore=shutil.ignore_patterns(*self._ignore_types))
        except (OSError, FileNotFoundError, FileExistsError, Exception) as e_1:
            print('Error when attempting to copy original package '
                  'to new location.')
            exit(1)

    def copy_hpkg_components(self):
        """Copies hpkg components and driver to H-package directory"""
        try:
            shutil.copytree(self._src_paths.hpkg_components,
                            self._h_paths.hpkg_components)
        except (OSError, FileNotFoundError, FileExistsError, Exception) as e_2:
            print('Error when attempting to copy hpkg_components.')
            exit(1)

    def move_orig_safe_main(self):
        """Renames __main__.py in the H-package to old_main.py"""

        try:
            self._h_paths.main_inner.rename(self._h_paths.old_main)
        except FileNotFoundError:
            print('__main__ not found in copy of original package.')
            exit(1)
        except FileExistsError:
            print('It appears that the original module has a file named '
                  'old_main.py. The hpkg_builder needs that file name.')
            exit(1)
        except (OSError, Exception) as e4:
            print('Error when trying to rename __main__.py to old_main.py')
            exit(1)

    def simple_file_copy(self, paths_attr: str):
        try:
            shutil.copy2(getattr(self._src_paths, paths_attr),
                         getattr(self._h_paths, paths_attr))
        except FileNotFoundError:
            print(f'Unable to find file when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._h_paths, paths_attr))}')
        except FileExistsError:
            print(f'File already exists at '
                  f'{str(getattr(self._h_paths, paths_attr))}.')
        except (OSError, Exception) as simple_copy_e:
            print(f'Error when attempting to copy from'
                  f'{str(getattr(self._src_paths, paths_attr))} to '
                  f'{str(getattr(self._h_paths, paths_attr))}')

    def modify_inner_pkg(self):
        self.move_orig_safe_main()
        self.simple_file_copy('main_inner')
        self._h_paths.setup_inner.rename(self._h_paths.setup_inner.parent /
                                         'setup_off.py')

    def add_srepkg_layer(self):

        self.copy_hpkg_components()
        write_file_from_template('main_outer.py.template',
                                 self._h_paths.main_outer, self.main_outer_subs)
        write_file_from_template('pkg_name.py.template',
                                 self._h_paths.header, self.header_subs)
        write_file_from_template('setup.py.template', self._h_paths.setup_outer,
                                 self.setup_subs)
        self.simple_file_copy('init')

    def build_hpkg(self):
        """Build the hpkg then prints paths of original pkg, hpkg, and hpkg
        executable to terminal"""
        self.copy_inner_package()
        self.modify_inner_pkg()
        self.add_srepkg_layer()

        print(f'H-package built from: {self._src_paths.orig_pkg}\n'
              f'H-package saved in: {self._h_paths.root}\n')
