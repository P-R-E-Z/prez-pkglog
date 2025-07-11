"""Unit tests for the DNF backend"""

import subprocess
from unittest.mock import patch, MagicMock

from src.prez_pkglog.backends.linux.dnf import DnfBackend


class TestDnfBackend:
    """Test the DnfBackend class."""

    def test_is_available_with_dnf(self):
        """Test availability detection when DNF is available."""
        with (
            patch("shutil.which") as mock_which,
            patch("src.prez_pkglog.backends.linux.dnf.dnf", MagicMock()),
        ):
            mock_which.return_value = "/usr/bin/dnf"
            assert DnfBackend.is_available() is True

    def test_is_available_without_dnf(self):
        """Test availability detection when DNF is not available."""
        with (
            patch("shutil.which") as mock_which,
            patch("pathlib.Path.exists") as mock_exists,
            patch("src.prez_pkglog.backends.linux.dnf.dnf", None),
        ):
            mock_which.return_value = None
            mock_exists.return_value = False
            assert DnfBackend.is_available() is False

    def test_get_installed_packages_success(self):
        """Test successful package listing."""
        mock_dnf = MagicMock()
        mock_base = MagicMock()
        mock_sack = MagicMock()
        mock_query = MagicMock()
        
        # Mock package objects
        mock_pkg1 = MagicMock()
        mock_pkg1.name = "package1"
        mock_pkg1.version = "1.0.0"
        mock_pkg1.arch = "x86_64"
        mock_pkg1.reponame = "fedora"
        
        mock_pkg2 = MagicMock()
        mock_pkg2.name = "package2"
        mock_pkg2.version = "2.0.0"
        mock_pkg2.arch = "x86_64"
        mock_pkg2.reponame = "fedora"
        
        mock_query.return_value = [mock_pkg1, mock_pkg2]
        mock_sack.query.return_value.installed.return_value = [mock_pkg1, mock_pkg2]
        mock_base.sack = mock_sack
        mock_base.fill_sack = MagicMock()
        mock_dnf.Base.return_value.__enter__ = MagicMock(return_value=mock_base)
        mock_dnf.Base.return_value.__exit__ = MagicMock(return_value=None)

        with (
            patch("src.prez_pkglog.backends.linux.dnf.dnf", mock_dnf),
            patch("shutil.which", return_value="/usr/bin/dnf"),
        ):
            backend = DnfBackend()
            packages = backend.get_installed_packages()

            assert len(packages) == 2
            assert "package1" in packages
            assert "package2" in packages
            assert packages["package1"].name == "package1"
            assert packages["package1"].version == "1.0.0"
            assert packages["package1"].architecture == "x86_64"

    def test_get_installed_packages_failure(self):
        """Test package listing when dnf API fails."""
        mock_dnf = MagicMock()
        mock_base = MagicMock()
        mock_base.fill_sack.side_effect = Exception("DNF API error")
        mock_dnf.Base.return_value.__enter__ = MagicMock(return_value=mock_base)
        mock_dnf.Base.return_value.__exit__ = MagicMock(return_value=None)

        with (
            patch("src.prez_pkglog.backends.linux.dnf.dnf", mock_dnf),
            patch("shutil.which", return_value="/usr/bin/dnf"),
        ):
            backend = DnfBackend()
            packages = backend.get_installed_packages()

            assert packages == {}
            # Verify the exception was caught and logged
            mock_base.fill_sack.assert_called_once()

    def test_register_transaction_success(self):
        """Test successful transaction registration."""
        mock_dnf = MagicMock()
        
        with (
            patch("src.prez_pkglog.backends.linux.dnf.dnf", mock_dnf),
            patch("shutil.which", return_value="/usr/bin/dnf"),
        ):
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
        mock_dnf = MagicMock()
        
        with (
            patch("src.prez_pkglog.backends.linux.dnf.dnf", mock_dnf),
            patch("shutil.which", return_value="/usr/bin/dnf"),
        ):
            backend = DnfBackend()
            backend.logger = None

            # Mock transaction object
            transaction = MagicMock()
            transaction.install_set = [MagicMock(name="package1")]
            transaction.remove_set = []

            result = backend.register_transaction(transaction)

            assert result is True  # Should not fail, just not log
