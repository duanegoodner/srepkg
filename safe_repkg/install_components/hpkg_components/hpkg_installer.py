from venv import EnvBuilder
from os import path
from .hpkg_controller import HpkgController


def install(safe_src: str):
    env_builder = EnvBuilder(with_pip=True)
    env_builder.create(path.dirname(safe_src) + '/' +
                       path.basename(safe_src) + '_venv')

    return HpkgController.for_env_builder(safe_src)

