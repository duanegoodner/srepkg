import configparser
import venv
import subprocess
import sys
from packaging import version
from types import SimpleNamespace
from pathlib import Path
from yaspin import yaspin


class CustomVenvBuilder(venv.EnvBuilder):
    def __init__(self):
        super().__init__(with_pip=True)
        self._context = SimpleNamespace()
        self._version_info = sys.version_info

    @property
    def context(self):
        return self._context

    @property
    def version_info(self):
        return self._version_info

    def post_setup(self, context) -> None:
        subprocess.call([
            context.env_exe, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
        subprocess.call([
            context.env_exe, "-m", "pip", "install", "--upgrade", "setuptools", "--quiet"])
        subprocess.call([context.env_exe, "-m", "pip", "install", "--upgrade", "wheel", "--quiet"])

        self._context = context


class VenvManager:
    def __init__(
        self, env_dir: Path, env_exe: Path, cfg_path: Path
    ):
        # self._context = venv_context
        self._env_dir = env_dir
        self._env_exe = env_exe
        self._cfg_path = cfg_path
        self._pyvenv_cfg = configparser.ConfigParser()
        with self._cfg_path.open(mode='r') as cfg_file:
            self._pyvenv_cfg.read_string("[pyvenv_cfg]\n" + cfg_file.read())
        # self._version_info = version_info
        self._console_scripts = []

    # @property
    # def _env_dir(self) -> Path:
    #     return Path(self._context.env_dir)

    @property
    def _version(self):
        return version.parse(self._pyvenv_cfg.get("pyvenv_cfg", "version"))

    @property
    def _site_packages(self):

        return (
            self._env_dir
            / "lib"
            / "".join(
                [
                    "python",
                    str(self._version.major),
                    ".",
                    str(self._version.minor),
                ]
            )
            / "site-packages"
        )

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
        pip_cs_without_dist_info = Path(
            self._env_dir
            / "bin"
            / (
                "pip"
                + str(self._version.major)
                + "."
                + str(self._version.minor)
            )
        )
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
            self, venv_path: Path, orig_pkg_dist: Path):
        self._venv_path = venv_path
        self._orig_pkg_dist = orig_pkg_dist

    def build_venv(self):
        # with yaspin().bouncingBall as sp:
        #     sp.text = "Setting up virtual env..."

        env_builder = CustomVenvBuilder()
        env_builder.create(self._venv_path)

        return env_builder.context

    def iso_install_inner_pkg(self):
        # with yaspin().bouncingBall as sp:
        #     sp.text = "Installing original package into virtual env..."
        venv_context = self.build_venv()
        venv_manager = VenvManager(
            env_dir=Path(venv_context.env_dir),
            env_exe=Path(venv_context.env_exe),
            cfg_path=Path(venv_context.cfg_path))
        venv_manager.pip_install(
            self._orig_pkg_dist, "--quiet"
        ).rewire_shebangs()
