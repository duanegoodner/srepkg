import sys
from typing import TypedDict, NamedTuple
import os


class SafePkgPaths(NamedTuple):
    safe_src: str
    venv_pkg: str
    venv_py: str
    venv_pip: str

    @classmethod
    def from_local_build(cls, safe_src: str):
        venv_path = os.path.dirname(safe_src) + '/' +\
                    os.path.basename(safe_src) + '_venv'
        venv_py = venv_path + '/bin/python'
        venv_pip = venv_path + '/bin/pip'
        py_v = 'python' + str(sys.version_info.major) + '.' + \
            str(sys.version_info.minor)
        venv_pkg = venv_path + '/lib/' + py_v + '/site-packages'

        return cls(safe_src=safe_src, venv_pkg=venv_pkg,
                   venv_py=venv_py, venv_pip=venv_pip)





