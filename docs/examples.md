# Examples

## Demo #1: Repackaging a local package that depends on old version of *numpy*

The following demo shows how we take an original package that has a dependency conflict what's already installed in an active Python environment, re-package with *srepkg*, install the re-packaged version, and access the original package's CLI from the active environment, without experiencing any dependency conflict.

### Environment Setup

We will be using some test files from the ***srepkg*** repository, so instead of installing from PyPI, we will just clone the ***srepkg*** repo and install from there
```
$ conda create -n srepkg_oldmath_test python=3.10
$ conda activate srepkg_oldmath_test
$ git clone https://github.com/duanegoodner/srepkg
$ cd srepkg
$ pip install .
```
Then, let's install a version of ***numpy*** that is relatively new (as of Feb. 2025).
```
$ pip install numpy==2.2.2
```
Later on, we will use the presence of this current numpy version to help illustrate the absence of dependency conflicts.

### Repackage ***oldmath*** as *oldmathsrepkg*

Next, we will re-package a simple local Python package ***oldmath*** with its source files located `./test/demos/oldmath/`. ***oldmath*** depends on ***numpy 1.26.4***.

```
$ srepkg test/demos/oldmath/

✅ Building original package wheel from source code
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing oldmath-0.1.0-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	oldmathsrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
✅ Building srepkg sdist
	oldmathsrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0.tar.gz

oldmathsrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/oldmathsrepkg-0.1.0.tar.gz
Upon installation, oldmathsrepkg will provide access to the following command line entry points: 
	• oldmath
```
The repackaged version of ***oldmath*** is called ***oldmathsrepkg***, and it has been built into both `wheel` and `sdist` distributions.

> [!NOTE]
> The `-n` option can be used to assign a custom name to the repackaged package and distributions.

### Install and test ***oldmathsrepkg***

Next, install ***oldmathsrepkg*** from the newly created wheel:
```
$ pip install ./srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
```
Now, we can get some info about the `oldmath` command:
```
$ oldmath --help

usage: oldmath [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer. Displays the resulting array as well as the version of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

options:
  -h, --help  show this help message and exit
```
Next, we run:
```
$ oldmath 2025

2025 * [1 2 3] = [2025 4050 6075]
numpy version used by this program = 1.26.4
```

### Confirm absence of dependency conflicts

Double-check the version of ***numpy*** that's installed in our active Python environment:
```
$ pip freeze | grep numpy

numpy==2.2.2
```

Finally, confirm that we do not have any dependency conflicts:
```
$ pip check

No broken requirements found.
```

The key thing to note is that ***oldmath***, which we can access from the active Python environment uses ***numpy 1.26.4***, but we still have ***numpy 2.2.2*** installed the active environment.


### Distribute ***oldmathsrepkg*** with confidence that it will not break environments

We can now send the ***oldmathsrepkg*** *wheel* and/or *sdist* (saved under `./srepkg_dists`) to colleagues, knowing that install it will not cause problems in their Python environment, even if they are using a current version of `numpy` and do not know much / anything about Python dependencies and environments.



## Demo #2: Re-package a distribution obtained from PyPI

We can re-package the latest version of ***scrape*** available on the PyPI using the following:
```
$ srepkg scrape

✅ Retrieving scrape from Python Packaging Index
	Downloaded files:
	• scrape-0.11.3-py3-none-any.whl
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing scrape-0.11.3-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	scrapesrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
✅ Building srepkg sdist
	scrapesrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz

scrapesrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz
Upon installation, scrapesrepkg will provide access to the following command line entry points: 
	• scrape
```

We can then install ***scrapesrepkg***, and try using it to scrape http://example.com/:
```
$ pip install pip install srepkg_dists/scrapesrepkg-0.11.3-cp310-abi3-linux_x86_64.whl

Processing ./srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
Installing collected packages: scrapesrepkg
Successfully installed scrapesrepkg-0.11.3

$ scrape http://example.com/ -pt

Failed to enable cache: No module named 'requests_cache'
Example Domain
Example Domain
This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.
More information...
```

If we wanted to re-package a specific version (e.g.`0.11.0`) from PyPI we could do this:
```
$ srepkg scrape -r 0.11.0
```


## Demo #3: Re-package a distribution obtained from GitHub

We can also re-package using a GitHub repo as the original source:
```
srepkg https://github.com/huntrar/scrape      
✅ Cloning https://github.com/huntrar/scrape into temporary directory
✅ Building original package wheel from source code
✅ Creating virtual env
	Virtual env created with the following pypa packages installed:
	• pip==25.0.1
	• setuptools==75.8.0
	• wheel==0.45.1
✅ Installing scrape-0.11.3-py3-none-any.whl in virtual env
✅ Building srepkg wheel
	scrapesrepkg wheel saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
✅ Building srepkg sdist
	scrapesrepkg sdist saved as: /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz

scrapesrepkg can be installed using either of the following commands:
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
	• pip install /home/duane/dproj/srepkg/srepkg_dists/scrapesrepkg-0.11.3.tar.gz
Upon installation, scrapesrepkg will provide access to the following command line entry points: 
	• scrape
```

If we want to re-package a specific commit from the ***scrape*** GitHub repo, we can do this:
```
$ srepkg https://github.com/huntrar/scrape -g 1dfd98bb0a308ef2a45b1e5dd136c38b17c27bc7
```
If we want to re-package a specific release or tag, we would do this:
```
$ srepkg https://github.com/huntrar/scrape -g 0.11.2 
```


