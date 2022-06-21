Description
===========


srepkg is a Python package that wraps an isolation layer around other Python packages. When a package that has been “re-packaged” by srepkg is installed in an existing Python environment, a dependency-free "access" package is installed in the pre-existing environment, while the original package and its dependencies are installed in a new, automatically created virtual environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment.