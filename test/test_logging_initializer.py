import logging
import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, ANY
from srepkg.logging_initializer import LoggingInitializer


@pytest.fixture
def logging_initializer():
    """Fixture to initialize LoggingInitializer."""
    return LoggingInitializer()


def test_log_unhandled_exception_keyboard_interrupt(logging_initializer):
    """Test that KeyboardInterrupt is passed to sys.__excepthook__."""
    with patch("sys.__excepthook__") as mock_excepthook:
        logging_initializer.log_unhandled_exception(KeyboardInterrupt, KeyboardInterrupt(), None)
        mock_excepthook.assert_called_once_with(KeyboardInterrupt, ANY, None)


def test_log_unhandled_exception_logging(logging_initializer, caplog):
    """Test that a non-keyboard exception is logged as critical."""
    with caplog.at_level(logging.CRITICAL, logger="std_err"):
        test_exception = ValueError("Test error")
        logging_initializer.log_unhandled_exception(ValueError, test_exception, None)

    assert "Uncaught exception" in caplog.text
    assert "Test error" in caplog.text

def test_non_default_init():
    logfile_dir = Path(tempfile.TemporaryDirectory().name)
    logging_initializer = LoggingInitializer(logfile_dir=logfile_dir)
    assert logging_initializer._logfile_dir == logfile_dir
