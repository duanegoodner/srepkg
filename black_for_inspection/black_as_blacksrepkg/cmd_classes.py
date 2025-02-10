import configparser
from pathlib import Path
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import inner_pkg_installer.inner_pkg_installer as ipi


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


class CmdClassInstaller(ipi.InnerPkgInstaller):
    def __init__(self, srepkg_root: Path):
        install_cfg = InnerPkgCfgReader(srepkg_root / "inner_pkg_install.cfg")
        super().__init__(
            venv_path=srepkg_root / install_cfg.srepkg_name / "srepkg_venv",
            orig_pkg_dist=srepkg_root
            / install_cfg.dist_dir
            / install_cfg.sdist_src,
        )


class CustomInstallCommand(install):
    def run(self):

        install.run(self)
        CmdClassInstaller(
            srepkg_root=Path(__file__).parent.absolute()
        ).iso_install_inner_pkg()


class CustomDevelopCommand(develop):
    def run(self):

        develop.run(self)
        CmdClassInstaller(
            srepkg_root=Path(__file__).parent.absolute()
        ).iso_install_inner_pkg()


class CustomEggInfoCommand(egg_info):
    def run(self):

        egg_info.run(self)
        CmdClassInstaller(
            srepkg_root=Path(__file__).parent.absolute()
        ).iso_install_inner_pkg()


if __name__ == "__main__":
    CmdClassInstaller(
        srepkg_root=Path(__file__).parent.absolute()
    ).iso_install_inner_pkg()
