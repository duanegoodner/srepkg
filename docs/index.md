# **Welcome to the Solo Repackage (*srepkg*) Documentation Site**


---

> **`srepkg`** is a Python package that wraps other Python packages with an isolation layer, ensuring installation in an isolated virtual environment while preserving access to the original package's command-line interface in an external environment. 

---

## 📦 Availability

***srepkg*** is available on [**PyPI**](https://pypi.org/project/srepkg/) and [**GitHub**](https://github.com/duanegoodner/srepkg).

## 📖 Description

When a package wrapped in an isolation layer by ***srepkg*** is installed in an active, pre-existing Python environment:

- The original package plus its dependencies are installed in a new, automatically created virtual environment.
- A dependency-free "access" package installed in the pre-existing environment contains a controller module capable of making calls to the Python interpreter in the newly created environment.
- This enivronment and package structure exposes the original package’s CL to the pre-existing environmen while ensuring that none of the original package's dependencies conflict with packages in the pre-existing environment.

## 🎯 Use Cases

### For Package Distributors
- ***srepkg*** can be useful if you are sharing a Python command line application, and you want to be certain that users can install and run it without worrying about dependency conflicts. 
- Wrapping a CL package with ***srepkg*** prior to sharing the package with other users will ensure that wherever the package is installed, it does not introduce dependency conflicts into a user's existing Python environment &mdash; even if the user knows nothing about managing Python environments.

### For Package Users
- Any existing CL package obtained from Python Packaging Index (PyPI) or GitHub can be wrapped with ***srepkg*** prior to installation.
- If you want the original package commands to be accessible from a single environment (that is distinct from the isolated environment where the original package is installed), then ***srepkg*** is likely a good option.
- However, if you want the isolated package's command interface to be available globally and/or want a much more mature isolation tool, then [***pipx***]("https://github.com/pypa/pipx") is likely a better choice.










[//]: # (## Commands)
[//]: # (* `mkdocs new [dir-name]` - Create a new project.)
[//]: # (* `mkdocs serve` - Start the live-reloading docs server.)
[//]: # (* `mkdocs build` - Build the documentation site.)
[//]: # (* `mkdocs -h` - Print help message and exit.)

