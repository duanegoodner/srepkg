import argparse
import subprocess
import sys
from .pkg_names import inner_pkg_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--called_by_safe_pkg', required=False,
                        action="store_true")
    parser.add_argument('venv_pkg_path')
    parser.add_argument('pkg_args', nargs='*')
    args = parser.parse_args()

    if args.called_by_safe_pkg:
        subprocess.call([sys.executable, args.venv_pkg_path +
                         f'/{inner_pkg_name}/orig_main.py'] + args.pkg_args)


if __name__ == '__main__':
    main()
