"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""
import configparser
from pathlib import Path
from typing import NamedTuple, List
import ep_console_script as epcs


def calc_root_paths_from(args):
    """
    Converts args (typically obtained from command line + argparse) into
    Path objects referencing orig package and srepackage root paths.

    :param args: Namespace with arguments parsed from command line input
    :return: tuple of Paths (orig_pkg_path, dest_path)
    """

    orig_pkg_path = Path(args.orig_pkg_path)
    if args.srepkg_name:
        srepkg_name = args.srepkg_name
    else:
        srepkg_name = orig_pkg_path.name + 'srnew'

    dest_path = Path.home() / 'srepkg_pkgs' / \
                (orig_pkg_path.name + '_as_' + str(srepkg_name)) / srepkg_name

    return orig_pkg_path, dest_path


def validate_root_paths(orig_pkg_path: Path, dest_path: Path):
    """
    Confirms that original package path exists, no file exists at destination,
    and that the destination path is not a sub-path of the original.

    :param orig_pkg_path: Path object referencing original package
    :param dest_path: Path object referencing root of repackaged app.
    """

    if not orig_pkg_path.exists():
        print(str(orig_pkg_path), ' not found.')
        exit(1)
    if dest_path.exists():
        print(str(dest_path), ' already exists.')
        exit(1)


def validate_orig_pkg(orig_pkg_path: Path):
    if not (orig_pkg_path.parent.absolute() / 'setup.cfg').exists():
        print(f'No setup.cfg file found for {orig_pkg_path}')
        exit(1)


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    container_path: Path
    entry_pts: List[epcs.CSEntry]


def read_orig_pkg_info(orig_pkg_path: Path):
    orig_config = configparser.ConfigParser()
    orig_config.read(orig_pkg_path.parent.absolute() / 'setup.cfg')

    orig_pkg_name = ''
    try:
        orig_pkg_name = orig_config['metadata']['name']
    except (KeyError, Exception):
        print('Unable to obtain package name from original package setup.cfg.')
        pass

    try:
        orig_pkg_name = orig_pkg_path.name
        print('Obtained original package name from directory name.'
              'Warning: If directory name does not match installed name, will'
              'be unable to run inner package.')
    except (FileNotFoundError, Exception):
        print('Also unable to obtain original package name from directory name')
        exit(1)

    cse_list = []
    try:
        ep_cs_list = orig_config['options.entry_points']['console_scripts'] \
            .strip().splitlines()
        cse_list = [epcs.parse_cs_line(entry) for entry in ep_cs_list]
    except (TypeError, Exception):
        print('Unable to find any console script entry point for original'
              'package')
        exit(1)

    return OrigPkgInfo(pkg_name=orig_pkg_name,
                       container_path=orig_pkg_path.parent,
                       entry_pts=cse_list)



class BuilderSrcPaths(NamedTuple):
    """Named tuple of paths to be copied from during srepkg build"""
    orig_pkg_container: Path
    orig_pkg: Path
    orig_setup_cfg: Path
    name_template: Path
    entry_template: Path
    entry_point_template: Path
    srepkg_components: Path
    setup_py_outer: Path
    setup_cfg_outer: Path
    init: Path


class BuilderDestPaths(NamedTuple):
    """Named tuple of paths where files are copied to during srepkg build"""
    root: Path
    inner_pkg_container: Path
    header: Path
    entry: Path
    entry_points: Path
    srepkg_components: Path
    setup_cfg_outer: Path
    setup_cfg_inner: Path
    setup_py_outer: Path
    setup_py_inner: Path
    init: Path


def create_builder_paths(orig_pkg_path: Path, dest_path: Path):
    """
    Determines BuilderSrcPaths and BuilderDestPaths (each containing multiple
    paths) from root paths of original package and srepkg destination.

    :param orig_pkg_path: Path object referencing original package
    :param dest_path: Path object referencing folder where srepkg will be built
    :return: (BuilderSrcPaths, BuilderDestPaths) tuple
    """
    h_src_root = Path(__file__).parent.absolute()
    install_components = h_src_root / 'install_components'
    pkg_name = orig_pkg_path.name

    src_paths = BuilderSrcPaths(
        orig_pkg_container=orig_pkg_path.parent.absolute(),
        orig_pkg=orig_pkg_path,
        orig_setup_cfg=orig_pkg_path.parent / 'setup.cfg',
        init=install_components / 'srepkg_init.py',
        name_template=install_components / 'pkg_name.py.template',
        entry_template=install_components / 'srepkg_entry.py.template',
        entry_point_template=install_components / 'entry_point.py.template',
        srepkg_components=install_components / 'srepkg_components',
        setup_py_outer=install_components / 'setup.py',
        setup_cfg_outer=install_components / 'setup_template.cfg'
    )

    h_paths = BuilderDestPaths(
        root=dest_path,
        inner_pkg_container=dest_path.parent,
        setup_py_outer=dest_path.parent / 'setup.py',
        init=dest_path / '__init__.py',
        header=dest_path / 'srepkg_components' / 'srepkg_header.py',
        entry=dest_path / 'srepkg_components' / 'srepkg_entry.py',
        entry_points=dest_path / 'srepkg_entry_points',
        srepkg_components=dest_path / 'srepkg_components',
        setup_cfg_outer=dest_path.parent / 'setup.cfg',
        setup_py_inner=dest_path / 'setup.py',
        setup_cfg_inner=dest_path / 'setup.cfg'
    )

    return src_paths, h_paths
