# Getting Started

## Requirements

- Python version 3.10 or higher
- For compatibility with *srepkg*, and existing package must:
  * Be installable via [pip](https://pip.pypa.io/en/stable/installation/#)
  * Have command line entry point(s) specified in either one the `[project.scripts]` section of a `pyproject.toml` (preferred), the `[options.entry_points]` section of a  `setup.cfg`, or the `entry_points` arguments passed to `setup()` in a `setupy.py` file.
- Optional: `miniconda` or `conda` if you want to exactly follow the examples below


### Installing

> [!CAUTION]
> It is highly recommended to install srepkg in a virtual environment created using a tool such as `conda` or Python's built-in `venv` module. In the example below, we use `conda`.

```
conda create -n srepkg_test python=3.10
conda activate srepkt_test
git clone https://github.com/duanegoodner/srepkg
cd srepkg
pip install .
```


### Quick Example

```
srepkg black -r 25.1.0


```


### Usage

```
usage: srepkg [-h] [-g [GIT_REF]] [-r [PYPI_VERSION]] [-n [SREPKG_NAME]]
              [-c [CONSTRUCTION_DIR]] [-d [DIST_OUT_DIR]] [-f [LOGFILE_DIR]]
              orig_pkg_ref

positional arguments:
  orig_pkg_ref          A reference to the original package to be repackaged. Can be a
                        local path to the directory where a package'spyproject.toml or
                        setup.py resides, a PyPI package name, or a Github repo url.

options:
  -h, --help            show this help message and exit
  -g [GIT_REF], --git_ref [GIT_REF]
                        A git branch name, tag name, or commit SHA that determines the
                        original package commit to use (if ORIG_PKG_REF is a git repo).
                        Defaults to: HEAD of the default branch for a remote Github repo,
                        and the currently checked out branch for a local repo.
  -r [PYPI_VERSION], --pypi_version [PYPI_VERSION]
                        Original package version to use (if ORIG_PKG_REF is a PyPI
                        package). Defaults to the latest PyPI package.
  -n [SREPKG_NAME], --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. Default is
                        <ORIGINAL_PACKAGE_NAME>srepkg
  -c [CONSTRUCTION_DIR], --construction_dir [CONSTRUCTION_DIR]
                        Directory where non-compressed repackage will be built and saved.
                        If not specified, srepkg is built in a temp directory that gets
                        deleted after wheel and or sdist archiveshave been created.
  -d [DIST_OUT_DIR], --dist_out_dir [DIST_OUT_DIR]
                        Directory where srepkg wheel and or sdist archives are saved.
                        Default is ./srepkg_dists.
  -f [LOGFILE_DIR], --logfile_dir [LOGFILE_DIR]
                        Directory where srepkg log file is saved. Default is to use
                        temporary directory that is automatically deleted at end of
                        execution.
```

