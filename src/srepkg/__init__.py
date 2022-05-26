"""
Solo Re-Package (srepkg)
=========================

srepkg is a Python package that wraps an isolation layer around the
source code of other Python packages. When a package that has been
“re-packaged” by srepkg is installed using a pip install command from
an existing Python environment, a new virtual environment is
automatically created. The original package and its dependencies are
installed there to avoid the possibility of any dependency-conflicts,
but the original package’s command line entry points are still
accessible from the pre-existing environment.

usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] orig_pkg_path

positional arguments:
  orig_pkg_path         Path of directory containing original package's
                        setup.cfg file

optional arguments:
  -h, --help            show this help message and exit
  --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. If not
                        specified, defaults to the original
                        package name appended with 'srepkg'

Output
======
A re-packaged package is saved in
~/srepkg_pkgs/ORIGINAL_PACKAGE_NAME_as_SREPKG_NAME

The re-packaged package can be installed via pip with the command:
pip install ~/srepkg_pkgs/ORIGINAL_PACKAGE_NAME_as_SREPKG_NAME
"""
