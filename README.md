# srepkg (Solo Repackage)


## Description
*srepkg* is a Python package that wraps an isolation layer around other Python packages.

When a package wrapped in this isolation layer is installed in an active, pre-existing Python environment, the original package plus its dependencies are installed in a new, automatically created virtual environment. A dependency-free "access" package installed in the pre-existing environment contains a controller module capable of making calls to the Python interpreter in the newly created environment. This package structure ensures that none of the original package's dependencies conflict with packages in the pre-existing environment but still exposes the original package’s CL to the pre-existing environment. 

## Use Cases

### For Package Distributors
*srepkg* can be useful if you are sharing a Python command line application, and you want to be certain that users can install and run it without worrying about dependency conflicts. You might be sharing application **X** that depends on package **Y** version 1.0.  Users may want to run **X** from an environment where they require **Y** version 2.0.  Wrapping a CL package with *srepkg* prior to sharing the package with other users will ensure that wherever the package is installed, it does not introduce dependency conflicts into a user's existing Python environment &mdash; even if the user knows nothing about managing Python environments.

### For Package Users
Any existing CL package obtained from Python Packaging Index (PyPI) or GitHub can be wrapped with *srepkg* prior to installation to ensure that none of the original package's dependencies will conflict with any packages in an existing environment. If you want the original package commands to be accessible from a single environment (that is distinct from the isolated environment where the original package is installed), then *srepkg* is likely a good option. However, if you want the isolated package's command interface to be available globally and/or want a much more mature isolation tool, then [pipx]("https://github.com/pypa/pipx") is likely a better choice.

## Getting Started

### Requirements

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

## Demos

### Demo #1: Repackaging a local package that depends on old version of `numpy`

The following demo shows how we take an original package that has a dependency conflict what's already installed in an active Python environment, re-package with *srepkg*, install the re-packaged version, and access the original package's CLI from the active environment, without experiencing any dependency conflict.

#### Environment Setup

First, confirm we are using a conda environment dedicated to our tests. From the *srepkg* repo root, run:
```
$ conda create -n srepkg_oldmath_test python=3.10
$ conda activate srepkg_oldmath_test
$ pip install .
```

Then, let's install a version of numpy that is relatively new (as of Feb. 2025).
```
$ pip install numpy==2.2.2
```
Later on, we will use the presence of this current numpy version to help illustrate the absence of dependency conflicts.

#### Repackage `oldmath`into `oldmathsrepkg`

Next, we will re-package a simple local Python package `oldmath` with its source files located `./test/demos/oldmath/`. `oldmath` depends on `numpy 1.26.4`.

```
$ srepkg test/demos/oldmath/

✅ Building original package wheel from source code
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing oldmath-0.1.0-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	oldmathsrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
✅ Building srepkg sdist
	oldmathsrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0.tar.gz

oldmathsrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0.tar.gz
Upon installation, oldmathsrepkg will provide access to the following command line entry points: 
	• oldmath
```
The repackaged version of `oldmath` is called `oldmathsrepkg`, and it has been built into both `wheel` and `sdist` distributions.

> [!NOTE]
> The `-n` option can be used to assign a custom name to the repackaged package and distributions.

#### Install and test `oldmathsrepkg`

Next, install `oldmathsrepkg` from the newly created wheel:
```
$ pip install ./srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
```
Now, we can get some info about `oldmath`:
```
$ oldmath --help

usage: oldmath [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer. Displays the resulting array as well as the version of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

options:
  -h, --help  show this help message and exit
```
Next, we run:
```
$ oldmath 2025

2025 * [1 2 3] = [2025 4050 6075]
numpy version used by this program = 1.26.4
```

#### Confirm absence of dependency conflicts

Double-check the version of `numpy` that's installed in our active Python environment:
```
$ pip freeze | grep numpy

numpy==2.2.2
```

