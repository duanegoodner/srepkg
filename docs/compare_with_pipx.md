# **⚖️ Comparing with a similar tool: [pipx](https://github.com/pypa/pipx)**

***srepkg*** is in many ways similar to the widely used tool [***pipx***](https://github.com/pypa/pipx) which also allows users to install a Python package in an isolated environment and then access its command line tool(s) from another environment. Key differences between ***srepkg*** and ***pipx*** include:

🎒 **Responsibility Burden:** The actions that ensure isolation via ***pipx*** are taken by the **user** at the time of package installation. With ***srepkg***, a package distributor and/or user wraps a package in an isolating layer prior to installation.

🔌 **CLI Access Model:** The CLI of a package that has been re-packaged by ***srepkg*** accessible from an environment containing its access package. pipx allows global access to isolated command line applications. 

❓ **Which Isolation Tool to Choose:** Since ***pipx*** is more mature and feature-rich than srepkg, if you have control of the package installation process, ***pipx*** will likely be more useful than ***srepkg***. However, if you are distributing but not installing a Python CLI app and want to be certain the app is always installed into an isolated environment regardless what happens at install time, consider using ***srepkg***.