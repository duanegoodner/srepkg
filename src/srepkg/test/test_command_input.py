from pathlib import Path
import srepkg.command_input as ci
import pytest

arg_1 = str(Path.home() / 'dproj' / 'my_project')
arg_2 = 'custom_package_name'
arg_3 = str(Path.home() / 'srepkg_pkgs_alternate')


def test_zero_args(capsys):
    with pytest.raises(SystemExit):
        ci.get_args([])

    stderr = capsys.readouterr().err
    expected_msg_components = [
        'usage',
        '[-h] [--srepkg_name [SREPKG_NAME]]',
        '[--srepkg_location [SREPKG_LOCATION]]',
        'error: the following arguments are required: '
        'pkg_ref'
    ]
    assert all([component in stderr for component in expected_msg_components])


def test_one_arg():
    args = ci.get_args([arg_1])
    assert args.pkg_ref == \
           str(Path.home() / 'dproj' / 'my_project')
    assert args.srepkg_name is None


def test_valid_custom_name():
    args = ci.get_args([arg_1, '--srepkg_name', arg_2])
    assert args.pkg_ref == str(Path.home() / 'dproj' / 'my_project')
    assert args.srepkg_name == 'custom_package_name'


def test_custom_srepkg_location():
    args = ci.get_args([arg_1, '--srepkg_location', arg_3])
    assert args.pkg_ref == str(Path.home() / 'dproj' / 'my_project')
    assert args.srepkg_location == str(Path.home() / 'srepkg_pkgs_alternate')


def test_too_many_args(capsys):
    with pytest.raises(SystemExit):
        ci.get_args([arg_1, '--srepkg_name', arg_2, 'extra_arg'])
    stderr = capsys.readouterr().err
    expected_msg_components = [
        'usage',
        '[-h] [--srepkg_name [SREPKG_NAME]]',
        '[--srepkg_location [SREPKG_LOCATION]]',
        'error: unrecognized arguments:',
        'extra_arg'
    ]
    assert all([component in stderr for component in expected_msg_components])
