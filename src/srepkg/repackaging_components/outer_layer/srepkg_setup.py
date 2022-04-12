"""
Minimal setup.py file. Metadata and setup parameters defined in setup.cfg, but
keeping call to setuptools.setup() might(?) help compatibility with legacy
builds.
"""
import pip
import setuptools


version_error_message =\
    f'\n===============================================================\n' \
    f'ERROR:\n' \
    f'pip version 21.3 or higher is required to install this package\n' \
    f'You are using version {pip.__version__}.\n' \
    f'RECOMMENDED SOLUTION:\n' \
    f'Upgrade pip to version 21.3 or higher. Then re-try installing.\n' \
    f'See https://pip.pypa.io/en/stable/installation/#upgrading-pip\n' \
    f'===============================================================\n'


def check_pip_version():

    parsed_pip_version = pip.__version__.strip().split('.')

    if int(parsed_pip_version[0]) < 22 and int(parsed_pip_version[1]) < 3:
        print(version_error_message)
        exit(1)


check_pip_version()
setuptools.setup()

