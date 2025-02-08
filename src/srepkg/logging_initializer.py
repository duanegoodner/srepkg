"""
Contqains LoggingInitialzer class
"""

import logging
import sys
import tempfile
from datetime import datetime
from pathlib import Path


class LoggingInitializer:
    """
    Applies global logging settings.
    """
    def __init__(self, logfile_dir: Path = None):
        """

        Args:
            logfile_dir: path where logfile is saved.
        """
        if logfile_dir is None:
            self._logfile_dir_temp_obj = tempfile.TemporaryDirectory()
            logfile_dir = Path(self._logfile_dir_temp_obj.name)
        else:
            self._logfile_dir_temp_obj = None
        self._logfile_dir = logfile_dir
        self._log_filename = (
            f"srepkg_log_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S_%f')}.log"
        )

    @staticmethod
    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.getLogger("std_err").critical(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    def setup(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
            filename=f"{str(self._logfile_dir)}/{self._log_filename}",
            filemode="w",
        )

        console_log_handler_info = {
            "std_err": (logging.DEBUG, sys.stderr),
            "std_out": (logging.DEBUG, sys.stdout),
        }

        for handler_name, handler_info in console_log_handler_info.items():
            logger = logging.getLogger(handler_name)
            handler = logging.StreamHandler(stream=handler_info[1])
            handler.setLevel(level=handler_info[0])
            logger.addHandler(handler)

        sys.excepthook = self.log_unhandled_exception
