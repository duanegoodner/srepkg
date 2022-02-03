from pathlib import Path
from typing import NamedTuple


class SrcPaths(NamedTuple):
    orig_pkg: Path
    name_template: Path
    hpkg_components: Path
    driver: Path
    main: Path


class DestPaths(NamedTuple):
    root: Path
    header: Path
    hpkg_components: Path
    driver: Path
    main: Path
    old_main: Path


def paths_builder(orig_pkg_path: Path, dest_path: Path):
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
