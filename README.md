# srepkg (Solo Repackage)

Add a safeguard to a dependency-laden Python command line  interface (CLI) app to ensure users can only install it in an isolated virtual environment but can run it from outside that environment.

## Description

srepkg is a Python package that wraps an isolation layer around other Python packages. A package that has been "re-packaged" is referred to as an "S-package." When an S-package is installed in an existing Python environment, a dependency-free "access" package is installed in the pre-existing environment, and the original package plus its dependencies are installed in a new, automatically created virtual environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment.

## Getting Started

### Requirements

- Python version 3.6 or higher

### Installing srepkg

From the command prompt:

```
$ pip install git+https://github.com/duanegoodner/srepkg
```

### Requirements for a package to be "re-packagable"
To be compatible with srepkg, a package must:
- Be installable via pip
- Have command line entry point(s) specifiied in a setup.py or setup.cfg file.

### Usage

```
usage: srepkg [-h] [-n [SREPKG_NAME]] [-c [CONSTRUCTION_DIR]] [-d [DIST_OUT_DIR]] orig_pkg_ref

positional arguments:
  orig_pkg_ref          A reference to the original package to be repackaged. Can be a local path to a directory
                        where a package's setup.py resides, a PyPI package name, or Github repo

optional arguments:
  -h, --help            show this help message and exit
  -n [SREPKG_NAME], --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. Default is <ORIGINAL_PACKAGE_NAME + srepkg>
  -c [CONSTRUCTION_DIR], --construction_dir [CONSTRUCTION_DIR]
                        Directory where non-compressed repackage will be built and saved. If not specified, srepkg
                        is built in a temp directory and deleted after distribution archive creation
  -d [DIST_OUT_DIR], --dist_out_dir [DIST_OUT_DIR]
                        Directory where srepkg distribution .zip file is saved. Default is the current working
                        directory.
```

### Output

If the user-provided command just takes the form `$ srepkg orig_pkg_ref`  (i. e. no optional arguments are used), a source distribution of the re-packaged package is saved as a .zip file named <ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip> in the directory from which srepkg is called, and no other files from the srepkg construction process are saved. ORIGINAL_NAME and ORIGINAL_VERSION are the respective name and version of the original package as specified in its setup.py or setup.cfg file. This source distribution archive can be installed as a package named ORIGINAL_NAMEsrepkg using `$ pip install ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip`. 

These name and output directory of the .zip file iscan be customized using the optional -n, and -d arguments. The optional -c argument can be used to save an un-compressed version of the re-packaged package in a user-specified directory.

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
$ python -m venv testprojsrepkg_venv
$ source testprojsrepkg_venv/bin/activate
```

Now we are ready to install our S-package with pip:

```
(testprojsrepkg_venv) $ pip install ~/testprojsrepkg-0.0.0.zip -q 
```

We can use pip freeze to confirm that howdoisrepkg is the only non-standard library package installed in the environment.

```
$ pip freeze
testprojsrepkg @ file:///Users/duane/testprojsrepkg-0.0.0.zip
```

Neither original package testproj nor its dependency numpy is installed in the active environment, but we can still access the testproj CLI in the same way we would if it were installed in the active environment

```
$ my_123_multiplier -h
usage: my_123_multiplier [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer. Displays the resulting array as well as the version
of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

optional arguments:
  -h, --help  show this help message and exit

$ my_123_multiplier 2
2 * [1 2 3] = [2 4 6]
numpy version used by this program = 1.22.4
```

#### 2. Repackaging a PyPI package

An S-package can also be built by providing a PyPI package name as the package_reference argument. Here, we repackage the CLI package *howdoi*. 

```
$ srepkg howdoi -d ~
Original package howdoi has been repackaged as howdoisrepkg
howdoisrepkg has been saved as source distribution /Users/duane/howdoisrepkg-2.0.19.zip
'howdoisrepkg' can be installed using: pip install /Users/duane/howdoisrepkg-2.0.19.zip
After installation, 'howdoisrepkg' will provide command line access to the following commands:
howdoi

$ pip install ~/howdoisrepkg-2.0.19.zip -q
$ howdoi redirect standard out
yourcommand &> filename
```

#### 3. Repackaging a packge from a Github repo

When the package reference argument is a Github repository, it takes the same form that pip uses when installing a package from Github. Below are examples of how to build S-packages based on code from the *howdoi* Github repository.

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

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python CLI app in an isolated environment and then access that package from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code is wrapped in an isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether the user takes any other action to isolate it.
* Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the `pip install` command was called. pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. 
* pipx is more mature and feature-rich than srepkg. If you are looking for a tool to isolate Python command line apps that <u>you</u> will be installing and using, pipx will likely be more useful than srepkg. However, if you will be distributing a Python CLI app and want to be certain that the app is always installed into an isolated environment - regardless what the user knows about virtual environments and/or decides to do at install time - then consider using srepkg.

