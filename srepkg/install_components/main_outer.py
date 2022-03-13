import argparse
from pathlib import Path
from .pkg_names import inner_pkg_name
from .srepkg_components.srepkg_controller import HpkgController


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('pkg_args', nargs='*')
    args = parser.parse_args()

    hpkg_controller = HpkgController.for_env_builder(
        Path(__file__).parent.absolute() / inner_pkg_name)

    hpkg_controller.run_inner_pkg(*args.pkg_args)


if __name__ == '__main__':
    main()