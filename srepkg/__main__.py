"""
Entry point for the srepkg application. Command line syntax:
$ python_interpreter_path srepkg -m orig_pkg_path [srepkg_name]
"""

import srepkg.sre_packager as sre_packager


if __name__ == '__main__':
    sre_packager.main()
