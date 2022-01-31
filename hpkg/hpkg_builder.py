from pathlib import Path
import string
import shutil


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
            'driver': self._h_path / ('hpkg_' + str(self._pkg_name) + '.py'),
            'main': self._h_path / self._pkg_name / '__main__.py',
            'old_main': self._h_path / self._pkg_name / 'old_main.py'
        }

    def copy_package(self):

        try:
            shutil.copytree(
                self._orig_path, self._h_path, ignore=shutil.ignore_patterns(
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

        with (self._build_src['name_template']).open(mode='r') as f:
            template_text = f.read()

        template = string.Template(template_text)

        substitutions = {
            'hpkg_path': self._h_path
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


test_builder = HpkgBuilder(Path('/Users/duane/dproj/xiangqigame'),
                           Path('/Users/duane/dproj/hhpkgs/xiangqigame'))

test_builder.build_hpkg()
