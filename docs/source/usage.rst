Usage
_____

Command Line Syntax
===================
.. code-block:: console

    usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] [--construction_dir
                [SREPKG_BUILD_DIR]] [--dist_out_dir [DIST_OUT_DIR]] pkg_ref

    positional arguments:
      pkg_ref               Original package to be repackaged. Can be a local
                            path, PyPI package name, or Github repo.

    optional arguments:
      -h, --help            show this help message and exit
      --srepkg_name [SREPKG_NAME]
                            Name to be used for repackaged package. Default is
                            <ORIGINAL_PACKAGE_NAME + srepkg>
      --construction_dir [SREPKG_BUILD_DIR]
                            Directory where non-compressed repackage will be
                            built and saved. If not specified, srepkg
                            is built in a temp directory and deleted after
                            distribution archive creation.
      --dist_out_dir [DIST_OUT_DIR]
                            Directory where srepkg distribution archive is
                            saved. Default is the current working directory.


Output
======
A source distribution of the re-packaged package is saved as a .zip file in the directory from which srepkg is called. This source distribution archive can be installed using pip.