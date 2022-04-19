import sys
from pathlib import Path
from .pkg_names import inner_pkg_name
from .srepkg_control_components.srepkg_controller import HpkgController


def main():

    hpkg_controller = HpkgController.for_env_builder(
        Path(__file__).parent.absolute() / inner_pkg_name)

    hpkg_controller.run_inner_pkg(*sys.argv[1:])


if __name__ == '__main__':
    main()