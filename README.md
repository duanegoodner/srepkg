# Srepkg (Solo Repackage)

Add a safeguard to a dependency-laden Python command line  interface (CLI) apps to ensure users can only install it in an isolated virtual environment but can still access it from outside that environment.



## Description

srepkg is a Python package that wraps an isolation layer around other Python packages. When a package that has been “re-packaged” by srepkg is installed in an existing Python environment, a dependency-free "access" package is installed in the pre-existing environment, while the original package and its dependencies are installed in a new, automatically created virtual environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment.

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

### Command line syntax

```
usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] [--srepkg_build_dir [SREPKG_BUILD_DIR]] pkg_ref

positional arguments:
  pkg_ref               Original package to be repackaged. Can be a local path, PyPI package name, or Github repo.

optional arguments:
  -h, --help            show this help message and exit
  --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. Default is <ORIGINAL_PACKAGE_NAME + srepkg>
  --srepkg_build_dir [SREPKG_BUILD_DIR]
                        Directory where non-compressed repackage will be built and saved. If not specified, non-
                        compressed repackage is not saved.
```

### Output

A source distribution of the re-packaged package is saved as a .zip file in the directory from which srepkg is called. This source distribution archive can be installed using pip.



## Example: Repackaging a package from the Python Packaging Index

For illustrative purposes, let's start by creating new Python virtual environment, activating this environment, and installing srepkg into it:

```
$ python -m venv my_venv
$ source my_venv/bin/activate
$ (my_venv) $ pip install git+https://github.com/duanegoodner/srepkg -q
```

We can use `pip freeze`  to see that srepkg is the only non-base Python package installed in this environment:

```
(my_venv) $ pip install git+https://github.com/duanegoodner/srepkg -q
(my_venv) $ pip freeze
srepkg @ git+https://github.com/duanegoodner/srepkg@ea689c9f9fab92794bd23b9007d5a121f8d0bbf1
```

Now, let's create a re-packaged version of the Python package [howdoi](https://pypi.org/project/howdoi/). We've chosen howdoi for this example because (a) it has a command line entry point, and (b) it has quite a few non-base Python dependencies (Pygments, cssselect, lxml, pyquery, requests, cache lib, appdirs, keep, rich, and colorama):

```
(my_venv) $ srepkg howdoi
Downloading howdoi
Repackaging howdoi-2.0.19
Building source distribution of repackaged package

Original package 'howdoi' has been re-packaged as 'howdoisrepkg'

The re-packaged version has been saved as source distribution archive file:
/Users/duane/dproj/howdoisrepkg-2.0.19.zip
'howdoisrepkg' can be installed using:
pip install /Users/duane/dproj/howdoisrepkg-2.0.19.zip

After installation, 'howdoisrepkg' will provide command line access to the following commands:
howdoi
```

Next, we install the re-packaged version of howdoi, and perform a quick test to confirm that we can use the howdoi command:

```
(my_venv) $ pip install /Users/duane/dproj/howdoisrepkg-2.0.19.zip -q
(my_venv) $ howdoi redirect standard out
yourcommand &> filename
```

Finally, we run pip freeze again and see that none of the howdoi package's dependencies are installed in our current virtual environment - even though we have access to the howdoi command line entry point:

```
(my_venv) $ pip freeze
howdoisrepkg @ file:///Users/duane/dproj/howdoisrepkg-2.0.19.zip
srepkg @ git+https://github.com/duanegoodner/srepkg@ea689c9f9fab92794bd23b9007d5a121f8d0bbf1
```



## Comparing srepkg with a similar tool: [pipx](https://github.com/pypa/pipx)

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python CLI app in an isolated environment and then access that package from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code is wrapped in an isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether the user takes any other action to isolate it.
* Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the `pip install` command was called. pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. 
* pipx is more mature and feature-rich than srepkg. If you are looking for a tool to isolate Python command line apps that <u>you</u> will be installing and using, I highly recommend pipx. However, if you will be distributing a Python CLI app and want to be certain that the app is always installed into an isolated environment - regardless what the user knows about virtual environments and/or decides to do at install - then consider using srepkg.



