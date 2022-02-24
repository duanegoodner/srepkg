from distutils.core import setup
import setuptools


setup(
    name='srepkg',
    version='0.0.1',
    description='Copies and repackages apps with an isolation layer',
    url='#',
    author='duanegoodner',
    install_requires=[],
    author_email='dmgoodner@gmail.com',
    packages=setuptools.find_packages(),
    package_data={"": ["*.template", "*.cfg"]},
    include_package_data=True,
    zip_safe=False
)
