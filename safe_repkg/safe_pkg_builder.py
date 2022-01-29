import os
import string
from shutil import copytree, ignore_patterns, copy2


class HpkgBuilder:
    _ignore_types = ['*.git', '*.gitignore', '*.idea', '*__pycache__']

    def __init__(self, stand_path: str, safe_path: str):
        self._stand_path = stand_path
        self._safe_path = safe_path
        self._pkg_name = os.path.basename(stand_path)

    def copy_package(self):
        try:
            copy_location = copytree(
                self._stand_path, self._safe_path, ignore=ignore_patterns(
                    *self._ignore_types))
            components_sub_dir = copytree(os.getcwd() +
                                          '/install_components/hpkg_components',
                                          copy_location + '/hpkg_components')

            copy2(os.getcwd() + '/install_components' + '/hpkg_driver.py',
                  self._safe_path + '/hpkg_' + os.path.basename(
                      self._stand_path) + '.py')

        except OSError:
            print("Error when attempting to copy")
            return

        return copy_location

    def move_orig_safe_main(self):
        os.rename(self._safe_path + '/' + os.path.basename(self._stand_path) +
                  '/__main__.py',
                  self._safe_path + '/' + os.path.basename(self._stand_path) +
                  '/old_main.py')

    def write_pkg_name(self):
        with open('package_name.py.template', 'r') as f:
            template_text = f.read()

        template = string.Template(template_text)

        substitutions = {
            'hpkg_path': self._safe_path
        }

        result = template.substitute(substitutions)

        with open(self._safe_path + '/hpkg_components/hpkg_header.py',
                  'w') as f:
            f.write(result)

    # TODO use pkgutils to properly access .template file

    def rebuild_safe_main(self):
        with open('safe_main.py.template', 'r') as f:
            template_text = f.read()

        template = string.Template(template_text)

        substitutions = {
            'cur_package_name': os.path.basename(self._stand_path)
        }

        result = template.substitute(substitutions)

        with open('new_safe_main.py', 'w') as f:
            f.write(result)

        os.rename('new_safe_main.py', self._safe_path + '/' +
                  os.path.basename(self._stand_path) + '/__main__.py')


test_builder = HpkgBuilder('/Users/duane/dproj/xiangqigame',
                           '/Users/duane/dproj/safe_repkg/xiangqigame')
test_builder.copy_package()
test_builder.move_orig_safe_main()
test_builder.write_pkg_name()
test_builder.rebuild_safe_main()
