"""
Solo Re-Package (srepkg)
=========================

srepkg is a Python package that modifies other Python packages by
adding a layer that affects how and where a package is
installed. When a “re-packaged” package is installed via a pip from a
pre-existing environment, the isolation layer that was added by srepkg
creates a new virtual environment. The original package and its
dependencies are installed in this newly-created, isolated environment.

A dependency-free access package is installed in the pre-existing
environment to provide access to the original package's command line
entry points.


"""