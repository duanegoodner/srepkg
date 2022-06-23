# About



## Description

**srepkg** is a Python package that wraps an isolation layer around other Python packages. A package that has been "re-packaged" is referred to as an "S-package."

When an S-package is installed in an existing Python environment, a dependency-free "access" package is installed in the pre-existing environment, and the original package plus its dependencies are installed in a new, automatically created virtual environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment.





