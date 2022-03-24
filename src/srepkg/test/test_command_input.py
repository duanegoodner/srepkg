from pathlib import Path
import src.srepkg.io.command_input as ci

arg_1 = str(Path.home() / 'dproj' / 'my_project')
arg_2 = 'custom_package_name'


def test_single_arg():
    args = ci.get_args([arg_1])
    assert args.orig_pkg_setup_dir == arg_1
    assert args.srepkg_name is None


def test_two_args():
    args = ci.get_args([arg_1, arg_2])
    assert args.orig_pkg_setup_dir == arg_1
    assert args.srepkg_name == arg_2