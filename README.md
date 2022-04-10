# Srepkg (Solo Repackage)
* Wraps a Python package with an isolation layer that ensures it can only be installed in an isolated virtual environment
* Avoids the need for manual environment management at install time.



## Description
srepkg is a Python package that modifies other Python packages by adding a layer that affects how and where the modified packages are installed. When a “re-packaged” package is installed via a pip from a pre-existing environment, the isolation layer that was added by srepkg creates a new virtual environment. The original package and its dependencies are installed in this newly-created, isolated environment.

A package with the sole purpose of providing access to the command line entry points of the original package is installed in the pre-existing environment. However, since this access package does not contain any dependencies (nor any code from the original package) there is no risk of dependency conflicts with any other packages in the pre-existing environment.

srepkg is in many ways similar to the widely used tool pipx which allows users to install and run Python applications in isolated environments. Key differences between srepkg and pipx include: 
* The actions that ensure isolation via pipx (i.e. using pipx instead of pip) are taken by the user at the time of package installation. srepkg requires that isolating modifications be made to a package before any install command is called, but then does not require the user to perform any action other than a standard pip installation.
* Pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the install command was called.


## Getting Started

### Requirements

- Python version 3.6 or higher
- pip* <br>

*pip is most likely included with your Python 3.6+ installation, but if that is not the case, you can install it with the command:

```
$ python -m ensurepip --upgrade
```

### Installing srepkg

From the command prompt:

```
$ pip install git+https://github.com/duanegoodner/srepkg
```


## Using srepkg

### Requirements for an Application to be "Re-packagable" with srepkg

- App needs to be a package that can be installed with pip
- Access to source code


### Steps for repackaging an app:


`$ srepkg original_package_path [srepkg_name]`



