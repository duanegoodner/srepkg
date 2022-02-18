# Solo Repackage (srepkg) :package:

### Re-package a Python application with a layer that makes it impossible to install the app anywhere *except* in its own isolated environment.

...because accidentally installing that dependency-laden app into the wrong environment can be oh so painful. :grimacing:

## Description

Builds a re-packaged version of an existing packaged application. When the re-packaged version of the app is launched, it automatically creates its own new virtual env and installs and runs the original package in the new env. The  active environment used to launch the re-packaged application remains active and unchanged during and after installation and execution of the re-packaged app.

## Getting Started

### Requirements

- Python version 3.6 or higher
- pip* <br>

*pip is most likely included with your Python 3.6+ installation, but if that is not the case, you can install it with the command:

`$ python -m ensurepip --upgrade`

### Installing

From the command prompt:

`$ pip install git+https://github.com/duanegoodner/srepkg`


## Using srepkg

### Requirements for an Application to be "Re-packagable" with srepkg

- App needs to be a package that can be installed with pip
- Access to source code


### Steps for repackaging an app:


`$ srepkg original_package_path [srepkg_name]`



