


# 📦 Solo Repackage (srepkg)

![Python Versions](https://img.shields.io/pypi/pyversions/srepkg)
![PyPI](https://img.shields.io/pypi/v/srepkg)
[![codecov](https://codecov.io/gh/duanegoodner/srepkg/graph/badge.svg?token=EM1ESYCU4C)](https://codecov.io/gh/duanegoodner/srepkg)
![PyPI - Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://duanegoodner.github.io/srepkg/)
![License: MIT](https://badgen.net/badge/license/MIT/blue)


Wraps a Python package with an isolation layer that enforces installation in an isolated virtual environment while still providing access to the original package's command-line interface in an external environment.

## 📖 Description

When a Python package that has been wrapped in a *srepkg* isolation layer is installed in an active, pre-existing Python environment:
- The original package plus its dependencies are installed in a new, automatically created virtual environment.
- A dependency-free "access" package installed in the pre-existing environment contains a controller module capable of making calls to the Python interpreter in the newly created environment.
- This enivronment and package structure exposes the original package’s CL to the pre-existing environmen while ensuring that none of the original package's dependencies conflict with packages in the pre-existing environment.

## 📘 Documentation

Full project documentation, including detailed examples, is available at: [duanegoodner/github.io/srepkg](https://duanegoodner.github.io/srepkg/)

## 🎯 Use Cases

### For Package Distributors
- *srepkg* can be useful if you are sharing a Python command line application, and you want to be certain that users can install and run it without worrying about dependency conflicts. 
- Wrapping a CL package with *srepkg* prior to sharing the package with other users will ensure that wherever the package is installed, it does not introduce dependency conflicts into a user's existing Python environment &mdash; even if the user knows nothing about managing Python environments.

### For Package Users
- Any existing CL package obtained from Python Packaging Index (PyPI) or GitHub can be wrapped with *srepkg* prior to installation.
- If you want the original package commands to be accessible from a single environment (that is distinct from the isolated environment where the original package is installed), then *srepkg* is likely a good option.
- However, if you want the isolated package's command interface to be available globally and/or want a much more mature isolation tool, then [pipx]("https://github.com/pypa/pipx") is likely a better choice.

## ⚡ Quick Start

### Requirements

- Python version 3.9 or higher
- For compatibility with *srepkg*, and existing package must:
  * Be installable via [pip](https://pip.pypa.io/en/stable/installation/#)
  * Be compatible with the Python interpreter version that is running *srepkg*.
  * Have command line entry point(s) specified in either one the `[project.scripts]` section of a `pyproject.toml` (preferred), the `[options.entry_points]` section of a  `setup.cfg`, or the `entry_points` arguments passed to `setup()` in a `setupy.py` file.
- Optional: `miniconda` or `conda` if you want to exactly follow the examples below


### Simple Demo

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

### Command Line Help
For details on all `srepkg` command options, run:
```shell
srepkg --help
```

## 🧪 Testing

An automated test suite runs via **GitHub Actions** on every push to the `main` branch and every pull request. However, tests can also be run manually.

First, clone the repo and install dependencies:

```
$ git clone https://github.com/duanegoodner/srepkg
$ cd srepkg
$ pip install -e '.[test]'
```
Then run the test suite and generate a coverage report:
```
$ coverage run -m pytest
$ coverage report -m
```


## 🤝 Contributing

Issues, Pull Requests and/or Discussions are welcome and appreciated!


