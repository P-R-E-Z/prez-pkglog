"""Unit tests for the DNF backend"""

import subprocess
from unittest.mock import patch, MagicMock

from src.prez_pkglog.backends.dnf import DnfBackend


class TestDnfBackend:
    """Test the DnfBackend class."""

    def test_is_available_with_dnf(self):
        """Test availability detection when DNF is available."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/dnf"
            assert DnfBackend.is_available() is True

    def test_is_available_without_dnf(self):
        """Test availability detection when DNF is not available."""
        with (
            patch("shutil.which") as mock_which,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_which.return_value = None
            mock_exists.return_value = False
            assert DnfBackend.is_available() is False

    def test_get_installed_packages_success(self):
        """Test successful package listing."""
        backend = DnfBackend()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="package1 1.0.0-1.fc42 x86_64\npackage2 2.0.0-1.fc42 x86_64",
                returncode=0,
            )

            packages = backend.get_installed_packages()

            assert len(packages) == 2
            assert "package1" in packages
            assert "package2" in packages
            assert packages["package1"].name == "package1"
            assert packages["package1"].version == "1.0.0"
            assert packages["package1"].architecture == "x86_64"

    def test_get_installed_packages_failure(self):
        """Test package listing when subprocess fails."""
        backend = DnfBackend()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.SubprocessError("Command failed")

            packages = backend.get_installed_packages()

            assert packages == {}
            # Verify the exception was caught and logged
            mock_run.assert_called_once()

    def test_register_transaction_success(self):
        """Test successful transaction registration."""
        backend = DnfBackend()
        # Create a mock logger with the expected method
        mock_logger = MagicMock()
        mock_logger.log_package = MagicMock()
        backend.logger = mock_logger

        # Mock transaction object
        transaction = MagicMock()
        transaction.install_set = [MagicMock(name="package1")]
        transaction.remove_set = [MagicMock(name="package2")]

        result = backend.register_transaction(transaction)

        assert result is True
        assert mock_logger.log_package.call_count == 2

    def test_register_transaction_no_logger(self):
        """Test transaction registration without logger."""
        backend = DnfBackend()
        backend.logger = None

        # Mock transaction object
        transaction = MagicMock()
        transaction.install_set = [MagicMock(name="package1")]
        transaction.remove_set = []

        result = backend.register_transaction(transaction)

        assert result is True  # Should not fail, just not log
