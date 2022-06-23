# Comparing srepkg with a similar tool: [pipx](https://github.com/pypa/pipx)

srepkg is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python CLI app in an isolated environment and then access that package from another environment. Key differences between srepkg and pipx include:

* The actions that ensure isolation via pipx (i.e. installing a package with pipx instead of pip) are taken by the user at the time of package installation. With srepkg, source code is wrapped in an isolating layer prior to installation. Upon installation, the re-packaged application is automatically placed in its own environment, regardless of whether the user takes any other action to isolate it.

* Packages that have been modified by srepkg and then installed are only accessible from the pre-existing environment from which the `pip install` command was called. pipx allows isolated applications to be installed with global access, or run in a temporary virtual environment. 

* pipx is more mature and feature-rich than srepkg. If you are looking for a tool to isolate Python command line apps that <u>you</u> will be installing and using, pipx will likely be more useful than srepkg. However, if you will be distributing a Python CLI app and want to be certain that the app is always installed into an isolated environment - regardless what the user knows about virtual environments and/or decides to do at install time - then consider using srepkg.