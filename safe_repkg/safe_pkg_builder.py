import os
from pathlib import Path
import string
from shutil import copytree, ignore_patterns, copy2


class HpkgBuilder:
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']

    def __init__(self, orig_path: Path, h_path: Path):
        self._orig_path = orig_path
        self._h_path = h_path
        self._pkg_name = orig_path.name
        self._build_src = {
            'hpkg_components': Path(__file__).parent.absolute().joinpath(
                'install_components', 'hpkg_components'),
            'driver': Path(__file__).parent.absolute().joinpath(
                'install_components', 'hpkg_driver.py'),
            'main': Path(__file__).parent.absolute().joinpath(
                'install_components', 'safe_main.py'),
            'name_template': Path(__file__).parent.absolute().joinpath(
                'install_components', 'pkg_name.py.template')
        }
        self._build_dest = {
            'hpkg_components': self._h_path.joinpath('hpkg_components'),
            'driver': self._h_path.joinpath(
                'hpkg_' + str(self._pkg_name) + '.py'),
            'main': self._h_path.joinpath(self._pkg_name, '__main__.py'),
            'old_main': self._h_path.joinpath(self._pkg_name, 'old_main.py'),

        }

    def copy_package(self):

        try:
            copytree(
                self._orig_path, self._h_path, ignore=ignore_patterns(
                    *self._ignore_types))

            copytree(self._build_src['hpkg_components'],
                     self._build_dest['hpkg_components'])

            copy2(self._build_src['driver'], self._build_dest['driver'])

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
        copy2(Path(__file__).parent.absolute() / 'install_components' /
              'safe_main.py',
              self._h_path / self._pkg_name / '__main__.py')


test_builder = HpkgBuilder(Path('/Users/duane/dproj/xiangqigame'),
                           Path('/Users/duane/dproj/hpkgs/xiangqigame'))
test_builder.copy_package()
test_builder.move_orig_safe_main()
test_builder.write_pkg_name()
test_builder.copy_safe_main()
