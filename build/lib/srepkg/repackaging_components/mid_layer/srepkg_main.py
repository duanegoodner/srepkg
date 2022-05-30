import sys
from pathlib import Path
from .pkg_names import inner_pkg_name
from .srepkg_control_components.srepkg_controller import SrepkgController


def main():

    srepkg_controller = SrepkgController.default(
        srepkg_root=Path(__file__).parent.absolute(),
        inner_pkg_name=inner_pkg_name)
    srepkg_controller.run_inner_pkg_main(*sys.argv[1:])


if __name__ == '__main__':
    main()
