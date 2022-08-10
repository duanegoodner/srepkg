import subprocess
import sys
from pathlib import Path
# from .entry_point_runner import run_entry_funct


# entry_command = Path(__file__).name[:-3]
#
#
# def entry_funct():
#     run_entry_funct(entry_command)

def entry_funct():
    entry_command = Path(__file__).name[:-3]
    pkg_args = sys.argv[1:]
    venv_bin = Path(__file__).parent.parent.absolute() / "srepkg_venv" / "bin"
    subprocess.call([venv_bin / entry_command, *pkg_args])



