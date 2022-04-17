# Srepkg (Solo Repackage)
Add a safeguard to your dependency-laden Python package to ensure it can only be installed in an isolated virtual environment.

## Description
srepkg is a Python package that wraps an isolation layer around the source code of other Python packages. When a package that has been “re-packaged” by srepkg is installed using a pip install command from an existing Python environment, a new virtual environment is automatically created. The original package and its dependencies are installed there to avoid the possibility of any dependency-conflicts, but the original package’s command line entry points are still accessible from the pre-existing environment.

## Comparing srepkg with a similar tool: pipx

srepkg is in many ways similar to the widely used tool pipx which also allows users to install a Python package in an isolated environment and then access the package’s command line interface from another environment. Key differences between srepkg and pipx include:
* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code must be wrapped with the isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether or not the user takes any other action to isolate it.
* Pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the install command was called.


## Getting Started

### Requirements

- Python version 3.6 or higher
- pip version 21.3 or higher


### Installing srepkg

From the command prompt:

```
$ pip install git+https://github.com/duanegoodner/srepkg
```

### Requirements for an Application to be "Re-packagable" with srepkg

- Must be installable via pip
- Must contain a setup.cfg file that specifies the package name. 
  - If the package has any console script entry points, they must be specified in the setup.cfg file.
  If the root of the package source code differs from the directory that contains the setup.cfg file (e.g. if a /src layout is used) the, the source code root path must be specified using the package_dir parameter in the [options] section of setup.cfg.
  - At least some part of the package’s functionality must be accessible from the command line (either through a console script entry point, or a top-level __main__.py script that can be run using `$ python -m <package_name>`.

## Usage

### Command line syntax 

```
usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] orig_pkg_path

positional arguments:
  orig_pkg_path         Path of directory containing original package's setup.cfg file

optional arguments:
  -h, --help            show this help message and exit
  --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package.
                        If not specified, defaults to the original package name appended with 'srepkg'

```

### Output

A re-packaged package is saved in `~/srepkg_pkgs/ORIGINAL_PACKAGE_NAME_as_SREPKG_NAME`. For example, if a package named `mypackage` with its `setup.cfg` file located in the current working directory is repackaged using the command `$ srepkg mypackage`, repackaged version `mypackagesrepkg` will be saved in `~/srepkg_pkgs/mypackage_as_mypackagesrepkg`.


### Example

```
.
├── setup.cfg
├── setup.py
└── src
    └── myproj
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        └── test.py
```

#### setup.cfg
```
[metadata]
name = myproj

[options]
package_dir=
    =src
install_requires =
    numpy

[options.entry_points]
console_scripts =
    my_multiply = myproj.app:run
    my_test = myproj.test:first_test
```

#### setup.py
```
import setuptools

setuptools.setup()
```


#### \_\_init__.py (empty)
```

```


#### \_\_main__.py
```
import myproj.app as app


def main():
    app.run()


if __name__ == "__main__":
    main()
```

#### app.py
```
import argparse
import numpy as np


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('factor', type=int)
    args = parser.parse_args()
    init_array = np.array([1, 2, 3])
    print(f'{args.factor} * {init_array} = {args.multiplier * init_array}')


if __name__ == '__main__':
    run()
```

#### test.py
```
def simple_test():
    print('This is a test')
```

#### Running srepkg
```
$ srepkg .
SRE package built from: myproj
SRE package saved in: /Users/duane/srepkg_pkgs/myproj_as_myprojsrepkg
```


#### Resulting srepkg file structure
```
$ pwd
/Users/duane/srepkg_pkgs

$ ls
myproj_as_myprojsrepkg
```


```
.
└── myproj_as_myprojsrepkg
    ├── MANIFEST.in
    ├── inner_pkg_installer.py
    ├── myprojsrepkg
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── pkg_names.py
    │   ├── setup_off.cfg
    │   ├── setup_off.py
    │   ├── src
    │   │   └── myproj
    │   │       ├── __init__.py
    │   │       ├── __main__.py
    │   │       ├── app.py
    │   │       └── test.py
    │   ├── srepkg_control_components
    │   │   ├── __init__.py
    │   │   ├── entry_points.py
    │   │   ├── srepkg_control_paths.py
    │   │   └── srepkg_controller.py
    │   └── srepkg_entry_points
    │       ├── __init__.py
    │       ├── my_multiply.py
    │       └── my_test.py
    ├── pkg_names.py
    ├── setup.cfg
    └── setup.py
```

#### Share with user who needs an older version of numpy

```
$ pip freeze
numpy==1.21.0
```

```
$ cd packages_from_colleagues

$ ls
myproj_as_myprojsrepkg

$ pip install ./myproj_as_myprojsrepkg
Processing ./myproj_as_myprojsrepkg
  Preparing metadata (setup.py) ... done
Building wheels for collected packages: myprojsrepkg
  Building wheel for myprojsrepkg (setup.py) ... done
  Created wheel for myprojsrepkg: filename=myprojsrepkg-0.0.0-py3-none-any.whl size=31540190 sha256=6b0297061eb7adb17539ddc7ecdd0e1543f239258a67901588f7314bab3e76aa
  Stored in directory: /private/var/folders/87/kc464rb570b1gpjfxbjh1xtm0000gn/T/pip-ephem-wheel-cache-2k7a8_vl/wheels/97/27/6c/2cbb7bb53a4e8134b424ad4328487bd34c4322004860d236e2
Successfully built myprojsrepkg
Installing collected packages: myprojsrepkg
Successfully installed myprojsrepkg-0.0.0

$ pip freeze
myprojsrepkg @ file:///Users/duane/srepkg_pkgs/myproj_as_myprojsrepkg
numpy==1.21.0


```





