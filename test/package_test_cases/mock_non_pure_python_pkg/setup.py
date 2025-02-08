import setuptools


class BinaryDistribution(setuptools.dist.Distribution):

    def has_ext_modules(self):
        return True


setuptools.setup(distclass=BinaryDistribution)
