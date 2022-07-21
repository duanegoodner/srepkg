import subprocess
import sys
from pathlib import Path


def run_entry_funct(inner_entry_arg: str):
    pkg_args = sys.argv[1:]
    venv_bin = Path(__file__).parent.parent.absolute() / "srepkg_venv" / "bin"
    subprocess.call([venv_bin / inner_entry_arg, *pkg_args])
