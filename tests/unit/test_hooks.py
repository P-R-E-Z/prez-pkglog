from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.prez_pkglog.monitors.downloads import DownloadsMonitor, DownloadsEventHandler


class TestDownloadsMonitor:
    """Test the downloads monitoring functionality."""

    def test_downloads_monitor_initialization(self):
        """Test downloads monitor initialization."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/Downloads"
        mock_logger.config = mock_config

        monitor = DownloadsMonitor(mock_logger)

        assert monitor.pkg_logger == mock_logger
        assert monitor.config == mock_config

    def test_downloads_monitor_invalid_logger(self):
        """Test downloads monitor with invalid logger."""
        with pytest.raises(ValueError, match="logger_instance must be provided"):
            DownloadsMonitor(None)

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_downloads_monitor_start_success(self):
        """Test starting downloads monitor successfully."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/Downloads"
        mock_logger.config = mock_config

        with (
            patch("src.prez_pkglog.monitors.downloads.Observer") as mock_observer_class,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_observer = MagicMock()
            mock_observer_class.return_value = mock_observer

            monitor = DownloadsMonitor(mock_logger)
            monitor.start()

            mock_observer.schedule.assert_called_once()
            mock_observer.start.assert_called_once()

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", False)
    def test_downloads_monitor_start_no_watchdog(self):
        """Test starting monitor without watchdog library."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/Downloads"
        mock_logger.config = mock_config

        monitor = DownloadsMonitor(mock_logger)
        monitor.start()

        # Should not crash, just log warning

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_downloads_monitor_start_missing_directory(self):
        """Test starting monitor with missing downloads directory."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/NonexistentDownloads"
        mock_logger.config = mock_config

        with patch("pathlib.Path.exists", return_value=False):
            monitor = DownloadsMonitor(mock_logger)
            monitor.start()

            # Should not crash, just log warning

    def test_downloads_monitor_stop(self):
        """Test stopping downloads monitor."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/Downloads"
        mock_logger.config = mock_config

        mock_observer = MagicMock()

        monitor = DownloadsMonitor(mock_logger)
        monitor.observer = mock_observer
        monitor.stop()

        mock_observer.stop.assert_called_once()
        mock_observer.join.assert_called_once()

    def test_downloads_monitor_stop_no_observer(self):
        """Test stopping monitor when no observer is running."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = "~/Downloads"
        mock_logger.config = mock_config

        monitor = DownloadsMonitor(mock_logger)
        # Should not crash when stopping without observer
        monitor.stop()


class TestDownloadsEventHandler:
    """Test the downloads event handler functionality."""

    def test_downloads_event_handler_initialization(self):
        """Test downloads event handler initialization."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_logger.config = mock_config

        handler = DownloadsEventHandler(mock_logger)

        assert handler.pkg_logger == mock_logger
        assert handler.config == mock_config

    def test_downloads_event_handler_file_created_rpm(self):
        """Test downloads event handler on RPM file creation."""
        import tempfile

        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".rpm,.deb,.pkg"
        mock_logger.config = mock_config

        with tempfile.NamedTemporaryFile(suffix=".rpm", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            handler = DownloadsEventHandler(mock_logger)

            # Mock file system event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = tmp_path

            handler.on_created(mock_event)

            mock_logger.log_package.assert_called_once()
            call_args = mock_logger.log_package.call_args

            # Check positional arguments: name, manager, action
            assert call_args[0][1] == "download"  # manager
            assert call_args[0][2] == "install"  # action
            # Check metadata keyword argument
            assert call_args[1]["metadata"]["file_type"] == ".rpm"
            assert "file_path" in call_args[1]["metadata"]
            assert "file_size" in call_args[1]["metadata"]

        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)

    def test_downloads_event_handler_file_created_deb(self):
        """Test downloads event handler on DEB file creation."""
        import tempfile

        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".rpm,.deb,.pkg"
        mock_logger.config = mock_config

        with tempfile.NamedTemporaryFile(suffix=".deb", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            handler = DownloadsEventHandler(mock_logger)

            # Mock file system event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = tmp_path

            handler.on_created(mock_event)

            mock_logger.log_package.assert_called_once()
            call_args = mock_logger.log_package.call_args

            # Check that it's logged as a download
            assert call_args[0][1] == "download"  # manager
            assert call_args[0][2] == "install"  # action
            assert call_args[1]["metadata"]["file_type"] == ".deb"

        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)

    def test_downloads_event_handler_directory_created(self):
        """Test downloads event handler ignores directory creation."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_logger.config = mock_config

        handler = DownloadsEventHandler(mock_logger)

        # Mock directory event
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = "/path/to/directory"

        handler.on_created(mock_event)

        mock_logger.log_package.assert_not_called()

    def test_downloads_event_handler_non_package_file(self):
        """Test downloads event handler ignores non-package files."""
        import tempfile

        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".rpm,.deb,.pkg"
        mock_logger.config = mock_config

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            handler = DownloadsEventHandler(mock_logger)

            # Mock file system event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = tmp_path

            handler.on_created(mock_event)

            mock_logger.log_package.assert_not_called()

        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)

    def test_downloads_event_handler_case_insensitive(self):
        """Test downloads event handler handles case-insensitive extensions."""
        import tempfile

        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".rpm,.deb,.pkg"
        mock_logger.config = mock_config

        with tempfile.NamedTemporaryFile(suffix=".RPM", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            handler = DownloadsEventHandler(mock_logger)

            # Mock file system event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = tmp_path

            handler.on_created(mock_event)

            mock_logger.log_package.assert_called_once()
            call_args = mock_logger.log_package.call_args

            # Should normalize to lowercase
            assert call_args[1]["metadata"]["file_type"] == ".rpm"

        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)

    def test_downloads_event_handler_file_stat_error(self):
        """Test downloads event handler handles file stat errors gracefully."""
        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".rpm,.deb,.pkg"
        mock_logger.config = mock_config

        handler = DownloadsEventHandler(mock_logger)

        # Mock file system event with non-existent file
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/non/existent/file.rpm"

        handler.on_created(mock_event)

        # Should still log the package even if file stat fails
        mock_logger.log_package.assert_called_once()
        call_args = mock_logger.log_package.call_args

        # File size should be 0 when stat fails
        assert call_args[1]["metadata"]["file_size"] == 0

    def test_downloads_event_handler_custom_extensions(self):
        """Test downloads event handler with custom monitored extensions."""
        import tempfile

        mock_logger = MagicMock()
        mock_config = MagicMock()
        mock_config.get.return_value = ".snap,.flatpak,.appimage"
        mock_logger.config = mock_config

        with tempfile.NamedTemporaryFile(suffix=".snap", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            handler = DownloadsEventHandler(mock_logger)

            # Mock file system event
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = tmp_path

            handler.on_created(mock_event)

            mock_logger.log_package.assert_called_once()
            call_args = mock_logger.log_package.call_args

            assert call_args[1]["metadata"]["file_type"] == ".snap"

        finally:
            # Clean up
            Path(tmp_path).unlink(missing_ok=True)


class TestHooksIntegration:
    """Test integration between different hook systems."""

    def test_plugin_file_exists(self):
        """Test that plugin files exist in correct locations."""
        plugin_file = Path("src/prez_pkglog/hooks/dnf/plugin.py")
        assert plugin_file.exists(), "DNF plugin file should exist"

        downloads_file = Path("src/prez_pkglog/monitors/downloads.py")
        assert downloads_file.exists(), "Downloads monitor file should exist"

    def test_plugin_imports(self):
        """Test that plugin has correct imports."""
        plugin_file = Path("src/prez_pkglog/hooks/dnf/plugin.py")

        if plugin_file.exists():
            content = plugin_file.read_text()

            # Should import required modules
            assert "import dnf" in content
            assert "from prez_pkglog.config import Config" in content
            assert "from prez_pkglog.logger import PackageLogger" in content

    def test_downloads_monitor_imports(self):
        """Test that downloads monitor has correct imports."""
        downloads_file = Path("src/prez_pkglog/monitors/downloads.py")

        if downloads_file.exists():
            content = downloads_file.read_text()

            # Should handle watchdog imports gracefully
            assert "from watchdog.observers import Observer" in content
            assert "WATCHDOG_AVAILABLE" in content

    def test_hooks_directory_structure(self):
        """Test that hooks directory structure is correct."""
        hooks_dir = Path("src/prez_pkglog/hooks")
        assert hooks_dir.exists(), "Hooks directory should exist"

        dnf_hooks_dir = hooks_dir / "dnf"
        assert dnf_hooks_dir.exists(), "DNF hooks directory should exist"

        monitors_dir = Path("src/prez_pkglog/monitors")
        assert monitors_dir.exists(), "Monitors directory should exist"

    def test_libdnf5_plugin_structure(self):
        """Test that libdnf5 plugin structure exists."""
        libdnf5_dir = Path("libdnf5-plugin")
        assert libdnf5_dir.exists(), "libdnf5-plugin directory should exist"

        cmake_file = libdnf5_dir / "dnf5-plugin" / "CMakeLists.txt"
        assert cmake_file.exists(), "CMakeLists.txt should exist"

        actions_dir = libdnf5_dir / "dnf5-plugin" / "actions.d"
        assert actions_dir.exists(), "actions.d directory should exist"

        actions_file = actions_dir / "prez_pkglog.actions"
        assert actions_file.exists(), "prez_pkglog.actions file should exist"

    def test_actions_file_content(self):
        """Test that actions file has correct content."""
        actions_file = Path("libdnf5-plugin/dnf5-plugin/actions.d/prez_pkglog.actions")

        if actions_file.exists():
            content = actions_file.read_text()

            # Should contain post_transaction hooks
            assert "post_transaction:" in content
            assert "prez-pkglog install" in content
            assert "prez-pkglog remove" in content
            assert "${pkg.name}" in content


class TestWatchdogFallback:
    """Test watchdog fallback functionality."""

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", False)
    def test_fallback_classes_exist(self):
        """Test that fallback classes are available when watchdog is not installed."""
        # Re-import to trigger fallback
        import importlib
        import src.prez_pkglog.monitors.downloads

        importlib.reload(src.prez_pkglog.monitors.downloads)

        from src.prez_pkglog.monitors.downloads import FileSystemEventHandler, Observer

        # Should be able to instantiate fallback classes
        handler = FileSystemEventHandler()
        observer = Observer()

        # Methods should exist and not crash
        handler.on_created(None)
        observer.schedule(None, ".", recursive=False)
        observer.start()
        observer.stop()
        observer.join()

    @patch("src.prez_pkglog.monitors.downloads.WATCHDOG_AVAILABLE", True)
    def test_real_watchdog_imports(self):
        """Test that real watchdog classes are used when available."""
        # Re-import to use real watchdog
        import importlib
        import src.prez_pkglog.monitors.downloads

        importlib.reload(src.prez_pkglog.monitors.downloads)

        # Should not crash when watchdog is available
        from src.prez_pkglog.monitors.downloads import WATCHDOG_AVAILABLE

        assert WATCHDOG_AVAILABLE is True
