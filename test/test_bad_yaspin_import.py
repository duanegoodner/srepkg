import unittest
from unittest.mock import patch
import builtins
import sys

class TestStatusDisplayFallback(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Backup the original import function before patching"""
        cls.original_import = builtins.__import__

    @staticmethod
    def fake_import(name, *args, **kwargs):
        """Force an ImportError when trying to import yaspin_updater"""
        if "inner_pkg_installer.yaspin_updater" in name or "yaspin_updater" in name:
            raise ModuleNotFoundError("Simulated ImportError")
        return TestStatusDisplayFallback.original_import(name, *args, **kwargs)  # Use the real import

    @patch("builtins.__import__")  # Patching Python’s import system
    def test_status_display_fallback(self, mock_import):
        # Ensure the mock import function calls the correct static method
        mock_import.side_effect = TestStatusDisplayFallback.fake_import

        # Remove module cache to force reimport
        sys.modules.pop("inner_pkg_installer.inner_pkg_installer", None)

        # Import the target module, triggering the except block
        import inner_pkg_installer.inner_pkg_installer
