"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""
import configparser
from pathlib import Path
from typing import NamedTuple, List
import srepkg.ep_console_script as epcs


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path
    entry_pts: List[epcs.CSEntry]


class SrePkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path


class BuilderDestPaths(NamedTuple):
    """Named tuple of paths where files are copied to during srepkg build"""
    root: Path
    srepkg: Path
    srepkg_components: Path
    srepkg_entry_module: Path
    srepkg_entry_points: Path
    srepkg_entry_points_init: Path
    srepkg_setup_cfg: Path
    srepkg_setup_py: Path
    srepkg_init: Path
    orig_pkg_setup_cfg: Path
    orig_pkg_setup_py: Path


class InstallCompSrcPaths(NamedTuple):
    srepkg_init: Path
    entry_module_template: Path
    entry_point_template: Path
    srepkg_components: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path


class BuilderSrcPaths(NamedTuple):
    """Named tuple of paths to be copied from during srepkg build"""
    entry_module_template: Path
    entry_point_template: Path
    srepkg_components: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path
    srepkg_init: Path


class PathCalculator:
    # ===== start of class variables =====
    install_components = Path(__file__).parent.absolute() / 'install_components'
    builder_src_paths = BuilderSrcPaths(
        srepkg_init=install_components / 'srepkg_init.py',
        entry_module_template=install_components / 'srepkg_entry.py.template',
        entry_point_template=install_components / 'entry_point.py.template',
        srepkg_components=install_components / 'srepkg_components',
        srepkg_setup_py=install_components / 'setup.py',
        srepkg_setup_cfg=install_components / 'setup_template.cfg'
    )

    srepkg_pkgs_dir = Path.home() / 'srepkg_pkgs'
    auto_srepkg_suffix = 'srnew'
    # ===== end of class variables =====

    def __init__(self, args):
        self._args = args

    @property
    def orig_pkg_path(self):
        return Path(self._args.orig_pkg)

    @property
    def srepkg_custom_name(self):
        return self._args.srepkg_name

    def validate_orig_pkg_path(self):
        if not self.orig_pkg_path.exists():
            print('Original package path not found.')
            exit(1)

    def validate_setup_cfg(self):
        if not (self.orig_pkg_path.parent.absolute() / 'setup.cfg').exists():
            print('Original package path not found.')
            exit(1)

    def get_orig_cfg_info(self):
        pkg_name = ''
        config = configparser.ConfigParser()

        root_path = self.orig_pkg_path.parent.absolute()
        try:
            config.read(root_path / 'setup.cfg')
        except (FileNotFoundError, KeyError, Exception):
            print(f'Unable to read setup.cfg file')
            exit(1)

        try:
            pkg_name = config['metadata']['name']
        except (KeyError, Exception):
            print('Unable to read package name')
            exit(1)

        cse_list = []
        try:
            ep_cs_list = config['options.entry_points']['console_scripts'] \
                .strip().splitlines()
            cse_list = [epcs.parse_cs_line(entry) for entry in ep_cs_list]
        except (TypeError, Exception):
            print('Unable to find any console script entry point for original'
                  'package')
            exit(1)

        return OrigPkgInfo(pkg_name=pkg_name, root_path=root_path,
                           entry_pts=cse_list)

    def get_sre_pkg_info(self, orig_pkg_info: OrigPkgInfo):

        if self.srepkg_custom_name:
            srepkg_name = self.srepkg_custom_name
        else:
            srepkg_name = orig_pkg_info.pkg_name + self.auto_srepkg_suffix

        dest_root_path = self.srepkg_pkgs_dir / (orig_pkg_info.pkg_name + \
                                                 '_as_' + srepkg_name)

        if dest_root_path.exists():
            print(f'Destination path {str(dest_root_path)} already exists')
            exit(1)

        return SrePkgInfo(pkg_name=srepkg_name, root_path=dest_root_path)

    def build_dest_paths(self, orig_pkg_info: OrigPkgInfo):

        srepkg_info = self.get_sre_pkg_info(orig_pkg_info)

        srepkg_root_path = srepkg_info.root_path
        srepkg_setup_py = srepkg_root_path / 'setup.py'
        srepkg_setup_cfg = srepkg_root_path / 'setup.cfg'

        srepkg_path = srepkg_root_path / srepkg_info.pkg_name
        srepkg_init = srepkg_path / '__init__.py'
        srepkg_components = srepkg_path / 'srepkg_components'
        srepkg_entry_points = srepkg_path / 'srepkg_entry_points'
        orig_setup_cfg = srepkg_path / 'setup.cfg'
        orig_setup_py = srepkg_path / 'setup.py'

        srepkg_entry_points_init = srepkg_entry_points / '__init__.py'

        srepkg_entry_module = srepkg_components / 'entry_points.py'

        return BuilderDestPaths(
            root=srepkg_info.root_path,
            srepkg=srepkg_path,
            srepkg_components=srepkg_components,
            srepkg_entry_module=srepkg_entry_module,
            srepkg_entry_points=srepkg_entry_points,
            srepkg_entry_points_init=srepkg_entry_points_init,
            srepkg_setup_cfg=srepkg_setup_cfg,
            srepkg_init=srepkg_init,
            srepkg_setup_py=srepkg_setup_py,
            orig_pkg_setup_cfg=orig_setup_cfg,
            orig_pkg_setup_py=orig_setup_py
        )


