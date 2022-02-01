from pathlib import Path
import string
import shutil
import pkgutil


class HpkgBuilder:
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']

    def __init__(self, orig_path: Path, h_path: Path):
        self._orig_path = orig_path
        self._h_path = h_path
        self._pkg_name = orig_path.name

        install_components = \
            Path(__file__).parent.absolute() / 'install_components'

        self._build_src = {
            'hpkg_components': install_components / 'hpkg_components',
            'driver': install_components / 'hpkg_driver.py',
            'main': install_components / 'safe_main.py',
            'name_template': install_components / 'pkg_name.py.template'
        }
        self._build_dest = {
            'hpkg_components': self._h_path / 'hpkg_components',
            'driver': self._h_path / (str(self._pkg_name) + '_hpkg.py'),
            'main': self._h_path / self._pkg_name / '__main__.py',
            'old_main': self._h_path / self._pkg_name / 'old_main.py'
        }

    def copy_package(self):

        try:
            shutil.copytree(
                self._orig_path.parent.absolute(), self._h_path, ignore=shutil.ignore_patterns(
                    *self._ignore_types))

            shutil.copytree(self._build_src['hpkg_components'],
                            self._build_dest['hpkg_components'])

            shutil.copy2(self._build_src['driver'], self._build_dest['driver'])

        except OSError:
            print("Error when attempting to copy")
            exit(1)

    def move_orig_safe_main(self):
        self._build_dest['main'].rename(self._build_dest['old_main'])

    def write_pkg_name(self):

        template_text = pkgutil.get_data(
            'hpkg.install_components', 'pkg_name.py.template').decode()

        template = string.Template(template_text)

        substitutions = {
            'pkg_name': self._orig_path.name
        }

        result = template.substitute(substitutions)

        with Path(self._h_path / 'hpkg_components' / 'hpkg_header.py') \
                .open(mode='w') as f:
            f.write(result)

    def copy_safe_main(self):
        shutil.copy2(Path(__file__).parent.absolute() / 'install_components' /
                     'safe_main.py',
                     self._h_path / self._pkg_name / '__main__.py')

    def build_hpkg(self):
        self.copy_package()
        self.move_orig_safe_main()
        self.write_pkg_name()
        self.copy_safe_main()


# test_builder = HpkgBuilder(Path('/Users/duane/dproj/xiangqigame/xiangqigame'),
#                            Path('/Users/duane/hpackaged_pkgs/xiangqigame_safe'))
#
# test_builder.build_hpkg()

