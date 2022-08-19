"""
Minimal setup.py file.
"""
import setuptools


class BinaryDistribution(setuptools.dist.Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(self):
        return True


setuptools.setup(
    distclass=BinaryDistribution
)

