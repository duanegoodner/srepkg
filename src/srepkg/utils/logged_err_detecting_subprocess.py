import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Callable


class SubprocessError(Exception):
    def __init__(
        self,
        sub_process: subprocess.CompletedProcess,
        msg="Error occurred when running subprocess",
    ):
        self._sub_process = sub_process
        self._msg = msg

    def __str__(self):
        return f"{str(self._sub_process)} -> {self._msg}"


class LoggedErrDetectingSubprocess:

    def __init__(
        self,
        cmd: List[str],
        gen_logger_name: str,
        std_out_logger_name: str,
        std_err_logger_name: str,
        cwd: Path = Path.cwd(),
        default_exception: Callable[
            [subprocess.CompletedProcess], Exception
        ] = SubprocessError,
        exception_table: Dict[
            int, Callable[[subprocess.CompletedProcess], Exception]
        ] = None,
    ):
        self._cmd = cmd
        self._gen_logger_name = gen_logger_name
        self._std_out_logger_name = std_out_logger_name
        self._std_out_buffer = tempfile.NamedTemporaryFile()
        self._std_err_logger_name = std_err_logger_name
        self._std_err_buffer = tempfile.NamedTemporaryFile()
        if exception_table is None:
            exception_table = {}
        self._cwd = cwd
        self._default_exception = default_exception
        self._exception_table = exception_table

    def run(self):
        sub_proc = subprocess.run(
            self._cmd,
            cwd=self._cwd,
            stdout=self._std_out_buffer,
            stderr=self._std_err_buffer,
            universal_newlines=True,
        )

        self._std_out_buffer.seek(0)
        for line in self._std_out_buffer:
            logging.getLogger(self._gen_logger_name).info(
                line.decode("utf-8").strip()
            )

        self._std_err_buffer.seek(0)
        if sub_proc.returncode == 0:
            for line in self._std_err_buffer:
                logging.getLogger(self._gen_logger_name).info(
                    line.decode("utf-8").strip()
                )
        else:
            for line in self._std_err_buffer:
                logging.getLogger(
                    f"{self._std_err_logger_name}.{self._gen_logger_name}"
                ).error(line.decode("utf-8").strip())

            if (
                self._exception_table
                and sub_proc.returncode in self._exception_table
            ):
                raise self._exception_table[sub_proc.returncode](sub_proc)
            else:
                raise self._default_exception(sub_proc)
