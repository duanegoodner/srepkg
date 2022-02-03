from sys import version_info
from typing import NamedTuple
from pathlib import Path


class HpkgControlPaths(NamedTuple):
    safe_src: Path
    venv_pkg: Path
    venv_py: Path
    venv_pip: Path

    @classmethod
    def for_env_builder(cls, safe_src: Path):
        venv_path = safe_src.parent.absolute().joinpath(
            str(safe_src.name) + '_venv'
        )

        venv_py = venv_path.joinpath('bin/python')
        venv_pip = venv_path.joinpath('bin/pip')
        py_v = 'python' + str(version_info.major) + '.' + \
            str(version_info.minor)
        venv_pkg = venv_path.joinpath('lib', py_v, 'site-packages')

        return cls(safe_src=safe_src, venv_pkg=venv_pkg,
                   venv_py=venv_py, venv_pip=venv_pip)





