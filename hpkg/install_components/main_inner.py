"""
Entry point to the module being rebuilt as a Hpkg. File gets renamed to
__main__.py when copied.
"""

import argparse
import subprocess
import sys
from pathlib import Path
# from hpkg_components.hpkg_header import pkg_name


pkg_name = Path(__file__).parent.absolute().name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--called_by_safe_pkg', required=False,
                        action="store_true")
    parser.add_argument('venv_pkg_path')
    parser.add_argument('pkg_args', nargs='*')
    args = parser.parse_args()

    if args.called_by_safe_pkg:
        subprocess.call([sys.executable, args.venv_pkg_path +
                         f'/{pkg_name}/old_main.py'] + args.pkg_args)


if __name__ == '__main__':
    main()
