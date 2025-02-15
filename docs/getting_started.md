# Getting Started

## Requirements

- Python version 3.9 or higher
- For compatibility with *srepkg*, and existing package must:
  * Be installable via [pip](https://pip.pypa.io/en/stable/installation/#)
  * Be compatible with the Python interpreter version that is running *srepkg*.
  * Have command line entry point(s) specified in either one the `[project.scripts]` section of a `pyproject.toml` (preferred), the `[options.entry_points]` section of a  `setup.cfg`, or the `entry_points` arguments passed to `setup()` in a `setupy.py` file.
- Optional: `miniconda` or `conda` if you want to exactly follow the examples in the documentation.

## Installing

```shell
pip install srepkg
```

## Command Line Help
```shell
srepkg --help
```

## Simple Demo with *srepkg* in a fresh conda environment

```shell
# Create and activate a new conda environment for testing
conda create -n srepkg_test python=3.11
conda activate srepkg_test

# Install srepkg from PyPI
pip install srepkg

# Re-package a version of black, obtained from PyPI
srepkg black -r 25.1.0  # creates re-package wheel and sdist under ./srepkg_dists

# install our re-packaged wheel
pip install ./srepkg_dists/blacksrepkg-25.1.0-py3-none-any.whl

# Confirm blacksrepkg is installed and that black is NOT installed in our conda env
conda list | grep black
# Output:
# blacksrepkg               25.1.0                   pypi_0    pypi

# Check if any of black's dependencies are installed in our conda environment
onda list | grep "click\|\
mypy_extensions\|\
packaging\|\
pathspec\|\
platformdirs\|\
tomli\|\
typing_extensions"

# Output:
# packaging                 24.2                     pypi_0    pypi

# Note: 'packaging' is installed because it is a dependency of 'srepkg'.
# No other package that black depends on is in our environment.

# Confirm that we have access to the black CLI
black -c "def foo():print('hello,world')"
# Output:
# def foo():
#    print("hello,world")
```