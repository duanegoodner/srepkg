# https://stackoverflow.com/a/24176022/263998

from contextlib import contextmanager
import os


@contextmanager
def dir_change_to(new_dir):
    prev_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)
