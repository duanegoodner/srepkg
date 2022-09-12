import configparser
import logging
import re
import subprocess
import sys
import tempfile
import venv
from datetime import datetime
from types import SimpleNamespace
from pathlib import Path
from typing import Dict

try:
    from .yaspin_status import yaspin_logging as show_status
except(ModuleNotFoundError, ImportError):
    from .simple_status import simple_status as show_status


class IPILogging:

    @staticmethod
    def confirm_setup():

        custom_logger_names = [logging.getLogger(ref).name for ref in
                               logging.root.manager.loggerDict]

        console_logger_info = {
            "std_err": (logging.DEBUG, sys.stderr),
            "std_out": (logging.DEBUG, sys.stdout)
        }

        if not all([key in custom_logger_names for key in console_logger_info]):

            log_dir = tempfile.TemporaryDirectory()
            filename = f"srepkg_log_" \
                       f"{datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f')}.log"
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
                filename=f"{str(log_dir.name)}/{filename}",
                filemode="w"
            )

            for logger_name, handler_info in console_logger_info.items():
                if logger_name not in custom_logger_names:
                    logger = logging.getLogger(logger_name)
                    handler = logging.StreamHandler(stream=handler_info[1])
                    handler.setLevel(level=handler_info[0])
                    logger.addHandler(handler)


