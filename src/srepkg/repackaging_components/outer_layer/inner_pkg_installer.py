import configparser
import venv
import subprocess
import sys
from types import SimpleNamespace
from typing import NamedTuple
from pathlib import Path
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from pkg_names import inner_pkg_name, sre_pkg_name


class CustomVenvBuilder(venv.EnvBuilder):
    def __init__(self):
        super().__init__(with_pip=True, upgrade_deps=True)
        self._context = SimpleNamespace()
        self._version_info = sys.version_info

    @property
    def context(self):
        return self._context

    @property
    def version_info(self):
        return self._version_info

    def post_setup(self, context) -> None:
        subprocess.call([context.env_exe, "-m", "pip", "install", "wheel"])
        self._context = context


class VenvManager:
    def __init__(
        self, venv_context: SimpleNamespace, version_info: sys.version_info
    ):
        self._context = venv_context
        self._version_info = version_info
        self._console_scripts = []

    @property
    def _env_dir(self) -> Path:
        return Path(self._context.env_dir)

    @property
    def _site_packages(self):

        return (
            self._env_dir
            / "lib"
            / "".join(
                [
                    "python",
                    str(self._version_info.major),
                    ".",
                    str(self._version_info.minor),
                ]
            )
            / "site-packages"
        )

    @property
    def _relative_shebang(self):
        return '#!/bin/sh\n"exec" "`dirname $0`/python" "$0" "$@"\n'

    def pip_install(self, *args):
        subprocess.call(
            [self._context.env_exe, "-m", "pip", "install"] + [*args]
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
                + str(self._version_info.major)
                + "."
                + str(self._version_info.minor)
            )
        )
        if pip_cs_without_dist_info.exists():
            self._update_cs_shebang(pip_cs_without_dist_info)

    def rewire_shebangs(self):
        self._gather_all_console_scripts()
        self._update_all_cs_shebangs()
        self._update_rogue_pip_cs_shebang()


class VenvInstallPaths(NamedTuple):
    inner_src: Path
    venv_py: Path
    venv_pip: Path

    @classmethod
    def from_inner_src(cls, inner_src: Path):
        venv_path = inner_src.parent.absolute() / (
            str(inner_src.name) + "_venv"
        )
        venv_py = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"

        return cls(inner_src=inner_src, venv_py=venv_py, venv_pip=venv_pip)


class InnerPkgInstaller:
    def __init__(self, venv_path: Path, inner_pkg_src: Path):
        self._venv_path = venv_path
        self._inner_pkg_src = inner_pkg_src

    @classmethod
    def from_inner_src(cls, inner_src: Path):
        return cls(VenvInstallPaths.from_inner_src(inner_src))

    def build_venv(self):
        env_builder = CustomVenvBuilder()
        env_builder.create(self._venv_path)

        return {
            "venv_context": env_builder.context,
            "version_info": env_builder.version_info,
        }

    def install_inner_pkg(self):
        venv_info = self.build_venv()
        venv_manager = VenvManager(**venv_info)
        venv_manager.pip_install(
            self._inner_pkg_src, "--quiet"
        ).rewire_shebangs()


def custom_command():

    inner_pkg_installer = InnerPkgInstaller(
        venv_path=Path(__file__).parent.absolute()
        / sre_pkg_name
        / "srepkg_venv",
        inner_pkg_src=Path(__file__).parent.absolute() / sre_pkg_name,
    )

    inner_pkg_installer.build_venv()
    inner_pkg_installer.install_inner_pkg()

    return inner_pkg_installer


class CustomInstallCommand(install):
    def run(self):
        # super(install, self).run()

        install.run(self)
        custom_command()

        # super(install, self).run()
        # custom_command()


class CustomDevelopCommand(develop):
    def run(self):
        develop.run(self)
        custom_command()


class CustomEggInfoCommand(egg_info):
    def run(self):
        egg_info.run(self)
        custom_command()


if __name__ == "__main__":
    custom_command()
