import sys
from pathlib import Path
from .srepkg_controller import HpkgController
from ..pkg_names import inner_pkg_name


def run_entry_funct(inner_entry_arg: str):
    pkg_args = sys.argv[1:]
    hpkg_controller = HpkgController.for_env_builder(
        Path(__file__).parent.parent.absolute() / inner_pkg_name)
    hpkg_controller.inner_pkg_entry_point(inner_entry_arg, *pkg_args)
