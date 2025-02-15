# Comparing with a similar tool: [pipx](https://github.com/pypa/pipx)

*srepkg* is in many ways similar to the widely used tool [pipx](https://github.com/pypa/pipx) which also allows users to install a Python package in an isolated environment and then access its command line tool(s) from another environment. Key differences between *srepkg* and *pipx* include:

* The actions that ensure isolation via *pipx* are taken by the user at the time of package installation. With *srepkg*, source code is wrapped in an isolating layer prior to installation, and the re-packaged application is automatically placed in its own environment during installation. 

* The CLI of a package that has been re-packaged by *srepkg* accessible from an environment containing its access package. pipx allows global access to isolated command line applications. 

* *pipx* is more mature and feature-rich than srepkg. If you have control of the package installation process, *pipx* will likely be more useful than *srepkg*. However, if you are distributing but not installing a Python CLI app and want to be certain the app is always installed into an isolated environment regardless what happens at install time, consider using *srepkg*.