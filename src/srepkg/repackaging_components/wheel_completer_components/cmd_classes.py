import sys
from setuptools.command.bdist_wheel import bdist_wheel


class BdistWheelAbi3(bdist_wheel):
    def get_tag(self):
        python, abi, plat = super().get_tag()

        if python.startswith("cp"):
            major, minor = sys.version_info[:2]
            return f"cp{major}{minor}", "abi3", plat

        return python, abi, plat
