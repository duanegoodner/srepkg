import argparse
from hpkg_components import hpkg_installer
from hpkg_components.hpkg_header import hpkg_src


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('pkg_args', nargs='*')
    args = parser.parse_args()

    hpkg_controller = hpkg_installer.install(hpkg_src)
    hpkg_controller.upgrade_pip().install_utilities('wheel')\
        .install_inner_pkg().post_install_cleanup()

    hpkg_controller.run_inner_pkg(*args.pkg_args)


if __name__ == '__main__':
    main()
