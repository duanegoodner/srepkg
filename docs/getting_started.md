# Getting Started

## Requirements

* Python version 3.6 or higher
* [pip](https://pip.pypa.io/en/stable/installation/#)
* To be compatible with srepkg, a package must:
    * Be installable via pip
    * Have command line entry point(s) specifiied in a setup.py or setup.cfg file.

## Installing srepkg

```
$ pip install git+https://github.com/duanegoodner/srepkg
```

## Usage

```
usage: srepkg [-h] [-n [SREPKG_NAME]] [-c [CONSTRUCTION_DIR]] [-d [DIST_OUT_DIR]]
       orig_pkg_ref

positional arguments:
  orig_pkg_ref          A reference to the original package to be repackaged.
                        Can be a local path to a directory where a package's
                        setup.py resides, a PyPI package name, or Github repo

optional arguments:
  -h, --help            show this help message and exit
  -n [SREPKG_NAME], --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package. Default is
                        <ORIGINAL_PACKAGE_NAMEsrepkg>
  -c [CONSTRUCTION_DIR], --construction_dir [CONSTRUCTION_DIR]
                        Directory where non-compressed repackage will be built
                        and saved. If not specified, srepkg is built in a temp
                        directory and deleted after distribution archive creation
  -d [DIST_OUT_DIR], --dist_out_dir [DIST_OUT_DIR]
                        Directory where srepkg distribution .zip file is saved.
                        Default is the current working directory.
```

## Output

srepkg re-packages the original package specified by `orig_pkg_ref` into an S-package saved as a .zip file. By default, this .zip file is saved in the user's current working directory and is named `ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip` where ORIGINAL_NAME and ORIGINAL_VERSION are the respective name and version specified in the original package's setup.cfg or setup.py file.

## Installing an S-package

A distribution archive produced by srepkg can be installed using pip. If we are in the directory containing S-package `ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip`, we can install it with the command:

```
$ pip install ORIGINAL_NAMEsrepkg-ORIGINAL_VERSION.zip
```

## Using an S-package

Once an S-package has been installed in a user's global Python environment, or (preferably) a virtual environment, all command line entry points of the original CLI application are available in that environment. The syntax of these commands is identical to that of the original application.
