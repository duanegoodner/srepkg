# Welcome to the srepkg documentation
*Add a safeguard to a dependency-laden Python command line  interface (CLI) app to ensure users can only install it in an isolated virtual environment but can run it from outside that environment.*

## Description

**srepkg** is a Python package that wraps an isolation layer around other Python packages. A package that has been "re-packaged" is referred to as an "S-package."

When an S-package is installed in an active, pre-existing Python environment, the original package plus its dependencies are installed in a new, automatically created virtual environment. A dependency-free "access" package installed in the pre-existing environment contains a controller module cabable of making calls to the Python interpreter in the newly created environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment. 



## Typical Use Case

srepkg can be useful if you are sharing a Python command line application, and you want to be certain that users can install and run it without worrying about dependency conflicts. You might be sharing application **X** that depends on package **Y** version 1.0, but users may want to run **X** from an environment where they require Y version 2.0. Or perhaps you just want to save users the trouble of dependency and/or environment management.









[//]: # (## Commands)
[//]: # (* `mkdocs new [dir-name]` - Create a new project.)
[//]: # (* `mkdocs serve` - Start the live-reloading docs server.)
[//]: # (* `mkdocs build` - Build the documentation site.)
[//]: # (* `mkdocs -h` - Print help message and exit.)

