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
    main_outer: Path
    main_inner: Path
    setup_template: Path
    init: Path


class DestPaths(NamedTuple):
    """Named tuple of paths where files are copied to during hpkg build"""
    root: Path
    header: Path
    hpkg_components: Path
    main_outer: Path
    main_inner: Path
    old_main: Path
    setup_outer: Path
    setup_inner: Path
    init: Path



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
    h_pkg_name = pkg_name + '_hpkg'

    src_paths = SrcPaths(
        orig_pkg=orig_pkg_path.parent.absolute(),
        init=install_components / 'dest_init.py',
        name_template=install_components / 'pkg_name.py.template',
        hpkg_components=install_components / 'hpkg_components',
        main_outer=install_components / 'main_outer.py.template',
        main_inner=install_components / 'main_inner.py',
        setup_template=install_components / 'setup.py.template'
    )

    h_paths = DestPaths(
        root=dest_path,
        setup_outer=dest_path.parent / 'setup.py',
        init=dest_path / '__init__.py',
        header=dest_path / 'hpkg_components' / 'hpkg_header.py',
        hpkg_components=dest_path / 'hpkg_components',
        main_outer=dest_path / '__main__.py',
        main_inner=dest_path / pkg_name / '__main__.py',
        setup_inner=dest_path / 'setup.py',
        old_main=dest_path / pkg_name / 'old_main.py'
    )

    return src_paths, h_paths
