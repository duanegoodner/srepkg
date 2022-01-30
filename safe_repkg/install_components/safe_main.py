import argparse
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--called_by_safe_pkg', required=False, action="store_true")
parser.add_argument('venv_pkg_path')
parser.add_argument('pkg_args', nargs='*')
args = parser.parse_args()

package_name = Path(__file__).parent.name

if __name__ == '__main__' and args.called_by_safe_pkg:
    subprocess.call([sys.executable, args.venv_pkg_path +
                     f'/{package_name}/old_main.py'] + args.pkg_args)