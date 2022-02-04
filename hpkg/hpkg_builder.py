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

        # try:
        #     shutil.copy2(self._src_paths.driver, self._h_paths.driver)
        # except (OSError, FileNotFoundError, FileExistsError, Exception) as e_3:
        #     print("Error when attempting to copy hpkg_driver.")
        #     exit(1)

    def write_pkg_name_header(self):
        """Writes the original package name to a header file in H-pkg folder"""

        header_template_text = pkgutil.get_data(
            'hpkg.install_components', 'pkg_name.py.template').decode()
        header_template = string.Template(header_template_text)
        substitutions = {
            'pkg_name': self._src_paths.orig_pkg.name
        }
        header_result = header_template.substitute(substitutions)
        with Path(self._h_paths.header).open(mode='w') as f:
            f.write(header_result)

    def write_pkg_name_setup(self):
        setup_template_text = pkgutil.get_data(
            'hpkg.install_components', 'setup.py.template').decode()
        setup_template = string.Template(setup_template_text)
        substitutions = {
            'pkg_name_hpkg': self._src_paths.orig_pkg.name + '_hpkg'
        }
        setup_result = setup_template.substitute(substitutions)
        with Path(self._h_paths.setup).open(mode='w') as f:
            f.write(setup_result)

    def write_outer_main_imports(self):
        main_outer_template_text = pkgutil.get_data(
            'hpkg.install_components', 'main_outer.py.template').decode()
        main_outer_template = string.Template(main_outer_template_text)
        substitutions = {
            'header_import_path':
                self._src_paths.orig_pkg.name +
                '_hpkg.hpkg_components.hpkg_header',
            'controller_import_path':
                self._src_paths.orig_pkg.name +
                '_hpkg.hpkg_components.hpkg_controller'
        }
        main_outer_result = main_outer_template.substitute(substitutions)
        with Path(self._h_paths.main_outer).open(mode='w') as f:
            f.write(main_outer_result)

    # def write_pkg_name_generic(self, template_path: Path, dest_path: Path):
    #     template_text = pkgutil.get_data(
    #         'hpkg.install_components', template_path.name).decode()
    #     template = string.Template(template_text)
    #     substitutions = {
    #         'pkg_name': self._src_paths.orig_pkg.name
    #     }
    #     result = template.substitute(substitutions)
    #     with dest_path.open(mode='w') as f:
    #         f.write(result)

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

    def copy_outer_main(self):
        """Copies H-pkg specific version of __main__.py to hpkg folder"""
        shutil.copy2(self._src_paths.main_outer, self._h_paths.main_outer)

    def copy_inner_main(self):
        """Copies H-pkg specific version of __main__.py to hpkg folder"""
        shutil.copy2(self._src_paths.main_inner, self._h_paths.main_inner)

    def copy_hpkg_init(self):
        shutil.copy2(self._src_paths.init, self._h_paths.init)

    def view_paths(self):

        for src_path in self._src_paths:
            print(src_path)
        print()
        for dest_path in self._h_paths:
            print(dest_path)

    def build_hpkg(self):
        """Build the hpkg then prints paths of original pkg, hpkg, and hpkg
        executable to terminal"""
        self.copy_package()
        self.copy_hpkg_components()
        self.view_paths()
        self.move_orig_safe_main()

        self.write_pkg_name_header()
        self.write_pkg_name_setup()

        # self.copy_outer_main()
        self.write_outer_main_imports()
        self.copy_inner_main()
        self.copy_hpkg_init()

        print(f'H-package built from: {self._src_paths.orig_pkg}\n'
              f'H-package saved in: {self._h_paths.root}\n')