Finally, confirm that we do not have any dependency conflicts:
```
$ pip check

No broken requirements found.
```

The key thing to note is that oldmath, which we can access from the active Python environment uses `numpy 1.26.4`, but we still have `numpy 2.2.2` installed the active environment.


#### Distribute `oldmathsrepkg` with confidence that it will not break environments

We can now send the `oldmathsrepkg` *wheel* and/or *sdist* (saved under `./srepkg_dists`) to colleagues, knowing that install it will not cause problems in their Python environment, even if they are using a current version of `numpy` and do not know much / anything about Python dependencies and environments.

### Demo #2: Re-package a distribution obtained from PyPI

We can re-package the latest version of `scrape` available on the PyPI using the following:
```
$ srepkg scrape

✅ Retrieving scrape from Python Packaging Index
	Downloaded files:
	• scrape-0.11.3-py3-none-any.whl
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing scrape-0.11.3-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	scrapesrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
✅ Building srepkg sdist
	scrapesrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz

scrapesrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz
Upon installation, scrapesrepkg will provide access to the following command line entry points: 
	• scrape
```

We can then install `scrapesrepkg`, and try using it on a file located under `test/demos/`:
```
$ pip install pip install srepkg_dists/scrapesrepkg-0.11.3-cp310-abi3-linux_x86_64.whl

Processing ./srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
Installing collected packages: scrapesrepkg
Successfully installed scrapesrepkg-0.11.3

$ scrape test/demos/scrape/explorers_club.html -pt

Failed to enable cache: No module named 'requests_cache'
DISCOVER THE GRAND EXPLORERS' CLUB!
The Grand Explorers' Club is a prestigious society dedicated to adventurers and thrill-seekers. More than 250,000 members participate in daring expeditions and exploration missions across the globe.
```

If we wanted to re-package a specific version (e.g.`0.11.0`) from PyPI we could do this:
```
$ srepkg scrape -r 0.11.0
```

### Demo #3: Re-package a distribution obtained from Github

We can also re-package using a GitHub repo as the original source:
```
srepkg https://github.com/huntrar/scrape      
✅ Cloning https://github.com/huntrar/scrape into temporary directory
✅ Building original package wheel from source code
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing scrape-0.11.3-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	scrapesrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
✅ Building srepkg sdist
	scrapesrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz

scrapesrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz
Upon installation, scrapesrepkg will provide access to the following command line entry points: 
	• scrape
```

If we want to re-package a specific commit from the `scrape` GitHub repo, we can do this:
```
$ srepkg https://github.com/huntrar/scrape -g 1dfd98bb0a308ef2a45b1e5dd136c38b17c27bc7
```
If we want to re-package a specific release or tag, we would do this:
```
$ srepkg https://github.com/huntrar/scrape -g 0.11.2 
```

## Comparing with a similar tool: [pipx](https://github.com/pypa/pipx)

*srepkg* is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python package in an isolated environment and then access its command line tool(s) from another environment. Key differences between *srepkg* and *pipx* include:

* The actions that ensure isolation via *pipx* are taken by the user at the time of package installation. With *srepkg*, source code is wrapped in an isolating layer prior to installation, and the re-packaged application is automatically placed in its own environment during installation. 
* The CLI of a package that has been re-packaged by *srepkg* accessible from an environment containing its access package. pipx allows global access to isolated command line applications. 
* *pipx* is more mature and feature-rich than srepkg. If you have control of the package installation process, *pipx* will likely be more useful than *srepkg*. However, if you are distributing but not installing a Python CLI app and want to be certain the app is always installed into an isolated environment regardless what happens at install time, consider using *srepkg*.


## Testing

The following series of commands will install *srepkg* in editable mode, run the project's tests, and report branch coverage.

```
$ pip install -e '.[test]'
$ coverage run -m pytest
$ coverage report -m
```

## Contributing

Issues, Pull Requests and/or Discussions are welcome and appreciated!
