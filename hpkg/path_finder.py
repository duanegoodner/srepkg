from pathlib import Path
from typing import NamedTuple


class SrcPaths(NamedTuple):
    name_template: Path
    hpkg_components: Path
    driver: Path
    main: Path


def src_path_builder():
    install_components = Path(__file__).parent.absolute() / 'install_components'

    return SrcPaths(
        name_template=install_components / 'pkg_name.py.template',
        hpkg_components=install_components / 'hpkg_components',
        driver=install_components / 'hpkg_driver.py',
        main=install_components / 'safe_main.py'
    )


class DestPaths(NamedTuple):
    header: Path
    hpkg_components: Path
    driver: Path
    main: Path
    old_main: Path


def dest_path_builder(dest_path: Path):
    pkg_name = dest_path.name

    return DestPaths(
        header=dest_path / 'hpkg_components' / 'hpkg_header.py',
        hpkg_components=dest_path / 'hpkg_components',
        driver=dest_path / pkg_name + '_hpkg.py',
        main=dest_path / pkg_name / '__main__.py',
        old_main=dest_path / pkg_name / 'old_main.py'
    )



