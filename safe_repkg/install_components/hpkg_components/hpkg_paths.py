import sys
from typing import TypedDict, NamedTuple
from pathlib import Path
import os


class HpkgPaths(NamedTuple):
    safe_src: str
    venv_pkg: Path
    venv_py: Path
    venv_pip: Path

    @classmethod
    def for_env_builder(cls, safe_src: str):
        venv_path = Path(safe_src).parent.absolute().joinpath(
            str(Path(safe_src).name) + '_venv'
        )

        venv_py = venv_path.joinpath('bin/python')
        venv_pip = venv_path.joinpath('bin/pip')
        py_v = 'python' + str(sys.version_info.major) + '.' + \
            str(sys.version_info.minor)
        venv_pkg = venv_path.joinpath('lib', py_v, 'site-packages')

        return cls(safe_src=safe_src, venv_pkg=venv_pkg,
                   venv_py=venv_py, venv_pip=venv_pip)





