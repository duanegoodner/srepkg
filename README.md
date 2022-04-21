# Srepkg (Solo Repackage)

Add a safeguard to your dependency-laden Python package to ensure it can only be installed in an isolated virtual environment.



## Description

srepkg is a Python package that wraps an isolation layer around the source code of other Python packages. When a package that has been “re-packaged” by srepkg is installed using a pip install command from an existing Python environment, a new virtual environment is automatically created. The original package and its dependencies are installed there to avoid the possibility of any dependency-conflicts, but the original package’s command line entry points are still accessible from the pre-existing environment.



## Getting Started

### Requirements

- Python version 3.6 or higher
- pip version 21.3 or higher

### Installing srepkg

From the command prompt:

```
$ pip install git+https://github.com/duanegoodner/srepkg
```

### Requirements for a package to be "re-packagable"
To be compatible with srepkg, a package must:
- Be installable via pip
- Have command line entry point(s) through console script entry point(s) and/or a top-level  `__main__.py` script that can be run using `$ python -m <package_name>`.
- Contain a setup.cfg file that specifies the package name. 
  - If the package has any console script entry points, they must be specified in the setup.cfg file.
  - If the source root path is not the same directory that contains the `setup.cfg` file (e.g. if a /src layout is used), the source code root path must be specified using the `[oprtions]package_dir` parameter in `setup.cfg`.

### Command line syntax

```
usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] orig_pkg_path

positional arguments:
  orig_pkg_path         Path of directory containing original package's setup.cfg file

optional arguments:
  -h, --help            show this help message and exit
  --srepkg_name [SREPKG_NAME]
                        Name to be used for repackaged package.
                        If not specified, defaults to the original package name appended 														with 'srepkg'
```

### Output

A re-packaged package is saved in `~/srepkg_pkgs/ORIGINAL_PACKAGE_NAME_as_SREPKG_NAME`. This package can be installed using:

```
$ pip install ~/srepkg_pkgs/ORIGINAL_PACKAGE_NAME_as_SREPKG_NAME
```

### Quick Example

Let's pretend that:

* We have built a package called *weeks* with a command line interface that displays the number of weeks remaining in the calendar year when the user enters the commane `$ how_many`.
* The date and time manipulation package arrow is a dependency of weeks
* The setup.cfg and setup.py files for weeks are both located in directory `~/projects/weeks`
* We are working in a freshly created virtual environment and that only the standard Python library is installed in this environment

The process of installing and running weeks without a srepkg isolation layer could go like this:

```
$ pip freeze
# (blank output since environment only contains standard library)

$ pip install ~/projects/weeks --quiet

$ pip freeze
arrow==1.2.2
python-dateutil==2.8.2
six==1.16.0
weeks==1.0.1

$ how_many
There are 28 weeks remaining in the current calendar year.
```

Installing weeks gives us the expected command line functionality. I also causes the packages *arrow*, *python-dateutil*, and *six* to be installed into the environment since *weeks* depends on *arrow* which depends on *python-dateutil* which depends on *six*. We can get back to our "fresh" environment by uninstalling these four packages:

```
$ pip uninstall arrow python-dateutil six weeks --quiet
Proceed (Y/n)? y
Proceed (Y/n)? y
Proceed (Y/n)? y
Proceed (Y/n)? y

$ pip freeze
# (blank output since we are back to only the standard library)
```

Now, we are ready to try using weeks with srepkg. The process of re-packaging weeks and then installing and running the re-packaged version looks like this:

```
$ srepkg ~/projects/weeks
srepackage built from: /Users/duane/projects/weeks
srepackage saved in: /Users/duane/srepkg_pkgs/weeks_as_weekssrepkg

$ pip install ~/srepkg_pkgs/weeks_as_weekssrepkg --quiet

$ pip freeze
@ file:///Users/duane/srepkg_pkgs/weeks_as_weekssrepkg

$ how_many
There are 28 weeks remaining in the current calendar year.
```

 Once again, the `how_many` command works, but now, there is only one non-standard-library package in our active virtual environment - *weekssrepkg*. This package has access to all command line entry points of weeks which (along with its dependencies) has been installed in a separate environment.



## Comparing srepkg with a similar tool: [pipx](https://github.com/pypa/pipx)

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python package in an isolated environment and then access the package’s command line interface from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code must be wrapped with the isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether the user takes any other action to isolate it.
* pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the `pip install` command was called.



## A more detailed example and use case: re-packaging and sharing *testproj*

In the following example, we use *srepkg* to build an isolation layer around the source code of a small package called *testproj*, and then install and run the resulting package *testprojsrepkg*.

### *testproj* file structure

```
testproj
├── setup.cfg
├── setup.py
└── src
    └── testproj
        ├── __init__.py
        ├── __main__.py
        ├── app.py
        └── test.py
```

The /src layout used here is not a requirement for use with srepkg. It's just what `testproj` happens to use. The contents of each file in the package are shown below.

### *testproj* file contents	

#### setup.cfg

```ini
[metadata]
name = testproj

[options]
package_dir=
    =src
packages = find:
install_requires =
    numpy >= 1.22

[options.packages.find]
where = src

[options.entry_points]
console_scripts =
    my_project = testproj.app:run
    my_test = testproj.test:simple_test
```

The setup.cfg file specifies `testproj` needs numpy version >= 1.22. This file also declares two command line entry points:
* Function `run` in `app.py` can be accessed with the command `my_project`.
* Function `simple_test` in test.py can be accessed with the command`my_test`.

#### setup.py

```python
import setuptools

setuptools.setup()
```

Since we included everything needed by setuptools in `setup.cfg`, our `setup.py` file is very brief. srepkg requires the original package's name and console script entry points be specified in `setup.cfg`. Any of the additional info declared in `setup.cfg` could have been included in either `setup.cfg` or `setup.py`.

#### _\_main__.py

```python
import testproj.app as app


def main():
    app.run()


if __name__ == "__main__":
    main()
```
The top-level `__main__.py` provides command line access `app.run` with the command `python -m testproj factor`. This access method and the `my_project` entry point in setup.cfg are redundant. Both are included for illustrative purposes.

#### app.py

```python
import argparse
import numpy as np


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('factor', type=int)
    args = parser.parse_args()

    initial_array = np.array([1, 2, 3])
    result = args.factor * initial_array

    print(f'{args.factor} * {initial_array} = {result}')
    
    print(f'numpy version used by this program = {np.__version__}')


if __name__ == '__main__':
    run()
```

The `run` function takes an integer provided as a command line argument, multiplies that integer by a numpy array, and then prints the multiplication result as well as the numpy version number.

#### test.py

```python
def simple_test():
    print('This is a test')
```

### Re-packaging testproj



```
$ pip freeze
numpy==1.21.0
```



```
$ srepkg ~/projects/testproj
srepackage built from: ~/projects/testproj
srepackage saved in: ~/srepkg_pkgs/testproj_as_testprojsrepkg

$ pip install ~/srepkg_pkgs/testproj_as_testprojsrepkg --quiet

$ pip freeze
numpy==1.21.0
testprojsrepkg @ file:///Users/duane/srepkg_pkgs/testproj_as_testprojsrepkg

$ my_project 2
2 * [1 2 3] = [2 4 6]
numpy version used by this program = 1.22.3

$ my_test
This is a test

$ python -m testprojsrepkg 2
2 * [1 2 3] = [2 4 6]
numpy version used by this program = 1.22.3

```

