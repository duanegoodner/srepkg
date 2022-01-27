import os
import string
from shutil import copytree, ignore_patterns


class SafePkgBuilder:

    def __init__(self, stand_path: str, safe_path: str):
        self._stand_path = stand_path
        self._safe_path = safe_path

    def copy_package(self):
        try:
            copy_location = copytree(
                self._stand_path, self._safe_path, ignore=ignore_patterns(
                    '*.git', '*.gitignore', '*.idea', '*__pycache__'))
        except OSError:
            print("Error when attempting to copy")
            return

        return copy_location

    def move_orig_safe_main(self):
        os.rename(self._safe_path + '/' + os.path.basename(self._stand_path) +
                  '/__main__.py',
                  self._safe_path + '/' + os.path.basename(self._stand_path) +
                  '/old_main.py')

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


test_builder = SafePkgBuilder('/Users/duane/dproj/xiangqigame',
                              '/Users/duane/dproj/xiangqigame_safe')
test_builder.copy_package()
test_builder.move_orig_safe_main()
test_builder.rebuild_safe_main()


