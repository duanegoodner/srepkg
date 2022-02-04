"""
Provides an entry point for running an H-packaged app from command line. Will
be renamed to <orig_package_name>_hpkg.py upon copying. Note that this file
needs to be run as a script, not as a package.
"""

import argparse
from pathlib import Path
from repackaged_app.hpkg_components.hpkg_header import pkg_name
from repackaged_app.hpkg_components.hpkg_controller import HpkgController


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
