import pkginfo
import pytest
from pathlib import Path
import srepkg.error_handling.custom_exceptions as ce


class TestCustomExceptions:

    @pytest.mark.parametrize("exception_name, exception_arg", [
        (ce.MissingOrigPkgContent, "dummy_path"),
        (ce.UnsupportedCompressionType, "dummy_file"),
        (ce.MultiplePackagesPresent, []),
        (ce.TargetDistTypeNotSupported, pkginfo.Develop),
        (ce.NoSDistForWheelConstruction, Path("dummy_path")),
        (ce.NoEntryPtsTxtFile, Path("dummy_path")),
        (ce.MultipleEntryPtsTxtFiles, Path("dummy_path")),
        (ce.NoConsoleScriptEntryPoints, Path("dummy_path")),
        (ce.GitCheckoutError, "dummy_commit_ref"),
        (ce.UnusableGitCommitRef, "dummy_commit_ref")
    ])
    def test_exception_init_and_print(self, exception_name, exception_arg,
                                      capsys):
        cur_exception = exception_name(exception_arg)
        print(cur_exception)
        stdout = capsys.readouterr().out
        assert stdout.strip() == cur_exception.__str__().strip()



