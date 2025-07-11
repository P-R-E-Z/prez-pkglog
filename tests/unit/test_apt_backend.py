"""Unit tests for the APT backend"""

import subprocess
from unittest.mock import patch, MagicMock

from src.prez_pkglog.backends.linux.apt import AptBackend


class TestAptBackend:
    """Test the AptBackend class."""

    def test_is_available_with_dpkg(self):
        """Test availability detection when dpkg is available."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/dpkg"
            assert AptBackend.is_available() is True

    def test_is_available_without_dpkg(self):
        """Test availability detection when dpkg is not available."""
        with patch("shutil.which") as mock_which:
            mock_which.return_value = None
            assert AptBackend.is_available() is False

    def test_initialization_with_dpkg_available(self):
        """Test AptBackend initialization when dpkg is available."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()
            assert backend.name == "apt"
            assert backend.enabled is True

    def test_initialization_without_dpkg_available(self):
        """Test AptBackend initialization when dpkg is not available."""
        with patch("shutil.which", return_value=None):
            backend = AptBackend()
            assert backend.name == "apt"
            assert backend.enabled is False

    def test_initialization_with_config(self):
        """Test AptBackend initialization with config."""
        mock_config = MagicMock()
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend(config=mock_config)
            assert backend.config is mock_config

    def test_get_installed_packages_success(self):
        """Test successful package listing."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            mock_output = "package1\t1.0.0-1\tamd64\npackage2\t2.0.0-1\ti386\n"
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout=mock_output,
                    returncode=0,
                )

                packages = backend.get_installed_packages()

                assert len(packages) == 2
                assert "package1" in packages
                assert "package2" in packages
                
                # Check package1 details
                pkg1 = packages["package1"]
                assert pkg1.name == "package1"
                assert pkg1.version == "1.0.0-1"
                assert pkg1.architecture == "amd64"
                assert pkg1.installed is True
                
                # Check package2 details
                pkg2 = packages["package2"]
                assert pkg2.name == "package2"
                assert pkg2.version == "2.0.0-1"
                assert pkg2.architecture == "i386"
                assert pkg2.installed is True

    def test_get_installed_packages_with_complex_output(self):
        """Test package listing with complex package names and versions."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            mock_output = (
                "python3-pip\t20.0.2-5ubuntu1.9\tall\n"
                "libc6-dev\t2.31-0ubuntu9.9\tamd64\n"
                "gcc-9-base\t9.4.0-1ubuntu1~20.04.1\tamd64\n"
            )
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout=mock_output,
                    returncode=0,
                )

                packages = backend.get_installed_packages()

                assert len(packages) == 3
                assert "python3-pip" in packages
                assert "libc6-dev" in packages
                assert "gcc-9-base" in packages
                
                # Check complex version handling
                pip_pkg = packages["python3-pip"]
                assert pip_pkg.version == "20.0.2-5ubuntu1.9"
                assert pip_pkg.architecture == "all"

    def test_get_installed_packages_empty_output(self):
        """Test package listing with empty output."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="",
                    returncode=0,
                )

                packages = backend.get_installed_packages()
                assert packages == {}

    def test_get_installed_packages_malformed_output(self):
        """Test package listing with malformed output."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            # Output with missing fields
            mock_output = "package1\t1.0.0\npackage2\npackage3\t2.0.0\tamd64\n"
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout=mock_output,
                    returncode=0,
                )

                packages = backend.get_installed_packages()
                
                # Should only include well-formed entries
                assert "package3" in packages
                assert len(packages) == 1

    def test_get_installed_packages_subprocess_error(self):
        """Test package listing when subprocess fails."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.SubprocessError("Command failed")

                packages = backend.get_installed_packages()

                assert packages == {}
                mock_run.assert_called_once()

    def test_get_installed_packages_timeout_error(self):
        """Test package listing when subprocess times out."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired(
                    cmd=["dpkg-query"], timeout=30
                )

                packages = backend.get_installed_packages()
                assert packages == {}

    def test_get_installed_packages_file_not_found(self):
        """Test package listing when dpkg-query is not found."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError("dpkg-query not found")

                packages = backend.get_installed_packages()
                assert packages == {}

    def test_get_installed_packages_when_disabled(self):
        """Test package listing when backend is disabled."""
        with patch("shutil.which", return_value=None):
            backend = AptBackend()
            assert backend.enabled is False

            packages = backend.get_installed_packages()
            assert packages == {}

    def test_register_transaction_not_supported(self):
        """Test that register_transaction is not supported."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("src.prez_pkglog.backends.linux.apt.logger") as mock_logger:
                result = backend.register_transaction(None)

                assert result is False
                mock_logger.warning.assert_called_once()
                warning_message = mock_logger.warning.call_args[0][0]
                assert "not supported" in warning_message
                assert "apt backend" in warning_message

    def test_register_transaction_with_mock_transaction(self):
        """Test register_transaction with a mock transaction object."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            mock_transaction = MagicMock()
            mock_transaction.install_set = ["package1", "package2"]
            mock_transaction.remove_set = ["package3"]

            with patch("src.prez_pkglog.backends.linux.apt.logger") as mock_logger:
                result = backend.register_transaction(mock_transaction)

                assert result is False
                mock_logger.warning.assert_called_once()

    def test_backend_name_attribute(self):
        """Test that AptBackend has correct name attribute."""
        assert AptBackend.name == "apt"

    def test_backend_inheritance(self):
        """Test that AptBackend inherits from PackageBackend."""
        from src.prez_pkglog.backends.base import PackageBackend
        
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()
            assert isinstance(backend, PackageBackend)

    def test_dpkg_query_command_format(self):
        """Test that dpkg-query is called with correct arguments."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="package1\t1.0.0\tamd64\n",
                    returncode=0,
                )

                backend.get_installed_packages()

                # Verify the command was called correctly
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                
                assert call_args[0] == "dpkg-query"
                assert "-W" in call_args
                assert "-f=${Package}\\t${Version}\\t${Architecture}\\n" in call_args

    def test_dpkg_query_timeout_setting(self):
        """Test that dpkg-query is called with appropriate timeout."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="package1\t1.0.0\tamd64\n",
                    returncode=0,
                )

                backend.get_installed_packages()

                # Verify timeout is set
                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["timeout"] == 30

    def test_dpkg_query_subprocess_options(self):
        """Test that dpkg-query subprocess is configured correctly."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="package1\t1.0.0\tamd64\n",
                    returncode=0,
                )

                backend.get_installed_packages()

                # Verify subprocess options
                mock_run.assert_called_once()
                call_kwargs = mock_run.call_args[1]
                assert call_kwargs["capture_output"] is True
                assert call_kwargs["text"] is True
                assert call_kwargs["check"] is True

    def test_error_logging_on_failure(self):
        """Test that errors are logged when package listing fails."""
        with patch("shutil.which", return_value="/usr/bin/dpkg"):
            backend = AptBackend()

            with (
                patch("subprocess.run") as mock_run,
                patch("src.prez_pkglog.backends.linux.apt.logger") as mock_logger,
            ):
                mock_run.side_effect = OSError("System error")

                packages = backend.get_installed_packages()

                assert packages == {}
                mock_logger.error.assert_called_once()
                error_message = mock_logger.error.call_args[0][0]
                assert "Failed to get installed packages" in error_message
                assert "dpkg-query" in error_message 