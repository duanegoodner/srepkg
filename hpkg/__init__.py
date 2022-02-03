"""
Hpkg ("helmeted" package)
=========================

Builds a "H-packaged" version of an existing application.

When the H-packaged version is launched, it automatically creates, loads
dependencies into, and runs in its own new virtual env. The active environment
used to launch the H-packaged application remains active and unchanged.
"""