class SitePackagesInspector:

    def __init__(self, site_pkgs: Path):
        self._site_pkgs = site_pkgs

    @staticmethod
    def _get_val_from_line(data_key: str, line: str):
        data_regex = r"^" + re.escape(data_key) + r": [\d.a-zA-Z-_]+\s*$"
        if re.search(data_regex, line, re.IGNORECASE):
            return line[(len(data_key) + 2):].strip()

    def _get_val_from_file(self, data_key: str, metadata_file: Path):
        with metadata_file.open(mode="r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                value = self._get_val_from_line(data_key, line)
                if value:
                    return value

    def _get_metadata_val_from_dist_info_dir(
            self, data_key: str, dist_info_dir: Path):
        for item in dist_info_dir.iterdir():
            if item.name == "METADATA":
                return self._get_val_from_file(
                    data_key=data_key, metadata_file=item)

    def get_pkg_version(self, pkg_name: str):
        for item in self._site_pkgs.iterdir():
            if item.suffix == ".dist-info":
                found_pkg_name = self._get_metadata_val_from_dist_info_dir(
                    data_key="Name", dist_info_dir=item)
                if found_pkg_name == pkg_name:
                    return self._get_metadata_val_from_dist_info_dir(
                        data_key="Version", dist_info_dir=item)


class PyVersion:

    def __init__(self, version_str: str):
        self._version_str = version_str

    @property
    def major(self):
        major_pattern = r"((?<=^)[\d]{1,2}(?=\.))"
        return int(re.findall(major_pattern, self._version_str)[0])

    @property
    def minor(self):
        minor_pattern = r"((?<=\.)[\d]{1,2}(?=\.))"
        return int(re.findall(minor_pattern, self._version_str)[0])

    @property
    def micro(self):
        micro_pattern = r"((?<=\.)[\d]{1,2}$)"
        return int(re.findall(micro_pattern, self._version_str)[0])


class CustomVenvBuilder(venv.EnvBuilder):
    def __init__(self):
        super().__init__(with_pip=True)
        self._context = SimpleNamespace()
        self._site_pkgs = None
        self._version_info = sys.version_info

    @property
    def context(self):
        return self._context

    @property
    def version_info(self):
        return self._version_info

    @property
    def site_pkgs(self):
        return self._site_pkgs

    def post_setup(self, context) -> None:
        subprocess.call([
            context.env_exe, "-m", "pip", "install", "--upgrade", "pip",
            "--quiet"])
        subprocess.call([
            context.env_exe, "-m", "pip", "install", "--upgrade", "setuptools",
            "--quiet"])
        subprocess.call(
            [context.env_exe, "-m", "pip", "install", "--upgrade", "wheel",
             "--quiet"])

        self._site_pkgs = Path(
            f"{context.env_dir}/lib/python{sys.version_info.major}."
            f"{sys.version_info.minor}/site-packages")
        self._context = context


class VenvManager:
    def __init__(self, context):
        self._context = context
        self._pyvenv_cfg = configparser.ConfigParser()
        with self._cfg_path.open(mode='r') as cfg_file:
            self._pyvenv_cfg.read_string("[pyvenv_cfg]\n" + cfg_file.read())
        self._console_scripts = []

    @property
    def _env_dir(self) -> Path:
        return Path(self._context.env_dir)

    @property
    def _env_exe(self):
        return Path(self._context.env_exe)

    @property
    def _cfg_path(self):
        return Path(self._context.cfg_path)

    @property
    def _version(self):
        return PyVersion(self._pyvenv_cfg.get("pyvenv_cfg", "version"))

    @property
    def _site_packages(self):

        return self._env_dir / f"lib/python{str(self._version.major)}." \
                               f"{str(self._version.minor)}" / "site-packages"

    @property
    def pypa_pkg_versions(self) -> Dict[str, str]:
        pypa_pkgs = ["pip", "setuptools", "wheel"]
        site_pkgs_inspector = SitePackagesInspector(self._site_packages)
        return {pkg: site_pkgs_inspector.get_pkg_version(pkg) for pkg in
                pypa_pkgs}

    @property
    def _relative_shebang(self):
        return '#!/bin/sh\n"exec" "`dirname $0`/python" "$0" "$@"\n'

    def pip_install(self, *args):
        subprocess.call(
            [self._env_exe, "-m", "pip", "install"] + [*args]
        )

        return self

    def _get_console_scripts(self, info_file: Path):
        config = configparser.ConfigParser()
        config.read(info_file)
        if "console_scripts" in config.sections():
            self._console_scripts += dict(
                config.items("console_scripts")
            ).keys()

    def _gather_all_console_scripts(self):
        self._console_scripts = []
        for path in self._site_packages.iterdir():
            if path.is_dir() and (
                    path.name.endswith(".dist-info")
                    or path.name.endswith(".egg-info")
            ):
                if (path / "entry_points.txt").exists():
                    self._get_console_scripts(path / "entry_points.txt")

    def _update_cs_shebang(self, cs_path: Path):
        if cs_path.exists():
            with cs_path.open(mode="r+") as f:
                first_line = f.readline()
                second_line = f.readline()
                if first_line + second_line != self._relative_shebang:
                    remaining_lines = f.read()
                    f.seek(0)
                    f.write(
                        self._relative_shebang + second_line + remaining_lines
                    )
                    f.truncate()

    def _update_all_cs_shebangs(self):

        for console_script in self._console_scripts:
            self._update_cs_shebang(self._env_dir / "bin" / console_script)

    def _update_rogue_pip_cs_shebang(self):
        pip_cs_without_dist_info = self._env_dir / "bin" / \
                                   f"pip{str(self._version.major)}.{str(self._version.minor)}"
        if pip_cs_without_dist_info.exists():
            self._update_cs_shebang(pip_cs_without_dist_info)

    def rewire_shebangs(self):
        self._gather_all_console_scripts()
        self._update_all_cs_shebangs()
        self._update_rogue_pip_cs_shebang()


class InnerPkgCfgReader:
    def __init__(self, inner_pkg_cfg: Path):
        self._inner_pkg_cfg_file = inner_pkg_cfg
        self._inner_pkg_cfg = configparser.ConfigParser()
        self._inner_pkg_cfg.read(self._inner_pkg_cfg_file)

    @property
    def srepkg_name(self):
        return self._inner_pkg_cfg.get("metadata", "srepkg_name")

    @property
    def dist_dir(self):
        return self._inner_pkg_cfg.get("metadata", "dist_dir")

    @property
    def sdist_src(self):
        return self._inner_pkg_cfg.get("metadata", "sdist_src")


class InnerPkgInstaller:
    def __init__(
            self,
            venv_path: Path,
            orig_pkg_dist: Path):
        self._venv_path = venv_path
        self._orig_pkg_dist = orig_pkg_dist

    @show_status(
        base_logger=logging.getLogger(__name__),
        std_out_logger=logging.getLogger(f"std_out.{__name__}"))
    def build_venv(self, status_msg_kwarg):
        env_builder = CustomVenvBuilder()
        env_builder.create(self._venv_path)

        return env_builder.context

    @show_status(
        base_logger=logging.getLogger(__name__),
        std_out_logger=logging.getLogger(f"std_out.{__name__}"))
    def install_orig_pkg_in_venv(self, status_msg_kwarg, venv_manager):
        venv_manager.pip_install(
            self._orig_pkg_dist, "--quiet"
        ).rewire_shebangs()

    def iso_install_inner_pkg(self):
        IPILogging.confirm_setup()
        venv_context = self.build_venv(status_msg_kwarg="Creating virtual env")
        venv_manager = VenvManager(context=venv_context)

        pkg_versions = "\n".join([f"\t• {pkg}=={version}" for pkg, version in
                                  venv_manager.pypa_pkg_versions.items()])
        msg = f"\tVirtual env created with the following pypa " \
              f"packages installed:\n{pkg_versions}"
        logging.getLogger(f"std_out.{__name__}").info(msg)

        self.install_orig_pkg_in_venv(
            venv_manager=venv_manager,
            status_msg_kwarg=f"Installing {self._orig_pkg_dist.name} in "
                             f"virtual env")

        # venv_manager.pip_install(
        #     self._orig_pkg_dist, "--quiet"
        # ).rewire_shebangs()
