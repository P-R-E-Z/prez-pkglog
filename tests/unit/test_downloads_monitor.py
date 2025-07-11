"""Unit tests for the downloads monitor module"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.prez_pkglog.monitors.downloads import DownloadsMonitor, DownloadsEventHandler


class TestDownloadsMonitor:
    """Test the DownloadsMonitor class."""

    def test_init(self):
        """Test DownloadsMonitor initialization."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        assert monitor.pkg_logger == mock_logger
        assert monitor.downloads_dir == Path.home() / "Downloads"
        assert monitor.observer is None

    def test_init_with_logger(self):
        """Test DownloadsMonitor initialization with logger."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        assert monitor.pkg_logger == mock_logger

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", False)
    def test_start_watchdog_not_available(self):
        """Test start when watchdog is not available."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        with patch("src.prez_pkglog.monitors.downloads.logger") as mock_logger_module:
            monitor.start()

            mock_logger_module.warning.assert_called_with(
                "watchdog library not found. Download monitoring disabled."
            )

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_start_downloads_dir_not_exists(self):
        """Test start when Downloads directory doesn't exist."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("src.prez_pkglog.monitors.downloads.logger") as mock_logger_module,
        ):
            monitor.start()

            mock_logger_module.warning.assert_called_with(
                f"Downloads directory {monitor.downloads_dir} not found. "
                "Monitoring disabled."
            )

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_start_success(self):
        """Test successful start of monitoring."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("src.prez_pkglog.monitors.downloads.Observer") as mock_observer_class,
            patch("src.prez_pkglog.monitors.downloads.logger") as mock_logger_module,
        ):
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            monitor.start()

            mock_observer.schedule.assert_called_once()
            mock_observer.start.assert_called_once()
            mock_logger_module.info.assert_called_with(
                f"Monitoring downloads folder: {monitor.downloads_dir}"
            )

    def test_stop_no_observer(self):
        """Test stop when no observer exists."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        # Should not raise any exception
        monitor.stop()

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_stop_with_observer(self):
        """Test stop with observer."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "~/Downloads"
        
        monitor = DownloadsMonitor(mock_logger)

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("src.prez_pkglog.monitors.downloads.Observer") as mock_observer_class,
        ):
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            monitor.start()
            monitor.stop()

            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()


class TestDownloadsEventHandler:
    """Test the DownloadsEventHandler class."""

    def test_init(self):
        """Test DownloadsEventHandler initialization."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        assert handler.pkg_logger == mock_logger

    def test_on_created_file(self):
        """Test on_created with a file."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/home/user/Downloads/test.rpm"

        with patch("pathlib.Path") as mock_path_class:
            mock_path = MagicMock()
            mock_path.suffix.lower.return_value = ".rpm"
            mock_path.name = "test.rpm"
            mock_path.stat.return_value.st_size = 1024
            mock_path.__str__ = MagicMock(return_value="/home/user/Downloads/test.rpm")
            mock_path_class.return_value = mock_path

            # Mock the actual Path creation inside the handler
            with patch(
                "src.prez_pkglog.monitors.downloads.Path", return_value=mock_path
            ):
                handler.on_created(mock_event)

            mock_logger.log_package.assert_called_once_with(
                "test.rpm",
                "download",
                "install",
                metadata={
                    "file_path": "/home/user/Downloads/test.rpm",
                    "file_size": 1024,
                    "file_type": ".rpm",
                },
            )

    def test_on_created_directory(self):
        """Test on_created with a directory (should be ignored)."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = "/home/user/Downloads/new_folder"

        handler.on_created(mock_event)

        # Should not call log_package for directories
        mock_logger.log_package.assert_not_called()

    def test_on_created_non_package_file(self):
        """Test on_created with a non-package file."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/home/user/Downloads/document.txt"

        with patch("pathlib.Path") as mock_path_class:
            mock_path = MagicMock()
            mock_path.suffix.lower.return_value = ".txt"
            mock_path_class.return_value = mock_path

            # Mock the actual Path creation inside the handler
            with patch(
                "src.prez_pkglog.monitors.downloads.Path", return_value=mock_path
            ):
                handler.on_created(mock_event)

            # Should not call log_package for non-package files
            mock_logger.log_package.assert_not_called()

    def test_on_created_package_files(self):
        """Test on_created with various package file types."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        package_extensions = [".rpm", ".deb", ".pkg", ".exe", ".msi", ".dmg"]

        for ext in package_extensions:
            mock_logger.log_package.reset_mock()

            # Mock event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = f"/home/user/Downloads/test{ext}"

            with patch("pathlib.Path") as mock_path_class:
                mock_path = MagicMock()
                mock_path.suffix.lower.return_value = ext
                mock_path.name = f"test{ext}"
                mock_path.stat.return_value.st_size = 1024
                mock_path.__str__ = MagicMock(
                    return_value=f"/home/user/Downloads/test{ext}"
                )
                mock_path_class.return_value = mock_path

                # Mock the actual Path creation inside the handler
                with patch(
                    "src.prez_pkglog.monitors.downloads.Path", return_value=mock_path
                ):
                    handler.on_created(mock_event)

                mock_logger.log_package.assert_called_once_with(
                    f"test{ext}",
                    "download",
                    "install",
                    metadata={
                        "file_path": f"/home/user/Downloads/test{ext}",
                        "file_size": 1024,
                        "file_type": ext,
                    },
                )

    def test_on_created_no_logger(self):
        """Test on_created when logger is None."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)
        # Test with logger set to None by mocking the attribute access
        with patch.object(handler, 'pkg_logger', None):
            # Mock event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = "/home/user/Downloads/test.rpm"

            with patch("pathlib.Path") as mock_path_class:
                mock_path = MagicMock()
                mock_path.suffix.lower.return_value = ".rpm"
                mock_path.stem = "test"
                mock_path.stat.return_value.st_size = 1024
                mock_path_class.return_value = mock_path

                # Mock the actual Path creation inside the handler
                with patch(
                    "src.prez_pkglog.monitors.downloads.Path", return_value=mock_path
                ):
                    # Should not raise any exception
                    handler.on_created(mock_event)

    def test_on_created_stat_error(self):
        """Test on_created when stat() fails."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        
        handler = DownloadsEventHandler(mock_logger)

        # Mock event
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/home/user/Downloads/test.rpm"

        with patch("pathlib.Path") as mock_path_class:
            mock_path = MagicMock()
            mock_path.suffix.lower.return_value = ".rpm"
            mock_path.name = "test.rpm"
            mock_path.stat.side_effect = OSError("Permission denied")
            mock_path.__str__ = MagicMock(return_value="/home/user/Downloads/test.rpm")
            mock_path_class.return_value = mock_path

            # Mock the actual Path creation inside the handler
            with patch(
                "src.prez_pkglog.monitors.downloads.Path", return_value=mock_path
            ), patch("src.prez_pkglog.monitors.downloads.logger") as mock_logger_module:
                # Should not raise OSError - the current implementation handles stat errors
                handler.on_created(mock_event)
                
                # Should log a warning about the stat error
                mock_logger_module.warning.assert_called_once()
                
                # Should still call log_package with file_size=0
                mock_logger.log_package.assert_called_once_with(
                    "test.rpm",
                    "download", 
                    "install",
                    metadata={
                        "file_path": "/home/user/Downloads/test.rpm",
                        "file_size": 0,
                        "file_type": ".rpm",
                    },
                )
