import sys
from pathlib import Path
from .srepkg_controller import SrepkgController
from ..pkg_names import inner_pkg_name


def run_entry_funct(inner_entry_arg: str):
    pkg_args = sys.argv[1:]
    srepkg_controller = SrepkgController.default(
        srepkg_root=Path(__file__).parent.parent.absolute(),
        inner_pkg_name=inner_pkg_name)
    srepkg_controller.run_inner_pkg_entry_point(inner_entry_arg, *pkg_args)
