import inner_pkg_installer.inner_pkg_installer as ipi
import logging
import srepkg.logging_initializer as lgr
import sys
import tempfile
from pathlib import Path
from test.shared_fixtures import sample_pkgs


def test_ipi_logging():
    temp_logging_dir = tempfile.TemporaryDirectory()
    logger_initializer = lgr.LoggingInitializer(
        logfile_dir=Path(temp_logging_dir.name)
    )
    logger_initializer.setup()

    ipi_logging = ipi.IPILogging()
    ipi_logging.confirm_setup()


def test_add_logger_streams():
    temp_logging_dir = tempfile.TemporaryDirectory()
    logger_initializer = lgr.LoggingInitializer(
        logfile_dir=Path(temp_logging_dir.name)
    )
    logger_initializer.setup()

    custom_logger_names = [
        logging.getLogger(ref).name for ref in logging.root.manager.loggerDict
    ]

    fake_logger_info = {
        "std_err": (logging.DEBUG, sys.stderr),
        # "std_out": (logging.DEBUG, sys.stdout),
        "mock_name": (logging.DEBUG, sys.stdout),
    }

    ipi.add_logger_streams(
        console_logger_info=fake_logger_info,
        custom_logger_names=custom_logger_names,
    )


def test_inner_pkg_cfg_reader(sample_pkgs):
    inner_pkg_cfg_reader = ipi.InnerPkgCfgReader(
        inner_pkg_cfg=Path(sample_pkgs.test_inner_pkg_cfg)
    )
    srepkg_name = inner_pkg_cfg_reader.srepkg_name
    dist_dir = inner_pkg_cfg_reader.dist_dir
    sdist_src = inner_pkg_cfg_reader.sdist_src

