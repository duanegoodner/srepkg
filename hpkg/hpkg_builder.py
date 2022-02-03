"""
Contains the HpkgBuilder class that creates a copy of the original package and
wraps the copied package with a file structure that forces it to run as a Hpkg.
"""

from pathlib import Path
import string
import shutil
import pkgutil
import hpkg.path_calculator as pcalc


class HpkgBuilder:
    """
    Hpkg encapsulates the file paths and methods for creating a Hpkg version
    of an existing package.
    """

    # file patterns that are not copied into the hpkg
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']
    install_components = Path(__file__).parent.absolute() / 'install_components'

    def __init__(self, src_paths: pcalc.SrcPaths, h_paths: pcalc.DestPaths):
        """
        Construct a new HpkgBuilder
        :param src_paths: SrcPaths object built by path_calculator module
        :param h_paths: DestPaths object built by path_calculator module
        """
        self._src_paths = src_paths
        self._h_paths = h_paths

    def copy_package(self):
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

        try:
            shutil.copy2(self._src_paths.driver, self._h_paths.driver)
        except (OSError, FileNotFoundError, FileExistsError, Exception) as e_3:
            print("Error when attempting to copy hpkg_driver.")
            exit(1)

    def write_pkg_name(self):
        """Writes the original package name to a header file in H-pkg folder"""

        template_text = pkgutil.get_data(
            'hpkg.install_components', 'pkg_name.py.template').decode()
        template = string.Template(template_text)
        substitutions = {
            'pkg_name': self._src_paths.orig_pkg.name
        }
        result = template.substitute(substitutions)
        with Path(self._h_paths.header).open(mode='w') as f:
            f.write(result)

    def move_orig_safe_main(self):
        """Renames __main__.py in the H-package to old_main.py"""

        try:
            self._h_paths.main.rename(self._h_paths.old_main)
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

    def copy_safe_main(self):
        """Copies H-pkg specific version of __main__.py to hpkg folder"""
        shutil.copy2(self._src_paths.main, self._h_paths.main)

    def build_hpkg(self):
        """Build the hpkg then prints paths of original pkg, hpkg, and hpkg
        executable to terminal"""
        self.copy_package()
        self.copy_hpkg_components()
        self.move_orig_safe_main()
        self.write_pkg_name()
        self.copy_safe_main()
        print(f'H-package built from: {self._src_paths.orig_pkg}\n'
              f'H-package saved in: {self._h_paths.root}\n'
              f'Run {self._h_paths.driver} as a script to start the '
              f'H-packaged app.')

