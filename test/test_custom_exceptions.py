import pkginfo
import pytest
from pathlib import Path
import srepkg.error_handling.custom_exceptions as ce


class TestCustomExceptions:

    @pytest.mark.parametrize(
        "exception_name, exception_args",
        [
            (ce.BuildSubprocessError, ("",)),
            (ce.MissingOrigPkgContent, ("dummy_path",)),
            (ce.UnsupportedCompressionType, ("dummy_file",)),
            (ce.MultiplePackagesPresent, ([],)),
            (ce.TargetDistTypeNotSupported, (pkginfo.Develop,)),
            (ce.NoSDistForWheelConstruction, (Path("dummy_path"),)),
            (ce.NoEntryPtsTxtFile, (Path("dummy_path"),)),
            (ce.MultipleEntryPtsTxtFiles, (Path("dummy_path"),)),
            (ce.NoConsoleScriptEntryPoints, (Path("dummy_path"),)),
            (ce.GitCheckoutError, ("dummy_commit_ref",)),
            (ce.GitCloneError, ("dummy_repo",)),
            (ce.UnusableGitCommitRef, ("dummy_commit_ref",)),
            (ce.UnusableVersionArgument, ("dummy_version_arg",)),
            (
                ce.PkgVersionWithCommitRef,
                ("dummy_commit_ref", "dummy_pkg_version"),
            ),
            (ce.WheelUnpackError, ("dummy_wheel",)),
        ],
    )
    def test_exception_init_and_print(
        self, exception_name, exception_args, capsys
    ):
        cur_exception = exception_name(*exception_args)
        print(cur_exception)
        stdout = capsys.readouterr().out
        assert stdout.strip() == cur_exception.__str__().strip()
