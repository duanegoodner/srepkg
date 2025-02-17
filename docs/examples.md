
# **Examples**

## **Environment Setup**

Some of the examples on this page rely on files from the  `test/` directory of the ***srepkg*** repo. Files from `test/` are not included when installing ***PyPI***, so we will create a fresh Conda environment and install ***srepkg*** there using a cloned GitHub repo as the source.

```shell
conda create -n srepkg_tests=3.10
conda activate srepkg_tests
git clone https://github.com/duanegoodner/srepkg
cd srepkg
pip install .
```

## **Example #1: Using *srepkg* to Avoid a Dependency Conflict**

For this example, we will use two local packages located under `./test/demos/` of the ***srepkg*** repo: ***oldmath*** at `./test/demos/oldmath` and ***newmath*** at `./test/demos/newmath`.

Here is the content of the `pyproject.toml` for ***oldmath***:
```toml
# ./test/demos/oldmath/pyproject.toml

[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "oldmath"
version = "0.1.0"

dependencies = ["numpy<=1.26.4"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[project.scripts]
oldmath = "oldmath.app:run"
```
And here is the `pyproject.toml` for ***newmath***:
```toml
# ./test/demos/newmath/pyproject.toml

[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "newmath"
version = "0.1.0"

dependencies = ["numpy>=2.0.0"]

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]
```

***oldmath*** has a command-line entry point named `oldmath`. ***newmath*** contains module `newmath.array_addition`. Since ***oldmath*** depends on ***numpy<=1.26.4***, and ***newmath*** depends on ***numpy>=2.0.0***, installing both packages in the same environment will result in a dependency conflict.

We can avoid this conflict and still have access to the `oldmath` command and the `newmath.array_addition` module in the same Python environment if use ***srepkg*** to re-package ***oldmath***, and install this re-packaged distribution and a `newmath` in the same environment.

### **Repackage the Package that has a Command Line Entry Point**

First, use ***srepkg*** to re-package ***oldmath*** by running:
```shell
srepkg test/demos/oldmath/
```
The output should look like this:
```
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
The repackaged version of ***oldmath*** is called ***oldmathsrepkg***, and it has been built into both `wheel` and `sdist` distributions located under `./srepkg_distributions`.

### **Install *newmath* and Re-packaged Version of *oldmath* in same Environment**
Next, install ***oldmathsrepkg*** from the newly created wheel:

```shell
pip install ./srepkg_dists/oldmathsrepkg-0.1.0-py3-none-any.whl
```

Then, install the regular ***newmath*** package:
```shell
pip install ./test/demos/newmath/
```

### Check Version of Potentially-Conflicting Dependency

We can check the version of ***numpy*** that has been installed (as a dependency of ***newmath***) by running:
```shell
conda list | grep numpy 
```
The output should be similar to:
```shell
numpy                     2.2.3                    pypi_0    pypi
```
***numpy 2.2.3*** satisfies the ***newmath*** requirement `numpy>=2.0.0` but does not satisfy the ***oldmath*** requirement `numpy<=1.26.4`.


### **Use the Command-Line Interface Exposed by Re-packaged Distribution**

With ***oldmathsrepkg*** installed, we can use the ***oldmath*** command-line interface. 

First, run:
```
oldmath --help
```
The output with the above `--help` option is:
```
usage: oldmath [-h] factor

Multiplies the numpy array [1 2 3] by a user-provided integer.
Displays the resulting array as well as the version of numpy used.

positional arguments:
  factor      An integer that numpy array [1 2 3] will be multiplied by

options:
  -h, --help  show this help message and exit
```
Then use the `oldmath` command to do some math. Running
```
oldmath 2025
```
gives:
```
2025 * [1 2 3] = [2025 4050 6075]
numpy version used by this program = 1.26.4
```

### **Confirm Absence of Dependency Conflicts**

Finally, confirm that we do not have any dependency conflicts:
```
$ pip check

No broken requirements found.
```

The key thing to note is that we can access the command-line interface of ***oldmath*** with its ***numpy<=1.26.4*** requirement and have ***newmath*** installed with its ***numpy>=2.0.0*** requirement **in the same environment without any dependency conflict** .

### ***Share the Re-packaged Distribution with Confidence***

Sharing ***oldmath*** with colleagues and/or the general Python community would run a high risk of breaking a Python environment due to the outdated ***numpy*** requirement. However, we can share ***oldmathsrepkg***, knowing that it will not cause problems a user's Python environment &mdash; even if they are using a current version of ***numpy*** and do not know much / anything about Python dependencies and environments.



## **Example #2: Re-package a Distribution Obtained from PyPI**

We can re-package the latest version of ***scrape*** available on the PyPI using:
```
srepkg scrape
```
The output should look similar to:
```
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

We can then install ***scrapesrepkg***:
```
pip install pip install srepkg_dists/scrapesrepkg-0.11.3-cp310-abi3-linux_x86_64.whl
```
Output:
```
Processing ./srepkg_dists/scrapesrepkg-0.11.3-py3-none-any.whl
Installing collected packages: scrapesrepkg
Successfully installed scrapesrepkg-0.11.3
```
Then we can use the `scrape` command on http://example.com/
```
scrape http://example.com/ -pt
```
Output:
```
Failed to enable cache: No module named 'requests_cache'
Example Domain
Example Domain
This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission.
More information...
```

If we wanted to re-package a specific version (e.g.`0.11.0`) from PyPI we could do this:
```
srepkg scrape -r 0.11.0
```


## **Example #3: Re-package a Distribution Obtained from GitHub**

We can also re-package using a GitHub repo as the original source:
```
srepkg https://github.com/huntrar/scrape
```
Output:
```
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

If we want to re-package a specific commit from the ***scrape*** GitHub repo, we can run:
```
srepkg https://github.com/huntrar/scrape -g 1dfd98bb0a308ef2a45b1e5dd136c38b17c27bc7
```
If we want to re-package a specific release or tag, we would run:
```
srepkg https://github.com/huntrar/scrape -g 0.11.2 
```


