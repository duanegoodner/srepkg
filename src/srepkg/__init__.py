"""
Solo Re-Package (srepkg)
=========================

Builds a re-packaged version of existing packaged application. When the
re-packaged version of the app is launched, it automatically creates its own new
virtual env and installs and runs the original package in the new env. The
active environment used to launch the re-packaged application remains active and
unchanged during and after installation and execution of the re-packaged app.
"""