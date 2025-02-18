import logging
import os
import sys
import tempfile
from pathlib import Path
from test.shared_fixtures import sample_pkgs
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
    assert logging.getLogger("std_err") is not None
    assert logging.getLogger("std_out") is not None



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

    assert logging.getLogger("dev_null") is not None


def test_py_version():
    py_version = ipi.PyVersion(version_str="3.11.2")
    assert py_version.major == 3
    assert py_version.minor == 11
    assert py_version.micro == 2


def test_custom_venv_builder():
    custom_venv_builder = ipi.CustomVenvBuilder()
    version_info = custom_venv_builder.version_info
    assert version_info == sys.version_info
    site_packages = custom_venv_builder.site_pkgs
    assert site_packages is None


def test_inner_pkg_cfg_reader(sample_pkgs):
    cfg_reader = ipi.InnerPkgCfgReader(
        inner_pkg_cfg=Path(sample_pkgs.innder_pkg_testproj_setup_cfg)
    )
    srepkg_name = cfg_reader.srepkg_name
    assert srepkg_name == "testprojsrepkg"
    dist_dir = cfg_reader.dist_dir
    assert dist_dir == "test_dist_dir"
    sdist_src = cfg_reader.sdist_src
    assert sdist_src == "test_sdist_src"
