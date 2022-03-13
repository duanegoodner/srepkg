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
    srepkg_entry_points: Path
    srepkg_entry_points_init: Path
    inner_pkg_installer: Path
    manifest: Path
    pkg_names_outer: Path
    pkg_names_mid: Path
    pkg_names_inner: Path
    srepkg_setup_cfg: Path
    srepkg_setup_py: Path
    srepkg_init: Path
    orig_pkg_setup_cfg: Path
    orig_pkg_setup_py: Path
    main_outer: Path
    main_inner: Path
    main_inner_orig: Path



class BuilderSrcPaths(NamedTuple):
    """Named tuple of paths to be copied from during srepkg build"""
    entry_point_template: Path
    inner_pkg_installer: Path
    manifest_template: Path
    pkg_names_template: Path
    srepkg_components: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path
    srepkg_init: Path
    main_outer: Path
    main_inner: Path


class PathCalculator:
    # ===== start of class variables =====
    install_components = Path(__file__).parent.absolute() / 'install_components'
    builder_src_paths = BuilderSrcPaths(
        srepkg_init=install_components / 'srepkg_init.py',
        entry_point_template=install_components / 'entry_point_template.py',
        inner_pkg_installer=install_components / 'inner_pkg_installer.py',
        manifest_template=install_components / 'MANIFEST.in.template',
        pkg_names_template=install_components / 'pkg_names.py.template',
        srepkg_components=install_components / 'srepkg_components',
        srepkg_setup_py=install_components / 'setup.py',
        srepkg_setup_cfg=install_components / 'setup_template.cfg',
        main_outer=install_components / 'main_outer.py',
        main_inner=install_components / 'main_inner.py'
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

        dest_root_path = self.srepkg_pkgs_dir / (orig_pkg_info.pkg_name +
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
        inner_pkg_installer = srepkg_root_path / 'inner_pkg_installer.py'
        manifest = srepkg_root_path / 'MANIFEST.in'
        pkg_names_outer = srepkg_root_path / 'pkg_names.py'
        srepkg_path = srepkg_root_path / srepkg_info.pkg_name
        srepkg_init = srepkg_path / '__init__.py'
        pkg_names_mid = srepkg_path / 'pkg_names.py'
        srepkg_components = srepkg_path / 'srepkg_components'
        srepkg_entry_points = srepkg_path / 'srepkg_entry_points'
        orig_setup_cfg = srepkg_path / 'setup.cfg'
        orig_setup_py = srepkg_path / 'setup.py'
        main_outer = srepkg_path / '__main__.py'
        srepkg_entry_points_init = srepkg_entry_points / '__init__.py'

        inner_pkg = srepkg_path / orig_pkg_info.pkg_name
        pkg_names_inner = inner_pkg / 'pkg_names.py'
        main_inner = inner_pkg / '__main__.py'
        main_inner_orig = inner_pkg / 'orig_main.py'


        return BuilderDestPaths(
            root=srepkg_info.root_path,
            srepkg=srepkg_path,
            srepkg_components=srepkg_components,
            srepkg_entry_points=srepkg_entry_points,
            srepkg_entry_points_init=srepkg_entry_points_init,
            srepkg_setup_cfg=srepkg_setup_cfg,
            inner_pkg_installer=inner_pkg_installer,
            manifest=manifest,
            pkg_names_outer=pkg_names_outer,
            pkg_names_mid=pkg_names_mid,
            pkg_names_inner=pkg_names_inner,
            srepkg_init=srepkg_init,
            srepkg_setup_py=srepkg_setup_py,
            orig_pkg_setup_cfg=orig_setup_cfg,
            orig_pkg_setup_py=orig_setup_py,
            main_outer=main_outer,
            main_inner=main_inner,
            main_inner_orig=main_inner_orig
        )


