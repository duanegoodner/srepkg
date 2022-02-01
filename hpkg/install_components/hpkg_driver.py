import argparse
from pathlib import Path
from hpkg_components.hpkg_header import pkg_name
from hpkg_components.hpkg_controller import HpkgController


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('pkg_args', nargs='*')
    args = parser.parse_args()

    hpkg_controller = HpkgController.for_env_builder(
        Path(__file__).parent.absolute() / pkg_name)
    hpkg_controller.build_venv().upgrade_pip().install_utilities('wheel')\
        .install_inner_pkg().post_install_cleanup()

    hpkg_controller.run_inner_pkg(*args.pkg_args)


if __name__ == '__main__':
    main()
