"""
Solo Re-Package (srepkg)
=========================

srepkg is a Python package that wraps an isolation layer around the
source code of other Python packages. When a package that has been
“re-packaged” by srepkg is installed using a pip install command from
an existing Python environment, a new virtual environment is
automatically created. The original package and its dependencies are
installed in this newly created virtual environment to avoid the
possibility of any dependency-conflicts, but the original package’s
command line entry points are still accessible from the pre-existing
environment.
"""
