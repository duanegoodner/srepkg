from pathlib import Path
from ..srepkg_control_components.entry_point_runner import run_entry_funct

# TODO use Path.suffix and drop that instead of assuming suffix is 3 chars
entry_command = Path(__file__).name[:-3]


def entry_funct():
    run_entry_funct(entry_command)