# def calc_root_paths_from(args):
#     """
#     Converts args (typically obtained from command line + argparse) into
#     Path objects referencing orig package and srepackage root paths.
#
#     :param args: Namespace with arguments parsed from command line input
#     :return: tuple of Paths (orig_pkg_path, dest_path)
#     """
#
#     orig_pkg_path = Path(args.orig_pkg)
#     if args.srepkg_name:
#         srepkg_name = args.srepkg_name
#     else:
#         srepkg_name = orig_pkg_path.name + 'srnew'
#
#     dest_path = Path.home() / 'srepkg_pkgs' / \
#                 (orig_pkg_path.name + '_as_' + str(srepkg_name)) / srepkg_name
#
#     return orig_pkg_path, dest_path
#
#
# def validate_root_paths(orig_pkg_path: Path, dest_path: Path):
#     """
#     Confirms that original package path exists, no file exists at destination,
#     and that the destination path is not a sub-path of the original.
#
#     :param orig_pkg_path: Path object referencing original package
#     :param dest_path: Path object referencing root of repackaged app.
#     """
#
#     if not orig_pkg_path.exists():
#         print(str(orig_pkg_path), ' not found.')
#         exit(1)
#     if dest_path.exists():
#         print(str(dest_path), ' already exists.')
#         exit(1)
#
#
# def validate_orig_pkg(orig_pkg_path: Path):
#     if not (orig_pkg_path.parent.absolute() / 'setup.cfg').exists():
#         print(f'No setup.cfg file found for {orig_pkg_path}')
#         exit(1)
#
#
# def read_orig_pkg_info(orig_pkg_path: Path):
#     orig_config = configparser.ConfigParser()
#     orig_config.read(orig_pkg_path.parent.absolute() / 'setup.cfg')
#
#     try:
#         orig_pkg_name = orig_config['metadata']['name']
#     except (KeyError, Exception):
#         print('Unable to obtain package name from original package setup.cfg.')
#
#         try:
#             orig_pkg_name = orig_pkg_path.name
#             print('Obtained original package name from directory name.'
#                   'Warning: If directory name does not match installed name,'
#                   'will be unable to run inner package.')
#         except (FileNotFoundError, Exception):
#             print(
#                 'Also unable to obtain original package name from directory'
#                 'name')
#             exit(1)
#
#     cse_list = []
#     try:
#         ep_cs_list = orig_config['options.entry_points']['console_scripts'] \
#             .strip().splitlines()
#         cse_list = [epcs.parse_cs_line(entry) for entry in ep_cs_list]
#     except (TypeError, Exception):
#         print('Unable to find any console script entry point for original'
#               'package')
#         exit(1)
#
#     return OrigPkgInfo(pkg_name=orig_pkg_name,
#                        container_path=orig_pkg_path.parent,
#                        inner_pkg_path=orig_pkg_path,
#                        entry_pts=cse_list)
#
#
# def create_builder_paths(orig_pkg_path: Path, dest_path: Path):
#     """
#     Determines BuilderSrcPaths and BuilderDestPaths (each containing multiple
#     paths) from root paths of original package and srepkg destination.
#
#     :param orig_pkg_path: Path object referencing original package
#     :param dest_path: Path object referencing folder where srepkg will be built
#     :return: (BuilderSrcPaths, BuilderDestPaths) tuple
#     """
#     h_src_root = Path(__file__).parent.absolute()
#     install_components = h_src_root / 'install_components'
#     pkg_name = orig_pkg_path.name
#
#     src_paths = BuilderSrcPaths(
#         orig_pkg_container=orig_pkg_path.parent.absolute(),
#         orig_pkg=orig_pkg_path,
#         orig_setup_cfg=orig_pkg_path.parent / 'setup.cfg',
#         init=install_components / 'srepkg_init.py',
#         name_template=install_components / 'pkg_name.py.template',
#         entry_template=install_components / 'srepkg_entry.py.template',
#         entry_point_template=install_components / 'entry_point.py.template',
#         srepkg_components=install_components / 'srepkg_components',
#         setup_py_outer=install_components / 'setup.py',
#         setup_cfg_outer=install_components / 'setup_template.cfg'
#     )
#
#     h_paths = BuilderDestPaths(
#         root=dest_path,
#         inner_pkg_container=dest_path.parent,
#         setup_py_outer=dest_path.parent / 'setup.py',
#         init=dest_path / '__init__.py',
#         header=dest_path / 'srepkg_components' / 'srepkg_header.py',
#         entry=dest_path / 'srepkg_components' / 'srepkg_entry.py',
#         entry_points=dest_path / 'srepkg_entry_points',
#         srepkg_components=dest_path / 'srepkg_components',
#         setup_cfg_outer=dest_path.parent / 'setup.cfg',
#         setup_py_inner=dest_path / 'setup.py',
#         setup_cfg_inner=dest_path / 'setup.cfg'
#     )
#
#     return src_paths, h_paths
