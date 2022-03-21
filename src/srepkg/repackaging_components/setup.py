"""
Minimal setup.py file. Metadata and setup parameters defined in setup.cfg, but
keeping call to setuptools.setup() might(?) help compatibility with legacy
builds.
"""
import pip
import setuptools


def check_pip_version():

    parsed_pip_version = pip.__version__.strip().split('.')

    if int(parsed_pip_version[0]) < 22 and int(parsed_pip_version[1]) < 3:

        print('\n============================================================')
        print('ERROR:')
        print('pip version 21.3 or higher is required to install this package')
        print(f'You are using version {pip.__version__}.\n')
        print('RECOMMENDED SOLUTION:')
        print('Upgrade pip to version 21.3 or higher. Then re-try installing.')
        print('See https://pip.pypa.io/en/stable/installation/#upgrading-pip')
        print('============================================================\n')
        exit(1)


check_pip_version()
setuptools.setup()

