import logging
import os
import sys
import tempfile
from pathlib import Path
import inner_pkg_installer.inner_pkg_installer as ipi
import srepkg.logging_initializer as lgr


def test_ipi_logging():
    temp_logging_dir = tempfile.TemporaryDirectory()
    logger_initializer = lgr.LoggingInitializer(
        logfile_dir=Path(temp_logging_dir.name)
    )
    logger_initializer.setup()

    ipi_logging = ipi.IPILogging()
    ipi_logging.confirm_setup()


def test_add_missing_loggers():
    temp_logging_dir = tempfile.TemporaryDirectory()
    logger_initializer = lgr.LoggingInitializer(
        logfile_dir=Path(temp_logging_dir.name)
    )
    logger_initializer.setup()

    custom_logger_names = [
        logging.getLogger(ref).name for ref in logging.root.manager.loggerDict
    ]

    console_logger_info = {
        "std_err": (logging.DEBUG, sys.stderr),
        "std_out": (logging.DEBUG, sys.stdout),
        "dev_null": (logging.DEBUG, os.devnull),
    }

    ipi.add_missing_loggers(
        custom_logger_names=custom_logger_names,
        console_logger_info=console_logger_info,
    )


