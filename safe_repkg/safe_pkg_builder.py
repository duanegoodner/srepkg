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

    def copy_package(self):

        try:
            copytree(
                self._orig_path, self._h_path, ignore=ignore_patterns(
                    *self._ignore_types))

            copytree(Path(__file__).parent.absolute() /
                     'install_components' /
                     'hpkg_components',
                     self._h_path /
                     'hpkg_components')

            copy2(Path(__file__).parent.absolute() / 'install_components' /
                  'hpkg_driver.py',
                  self._h_path / ('hpkg_' + str(self._pkg_name) + '.py'))

        except OSError:
            print("Error when attempting to copy")
            exit(1)

    def move_orig_safe_main(self):
        (self._h_path / self._pkg_name / '__main__.py').rename(
            self._h_path / self._pkg_name / 'old_main.py')

    def write_pkg_name(self):

        # TODO fix to maek compatbile with Path object
        with (Path(__file__).parent.absolute() /
              'package_name.py.template').open(mode='r') as f:
            template_text = f.read()

        template = string.Template(template_text)

        substitutions = {
            'hpkg_path': self._h_path
        }

        result = template.substitute(substitutions)

        with Path(self._h_path / 'hpkg_components' / 'hpkg_header.py')\
                .open(mode='w') as f:
            f.write(result)

    def rebuild_safe_main(self):
        with (Path(__file__).parent.absolute() /
              'safe_main.py.template').open(mode='r') as f:
            template_text = f.read()

        template = string.Template(template_text)

        substitutions = {
            'cur_package_name': os.path.basename(self._orig_path)
        }

        result = template.substitute(substitutions)

        with (self._h_path / self._pkg_name / '__main__.py')\
                .open(mode='w') as f:
            f.write(result)


test_builder = HpkgBuilder(Path('/Users/duane/dproj/xiangqigame'),
                           Path('/Users/duane/dproj/safe_repkg/xiangqigame'))
test_builder.copy_package()
test_builder.move_orig_safe_main()
test_builder.write_pkg_name()
test_builder.rebuild_safe_main()
