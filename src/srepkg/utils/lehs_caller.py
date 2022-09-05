import subprocess
import srepkg.utils.logged_err_detecting_subprocess as lehs

from pathlib import Path


class BuildSubprocessError(Exception):
    def __init__(
            self,
            sub_process: subprocess.CompletedProcess,
            msg="Error occurred when running subprocess intended build a sdist"
                " or wheel."):
        self._sub_process = sub_process
        self._msg = msg

    def __str__(self):
        return f"{str(self._sub_process)} -> {self._msg}"


def run_git_lehs():

    git_sub_proc = lehs.LoggedErrDetectingSubprocess(
        cmd=["git", "blabla"],
        gen_logger_name=__name__,
        std_err_logger_name="std_err",
        std_out_logger_name="std_out",
        default_exception=BuildSubprocessError)

    git_sub_proc.run()


