"""
Contains classes and function for determining source and destination paths
of directories and files copied/built when creating a Hpkg.
"""

from pathlib import Path
from typing import NamedTuple


class SrcPaths(NamedTuple):
    """Named tuple of paths to be copied from during hpkg build"""
    orig_pkg: Path
    name_template: Path
    hpkg_components: Path
    driver: Path
    main: Path


class DestPaths(NamedTuple):
    """Named tuple of paths where files are copied to during hpkg build"""
    root: Path
    header: Path
    hpkg_components: Path
    driver: Path
    main: Path
    old_main: Path


def paths_builder(orig_pkg_path: Path, dest_path: Path):
    """
    Determines SrcPaths and DestPaths (each containing multiple paths) based on
    single path of original package and single path of hpkg destination.
    :param orig_pkg_path: Path object referencing original package
    :param dest_path: Path object of folder where hpkg will be built
    :return: (SrcPaths, DestPaths) tuple
    """
    h_src_root = Path(__file__).parent.absolute()
    install_components = h_src_root / 'install_components'
    pkg_name = orig_pkg_path.name

    src_paths = SrcPaths(
        orig_pkg=orig_pkg_path.parent.absolute(),
        name_template=install_components / 'pkg_name.py.template',
        hpkg_components=install_components / 'hpkg_components',
        driver=install_components / 'hpkg_driver.py',
        main=install_components / 'safe_main.py'
    )

    h_paths = DestPaths(
        root=dest_path,
        header=dest_path / 'hpkg_components' / 'hpkg_header.py',
        hpkg_components=dest_path / 'hpkg_components',
        driver=dest_path / (str(pkg_name) + '_hpkg.py'),
        main=dest_path / pkg_name / '__main__.py',
        old_main=dest_path / pkg_name / 'old_main.py'
    )

    return src_paths, h_paths
