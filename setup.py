from distutils.core import setup
import setuptools


setup(
    name='hpkg',
    version='0.0.1',
    description='Builds "helmeted" packages that are force to run in separate '
                'env',
    url='#',
    author='duanegoodner',
    install_requires=[],
    author_email='dmgoodner@gmail.com',
    packages=setuptools.find_packages(),
    package_data={"": ["*.template"]},
    include_package_data=True,
    zip_safe=False
)