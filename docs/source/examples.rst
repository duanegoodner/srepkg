Examples
========

Repackaging a package from the Python Packaging Index
-----------------------------------------------------
Let's create a re-packaged version of the Python package [howdoi](https://pypi.org/project/howdoi/). We've chosen howdoi for this example because (a) it has a command line entry point, and (b) it has quite a few non-base Python dependencies (Pygments, cssselect, lxml, pyquery, requests, cache lib, appdirs, keep, rich, and colorama):

.. code-block:: console

        $ srepkg howdoi

    Downloading howdoi
    Repackaging howdoi-2.0.19
    Building source distribution of repackaged package

    Original package 'howdoi' has been re-packaged as 'howdoisrepkg'

    The re-packaged version has been saved as source distribution archive file:
    /Users/duane/dproj/howdoisrepkg-2.0.19.zip
    'howdoisrepkg' can be installed using:
    pip install /Users/duane/dproj/howdoisrepkg-2.0.19.zip

    After installation, 'howdoisrepkg' will provide command line access to the
    following commands:
    howdoi

Before installing the re-packaged version of howdoi, we will create and activate a new virtual environment just so we can clearly see what is (and what is not) installed into the active virtual environment.

.. code-block:: console

    $ python -m venv my_venv
    $ source my_venv/bin/activate

Next, we install the re-packaged version of howdoi, and use the `pip freeze` command to view what is installed in our virtual environment:

.. code-block:: console

    (my_venv) $ pip install /Users/duane/dproj/howdoisrepkg-2.0.19.zip -q
    (my_venv) $ pip freeze
    howdoisrepkg @ file:///Users/duane/dproj/howdoisrepkg-2.0.19.zip

From the above code block, we see that the only non-base Python package in our current environment is `howdoisrepkg`.  We then run a quick test of the `howdoi` command, and confirm that it works, despite the fact that Neither howdoi nor any of its dependencies are present.

.. code-block:: console

    (my_venv) $ howdoi redirect standard out
        yourcommand &> filename


Repackaging using Github as the source
--------------------------------------
We can also repackage source code from a Github repo.

Any of the following commands would build a re-packaged version of howdoi:

.. code-block:: console

    $ srepkg git+https://github.com/gleitz/howdoi.git
    $ srepkg git+https://github.com/gleitz/howdoi@bugfix/remove-pathlib
    $ srepkg git+https://github.com/gleitz/howdoi.git@4ac146f5aaaf33d8630f6b616727e5b000965863

The first of these commands would repackage the head of the default branch. The second would repackage the head of a branch named 'bugfix/remove-pathlib', and the third would repackage code from commit with SHA = 4ac146f5aaaf33d8630f6b616727e5b000965863.


Repackaging a local package
---------------------------

A package saved locally can be repackaged using:

.. code-block:: console

    $ srepkg [PATH TO DIRECTORY CONTAINING setup.py]

