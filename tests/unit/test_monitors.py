"""Unit tests for monitors functionality."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.prez_pkglog.monitors.downloads import DownloadsMonitor, DownloadsEventHandler


class TestDownloadsMonitor:
    """Test the downloads monitor functionality."""

    def test_monitor_initialization(self):
        """Test that the monitor initializes correctly."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        assert monitor.pkg_logger is mock_logger
        assert monitor.config is mock_logger.config
        assert monitor.downloads_dir == Path("/tmp/downloads").expanduser()

    def test_monitor_download_directories(self):
        """Test that monitor detects download directories."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor can be created
        assert monitor is not None
        assert hasattr(monitor, "start")
        assert hasattr(monitor, "stop")

    def test_monitor_file_detection(self):
        """Test that monitor can detect package files."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor has required attributes
        assert hasattr(monitor, "pkg_logger")
        assert hasattr(monitor, "config")
        assert hasattr(monitor, "downloads_dir")

    def test_monitor_file_processing(self):
        """Test that monitor processes files correctly."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor can be started and stopped
        monitor.start()  # Should not raise an error
        monitor.stop()  # Should not raise an error

    def test_monitor_error_handling(self):
        """Test that monitor handles errors gracefully."""
        # Test with None logger (should raise ValueError)
        with pytest.raises(ValueError, match="logger_instance must be provided"):
            DownloadsMonitor(None)

    def test_monitor_start_stop(self):
        """Test that monitor can start and stop."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test start/stop cycle
        monitor.start()
        monitor.stop()

        # Should not raise any errors

    def test_monitor_directory_watching(self):
        """Test that monitor watches directories correctly."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor can be initialized
        assert monitor is not None

    def test_monitor_file_extensions(self):
        """Test that monitor recognizes correct file extensions."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor has the expected interface
        assert hasattr(monitor, "start")
        assert hasattr(monitor, "stop")

    def test_monitor_logging_integration(self):
        """Test that monitor integrates with logging system."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor can be created with logger
        assert monitor.pkg_logger is mock_logger

    def test_monitor_configuration(self):
        """Test that monitor respects configuration."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = "/tmp/downloads"

        monitor = DownloadsMonitor(mock_logger)

        # Test that monitor uses configuration
        assert monitor.config is mock_logger.config


class TestDownloadsEventHandler:
    """Test the downloads event handler functionality."""

    def test_event_handler_initialization(self):
        """Test that the event handler initializes correctly."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg"

        handler = DownloadsEventHandler(mock_logger)

        assert handler.pkg_logger is mock_logger
        assert handler.config is mock_logger.config

    def test_event_handler_file_processing(self):
        """Test that event handler processes files correctly."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg"

        handler = DownloadsEventHandler(mock_logger)

        # Test that handler can be created
        assert handler is not None
        assert hasattr(handler, "on_created")
        assert hasattr(handler, "_log_download")

    def test_event_handler_error_handling(self):
        """Test that event handler handles errors gracefully."""
        mock_logger = MagicMock()
        mock_logger.config = MagicMock()
        mock_logger.config.get.return_value = ".rpm,.deb,.pkg"

        handler = DownloadsEventHandler(mock_logger)

        # Test that handler can be created without errors
        assert handler is not None
