import pytest
import srepkg.command_input as ci
import srepkg.error_handling.custom_exceptions as ce


class TestCommandInput:

    local_src_pkg_ref = "./local_pkg_ref"
    user_srepkg_name = "user_srepkg_name"
    user_construction_dir = "user_construction_dir"
    user_dist_out_dir = "user_dist_out_dir"
    extra_arg = "extra_arg"

    def test_zero_args(self, capsys):
        with pytest.raises(SystemExit):
            srepkg_args = ci.SrepkgCommandLine().get_args([])

    def test_one_arg(self):
        args = ci.SrepkgCommandLine().get_args([self.local_src_pkg_ref])
        assert args.orig_pkg_ref == self.local_src_pkg_ref
        assert args.srepkg_name is None

    def test_valid_custom_name(self):
        args = ci.SrepkgCommandLine().get_args(
            [self.local_src_pkg_ref, "-n", self.user_srepkg_name]
        )
        assert args.orig_pkg_ref == self.local_src_pkg_ref
        assert args.srepkg_name == self.user_srepkg_name

    def test_custom_construction_dir(self):
        args = ci.SrepkgCommandLine().get_args(
            [self.local_src_pkg_ref, "-c", self.user_construction_dir]
        )
        assert args.orig_pkg_ref == self.local_src_pkg_ref
        assert args.construction_dir == self.user_construction_dir

    def test_custom_dist_out_dir(self):
        args = ci.SrepkgCommandLine().get_args(
            [self.local_src_pkg_ref, "-d", self.user_dist_out_dir]
        )
        assert args.orig_pkg_ref == self.local_src_pkg_ref
        assert args.dist_out_dir == self.user_dist_out_dir

    def test_too_many_args(self, capsys):
        with pytest.raises(SystemExit):
            ci.SrepkgCommandLine().get_args(
                [
                    self.local_src_pkg_ref,
                    "-n",
                    self.user_srepkg_name,
                    self.extra_arg,
                ]
            )

    def test_pypi_version_and_git_ref(self):
        with pytest.raises(ce.PkgVersionWithCommitRef):
            ci.SrepkgCommandLine().get_args(
                [
                    self.local_src_pkg_ref,
                    "-g",
                    "dummy_git_ref",
                    "-r",
                    "dummy_pypi_version",
                ]
            )
