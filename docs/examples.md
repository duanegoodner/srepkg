# Examples

## 1. Repackaging a local package

The srepkg Github repo has a small example CLI package named testproj saved in `srepkg/src/test/package_test_cases/testproj/`. In testproj's setup.cfg file, we can see that it depends on non-standard library package numpy.

From the root of the srepkg repo, we can re-package testproj and save the S-package distribution archive to our home directory using:

```
$ srepkg src/srepkg/test/package_test_cases/testproj -d ~ 
```

When the re-packaging process is complete, we have the following output:

```
Repackaging testproj
Building source distribution of repackaged package
Original package 'testproj' has been re-packaged as 'testprojsrepkg'

The re-packaged version has been saved as source distribution archive file: /Users/duane/testprojsrepkg-0.0.0.zip
'testprojsrepkg' can be installed using:  pip install /Users/duane/testprojsrepkg-0.0.0.zip

After installation, 'testprojsrepkg' will provide command line access to the following commands:
my_test
```

Before proceeding, let's create and activate a new virtual environment so we can clearly see what package(s) do / don't get added to the environment when we install testprojsrepkg.

```
$ python -m venv my_venv
$ source my_venv/bin/activate
```

Now we are ready to install our S-package with pip:

```
(my_venv) $ pip install ~/testprojsrepkg-0.0.0.zip -q 
```

We can use pip freeze to confirm that howdoisrepkg is the only non-standard library package installed in the environment.

```
(my_venv) $ pip freeze
testprojsrepkg @ file:///Users/duane/testprojsrepkg-0.0.0.zip
```

Neither original package testproj nor its dependency numpy is installed in the active environment, but we can still access the testproj CLI in the same way we would if it were installed in the active environment

```
(my_venv) $ my_123_multiplier -h
usage: my_123_multiplier [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer. Displays the resulting array as well as the version
of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

optional arguments:
  -h, --help  show this help message and exit

(my_venv) $ my_123_multiplier 2
2 * [1 2 3] = [2 4 6]
numpy version used by this program = 1.22.4
```

## 2. Repackaging a PyPI package

An S-package can also be built by providing a PyPI package name as the package_reference argument. Here, we repackage the [PyPI package *howdoi*](https://pypi.org/project/howdoi/). Let's continue working in the virtual environment created in the previous example.

```
(my_venv) $ srepkg howdoi -d ~
Original package howdoi has been repackaged as howdoisrepkg
howdoisrepkg has been saved as source distribution /Users/duane/howdoisrepkg-2.0.19.zip
'howdoisrepkg' can be installed using: pip install /Users/duane/howdoisrepkg-2.0.19.zip
After installation, 'howdoisrepkg' will provide command line access to the following commands:
howdoi
```

We can then install the S-package, confirm that we have access to the original package's CLI, and run `pip freeze` to list the non-standard packages installed in the current environment.

```
(my_venv) $ pip install ~/howdoisrepkg-2.0.19.zip -q
(my_venv) $ howdoi redirect standard out
yourcommand &> filename
(my_venv) $ pip freeze
	testprojsrepkg @ file:///Users/duane/testprojsrepkg-0.0.0.zip
	howdoisrepkg @ file:///Users/duane/dproj/howdoisrepkg-2.0.19.zip
```

Note that *howdoi* has a number dependencies (Pygments, cssselect, lxml, pyquery, requests, cachelib, appdirs, keep, rich, and colorama), but none of these packages are installed in my_venv.

## 3. Repackaging a package from a Github repo

When the package reference argument is a Github repository, it takes the same form that pip uses when installing a package from Github. Below are examples of how to build S-packages based on code from the [*howdoi* Github repository](https://github.com/gleitz/howdoi).

### Head of the default branch

```
$ srepkg git+https://github.com/gleitz/howdoi.git
```

### Head of a specific branch

Re-package the head of branch *bugfix/remove-pathlib* using:

```
$ srepkg git+https://github.com/gleitz/howdoi@bugfix/remove-pathlib
```

### Specific commit

Re-package commit *ac146f5aaaf33d8630f6b616727e5b000965863*:

```
$ srepkg git+https://github.com/gleitz/howdoi.git@4ac146f5aaaf33d8630f6b616727e5b000965863
```

### Specific release

Re-package release *2.0.17*:

```
$ srepkg git+https://github.com/gleitz/howdoi.git@v2.0.17
```