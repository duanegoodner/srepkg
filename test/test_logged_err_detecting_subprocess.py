import pytest
import subprocess
import srepkg.error_handling.custom_exceptions as ce
import srepkg.logging_initializer as lgr
import srepkg.utils.logged_err_detecting_subprocess as leds
from test.shared_fixtures import app_logger
import srepkg.dist_builder as db


class SubprocessException(Exception):
    def __init__(
        self,
        sub_process: subprocess.CompletedProcess,
        msg="Raised test exception requiring CompletedProcess as arg",
    ):
        self._sub_process = sub_process
        self._msg = msg

    def __str__(self):
        return f"{str(self._sub_process)} -> {self._msg}"


class TestLoggedErrorDetectingSubprocess:

    @pytest.mark.parametrize(
        "command, exception",
        [
            (["not_a_command"], FileNotFoundError),
            (["git", "asdfas"], ce.BuildSubprocessError),
        ],
    )
    def test_bad_command(self, command, exception, app_logger):
        bad_sub_proc = leds.LoggedErrDetectingSubprocess(
            cmd=command,
            gen_logger_name=__name__,
            std_out_logger_name="std_out",
            std_err_logger_name="std_err",
            default_exception=exception,
        )

        with pytest.raises(exception):
            bad_sub_proc.run()
