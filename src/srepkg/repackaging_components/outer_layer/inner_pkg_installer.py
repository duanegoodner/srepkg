import venv
import subprocess
from typing import NamedTuple
from pathlib import Path
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
from pkg_names import inner_pkg_name, sre_pkg_name


class VenvInstallPaths(NamedTuple):
    inner_src: Path
    venv_py: Path
    venv_pip: Path

    @classmethod
    def from_inner_src(cls, inner_src: Path):
        venv_path = inner_src.parent.absolute() / \
                    (str(inner_src.name) + '_venv')
        venv_py = venv_path / 'bin' / 'python'
        venv_pip = venv_path / 'bin' / 'pip'

        return cls(inner_src=inner_src, venv_py=venv_py, venv_pip=venv_pip)


class InnerPkgInstaller:

    def __init__(self, install_paths: VenvInstallPaths):
        self._paths = install_paths

    @classmethod
    def from_inner_src(cls, inner_src: Path):
        return cls(VenvInstallPaths.from_inner_src(inner_src))

    def build_venv(self):
        env_builder = venv.EnvBuilder(with_pip=True)
        env_builder.create(self._paths.inner_src.parent.absolute() /
                           str(self._paths.inner_src.name + '_venv'))

        return self

    def upgrade_pip(self):
        subprocess.call([self._paths.venv_py, '-m', 'pip', 'install',
                         '--upgrade', 'pip'])
        return self

    def install_utilities(self, *utility_packages):
        subprocess.call([self._paths.venv_pip, 'install', *utility_packages])
        return self

    def install_inner_pkg(self):
        # if (self._paths.inner_src.parent / 'setup_off.py').exists():
        #     (self._paths.inner_src.parent / 'setup_off.py').rename(
        #         self._paths.inner_src.parent / 'setup.py')
        #
        # if (self._paths.inner_src.parent / 'setup_off.cfg').exists():
        #     (self._paths.inner_src.parent / 'setup_off.cfg').rename(
        #         self._paths.inner_src.parent / 'setup.cfg')

        subprocess.call([self._paths.venv_pip, 'install',
                         self._paths.inner_src.parent / '.', '--quiet'])

        # if (self._paths.inner_src.parent / 'setup.py').exists():
        #     (self._paths.inner_src.parent / 'setup.py').rename(
        #         self._paths.inner_src.parent / 'setup_off.py')
        #
        # if (self._paths.inner_src.parent / 'setup.cfg').exists():
        #     (self._paths.inner_src.parent / 'setup.cfg').rename(
        #         self._paths.inner_src.parent / 'setup_off.cfg')
        return self


def custom_command():
    inner_pkg_installer = InnerPkgInstaller.from_inner_src(
        Path(__file__).parent.absolute() / sre_pkg_name / inner_pkg_name)

    inner_pkg_installer.build_venv()
    inner_pkg_installer.upgrade_pip()
    inner_pkg_installer.install_utilities('wheel')
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


if __name__ == '__main__':
    custom_command()
