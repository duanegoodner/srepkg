from pathlib import Path
from ..srepkg_control_components.entry_point_runner import run_entry_funct


entry_command = Path(__file__).name[:-3]


def entry_funct():
    run_entry_funct(entry_command)
