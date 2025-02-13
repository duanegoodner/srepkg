# Srepkg (Solo Repackage)

Add a safeguard to a Python command line (CL) app to ensure users can only install it in an isolated virtual environment but can access it from another environment.

## Description

**Srepkg** is a Python package that wraps an isolation layer around other Python packages.

When a package wrapped in this isolation layer is installed in an active, pre-existing Python environment, the original package plus its dependencies are installed in a new, automatically created virtual environment. A dependency-free "access" package installed in the pre-existing environment contains a controller module capable of making calls to the Python interpreter in the newly created environment. This package structure ensures that none of the original package's dependencies conflict with packages in the pre-existing environment but still exposes the original package’s CL to the pre-existing environment. 

## Use Cases

### For Package Distributors
\Wrapping a CL package with **Srepkg** prior to sharing the package with other users will ensure that wherever the package is installed, it does not "break" a user's existing Python environment &mdash; even if the user knows nothing about managing Python environments.

### For Package Users
Any existing CL package obtained from sources such as the Python Packaging Index (PyPI) , GitHub, or directly from another user can be wrapped with **Srepkg** prior to installation.

## Getting Started

### Requirements

- Python version 3.10 or higher
- For compatibility with **Srepkg**, and existing package must:
  * Be installable via [pip](https://pip.pypa.io/en/stable/installation/#)
  * Have command line entry point(s) specified in either one the `[project.scripts]` section of a `pyproject.toml` (preferred), the `[options.entry_points]` section of a  `setup.cfg`, or the `entry_points` arguments passed to `setup()` in a `setupy.py` file.

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

### Demos

#### Local package `oldmath` that depends on old version of `numpy`

 `oldmath`

```


```

### Usage

```
usage: srepkg [-h] [-g [GIT_REF]] [-r [PYPI_VERSION]] [-n [SREPKG_NAME]] [-c [CONSTRUCTION_DIR]] [-d [DIST_OUT_DIR]]
              [-f [LOGFILE_DIR]]
              orig_pkg_ref

positional arguments:
  orig_pkg_ref          A reference to the original package to be repackaged. Can be a local path to the directory where a
                        package's setup.py or pyproject.toml resides, a PyPI package name, or a Github repo url.

options:
  -h, --help            show this help message and exit
  -g [GIT_REF], --git_ref [GIT_REF]
                        A git branch name, tag name, or commit SHA that determines the original package commit to use (if
                        ORIG_PKG_REF is a git repo). Defaults to: HEAD of the default branch for a remote Github repo, and
                        the currently checked out branch for a local repo.
  -r [PYPI_VERSION], --pypi_version [PYPI_VERSION]
                        Original package version to use (if ORIG_PKG_REF is a PyPI package). Defaults to the latest PyPI
                        package.
  -n [SREPKG_NAME], --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. Default is <{ORIGINAL_PACKAGE_NAME}srepkg>
  -c [CONSTRUCTION_DIR], --construction_dir [CONSTRUCTION_DIR]
                        Directory where non-compressed repackage will be built and saved. If not specified, srepkg is
                        built in a temp directory that gets deleted after wheel and or sdist archiveshave been created.
  -d [DIST_OUT_DIR], --dist_out_dir [DIST_OUT_DIR]
                        Directory where srepkg wheel and or sdist archives are saved. Default is the current working
                        directory.
  -f [LOGFILE_DIR], --logfile_dir [LOGFILE_DIR]
                        Directory to write srepkg log file to. Default behavior is to write log to file in temporary
                        directory that is automatically deleted at end of execution.

```

### Output

If the user-provided command just takes the form `$ srepkg orig_pkg_ref`  (i. e. no optional arguments are used), srepkg saves the re-packaged 'S-package' as a .zip file named `ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip` in the directory from which srepkg is called. ORIGINAL_NAME and ORIGINAL_VERSION are the respective name and version of the original package as specified in its setup.py or setup.cfg file.

### Installing an S-package

A distribution archive produced by srepkg can be installed using pip. If we are in the directory where we have used srepkg to create `ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip`, we can install it with the command:

```
$ pip install ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip
```

### Using an S-package

Once an S-package has been installed in a user's global Python environment, or (preferably) a virtual environment, all command line entry points of the original CLI application are available in that environment. The syntax of these commands is identical to that of the original application.

## Examples

#### 1. Repackaging a local package

The srepkg Github repo has a small example CLI package named testproj saved in `srepkg/src/test/package_test_cases/testproj/`. In testproj's setup.cfg file, we can see that it depends on non-standard library package numpy.

From the root of the srepkg repo, we can re-package testproj and save the S-package distribution archive to our home directory using:

```
$ srepkg src/srepkg/test/package_test_cases/testproj -d ~ 
```

When the re-packaging process is complete, we have the following output:

```
Repackaging testproj
Building source distribution of repackaged package
Original package 'testproj' has been re-packaged as 'testprojsrepkg'

The re-packaged version has been saved as source distribution archive file: /Users/duane/testprojsrepkg-0.0.0.zip
'testprojsrepkg' can be installed using:  pip install /Users/duane/testprojsrepkg-0.0.0.zip

After installation, 'testprojsrepkg' will provide command line access to the following commands:
my_test
```

Before proceeding, let's create and activate a new virtual environment so we can clearly see what package(s) do / don't get added to the environment when we install testprojsrepkg.

```
$ python -m venv my_venv
$ source my_venv/bin/activate
```

Now we are ready to install our S-package with pip:

```
(my_venv) $ pip install ~/testprojsrepkg-0.0.0.zip -q 
```

We can use pip freeze to confirm that howdoisrepkg is the only non-standard library package installed in the environment.

```
(my_venv) $ pip freeze
testprojsrepkg @ file:///Users/duane/testprojsrepkg-0.0.0.zip
```

Neither original package testproj nor its dependency numpy is installed in the active environment, but we can still access the testproj CLI in the same way we would if it were installed in the active environment

```
(my_venv) $ my_123_multiplier -h
usage: my_123_multiplier [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer. Displays the resulting array as well as the version
of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

optional arguments:
  -h, --help  show this help message and exit

(my_venv) $ my_123_multiplier 2
2 * [1 2 3] = [2 4 6]
numpy version used by this program = 1.22.4
```

#### 2. Repackaging a PyPI package

An S-package can also be built by providing a PyPI package name as the package_reference argument. Here, we repackage the [PyPI package *howdoi*](https://pypi.org/project/howdoi/). Let's continue working in the virtual environment created in the previous example.

```
(my_venv) $ srepkg howdoi -d ~
Original package howdoi has been repackaged as howdoisrepkg
howdoisrepkg has been saved as source distribution /Users/duane/howdoisrepkg-2.0.19.zip
'howdoisrepkg' can be installed using: pip install /Users/duane/howdoisrepkg-2.0.19.zip
After installation, 'howdoisrepkg' will provide command line access to the following commands:
howdoi
```

We can then install the S-package, confirm that we have access to the original package's CLI, and run `pip freeze` to list the non-standard packages installed in the current environment.

```
(my_venv) $ pip install ~/howdoisrepkg-2.0.19.zip -q
(my_venv) $ howdoi redirect standard out
yourcommand &> filename
(my_venv) $ pip freeze
	testprojsrepkg @ file:///Users/duane/testprojsrepkg-0.0.0.zip
	howdoisrepkg @ file:///Users/duane/dproj/howdoisrepkg-2.0.19.zip
```

Note that *howdoi* has a number dependencies (Pygments, cssselect, lxml, pyquery, requests, cachelib, appdirs, keep, rich, and colorama), but none of these packages are installed in my_venv.

#### 3. Repackaging a package from a Github repo

When the package reference argument is a Github repository, it takes the same form that pip uses when installing a package from Github. Below are examples of how to build S-packages based on code from the [*howdoi* Github repository](https://github.com/gleitz/howdoi).

##### Head of the default branch

```
$ srepkg git+https://github.com/gleitz/howdoi.git
```

##### Head of a specific branch

Re-package the head of branch *bugfix/remove-pathlib* using:

```
$ srepkg git+https://github.com/gleitz/howdoi@bugfix/remove-pathlib
```

##### Specific commit

Re-package commit *ac146f5aaaf33d8630f6b616727e5b000965863*:

```
$ srepkg git+https://github.com/gleitz/howdoi.git@4ac146f5aaaf33d8630f6b616727e5b000965863
```

##### Specific release

Re-package release *2.0.17*:

```
$ srepkg git+https://github.com/gleitz/howdoi.git@v2.0.17
```



## Comparing srepkg with a similar tool: [pipx](https://github.com/pypa/pipx)

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python package in an isolated environment and then access its command line tool(s) from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx are taken by the user at the time of package installation. With srepkg, source code is wrapped in an isolating layer prior to installation, and the re-packaged application is automatically placed in its own environment during installation. 
* The CLI of a srepkg S-package is only accessible from an environment containing its access package. pipx allows global access to isolated command line applications. 
* pipx is more mature and feature-rich than srepkg. If you have control of the package installation process, pipx will likely be more useful than srepkg. However, if you are distributing but not installing a Python CLI app and want to be certain the app is always installed into an isolated environment regardless what happens at install time, consider using srepkg.



## Roadmap

### Functionality

* Option to add prefix before CLI command. This would allow multiple re-packaged versions of the same original package to be accessed from single environment.
* Change behavior in cases where srepkg does not find console entry points or package name from from setup.cfg or setup.py. Instead of exiting, give re-packaging user the option to proceed and have inner_pkg_installer module look for these items during S-package install process.

### Performance

* Use [fastentrypoints](https://github.com/ninjaaron/fast-entry_points) to prevent delay that occurs the first time an S-package's CLI is accessed
* Reduce install time via .whl support for



## Contributing

Issues, Pull Requests and/or Discussions are welcome and appreciated!



Anyone interacting with this project is expected to follow the [Code of Conduct](https://github.com/duanegoodner/srepkg/blob/main/CODE_OF_CONDUCT.md).











