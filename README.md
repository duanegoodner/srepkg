# Srepkg (Solo Repackage)

Add a safeguard to a dependency-laden Python command line  interface (CLI) app to ensure users can only install it in an isolated virtual environment but can access it from outside that environment.

## Description

srepkg is a Python package that wraps an isolation layer around other Python packages. When a package that has been “re-packaged” by srepkg (a.k.a an S-package) is installed in an existing Python environment, a dependency-free "access" package is installed in the pre-existing environment, while the original package and its dependencies are installed in a new, automatically created virtual environment. This package structure prevents dependency conflicts but still exposes the original package’s CLI to the pre-existing environment.

## Getting Started

### Requirements

- Python version 3.6 or higher

### Installing srepkg

From the command prompt:

```
$ pip install git+https://github.com/duanegoodner/srepkg
```

### Requirements for a package to be "re-packagable" into an S-package
To be compatible with srepkg, a package must:
- Be installable via pip
- Have command line entry point(s) specifiied in a setup.py or setup.cfg file.

### Command line syntax for creating an S-package

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



## Example: Repackaging a package from the Python Packaging Index

Let's create a re-packaged version of the Python package [howdoi](https://pypi.org/project/howdoi/). We've chosen howdoi for this example because (a) it has a command line entry point, and (b) it has quite a few non-base Python dependencies (Pygments, cssselect, lxml, pyquery, requests, cache lib, appdirs, keep, rich, and colorama):

```
$ srepkg howdoi

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

Before installing the re-packaged version of howdoi, we will create and activate a new virtual environment just so we can clearly see what is (and what is not) installed into the active virtual environment.

```
$ python -m venv my_venv
$ source my_venv/bin/activate
```

Next, we install the re-packaged version of howdoi, and use the `pip freeze` command to view what is installed in our virtual environment:

```
(my_venv) $ pip install /Users/duane/dproj/howdoisrepkg-2.0.19.zip -q
(my_venv) $ pip freeze
howdoisrepkg @ file:///Users/duane/dproj/howdoisrepkg-2.0.19.zip
```

From the above code block, we see that the only non-base Python package in our current environment is `howdoisrepkg`.  We then run a quick test of the `howdoi` command, and confirm that it works, despite the fact that Neither howdoi nor any of its dependencies are present.

```
(my_venv) $ howdoi redirect standard out
yourcommand &> filename
```



## Comparing srepkg with a similar tool: [pipx](https://github.com/pypa/pipx)

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python CLI app in an isolated environment and then access that package from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code is wrapped in an isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether the user takes any other action to isolate it.
* Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the `pip install` command was called. pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. 
* pipx is more mature and feature-rich than srepkg. If you are looking for a tool to isolate Python command line apps that <u>you</u> will be installing and using, I highly recommend pipx. However, if you will be distributing a Python CLI app and want to be certain that the app is always installed into an isolated environment - regardless what the user knows about virtual environments and/or decides to do at install time - then consider using srepkg.



