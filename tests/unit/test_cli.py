"""Unit tests for the CLI module"""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from src.prez_pkglog.cli import cli


class TestCLI:
    """Test the CLI interface."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Prez Package Logger" in result.output

    def test_setup_user_scope(self):
        """Test setup command with user scope."""
        with (
            patch("src.prez_pkglog.config.Config") as mock_config_class,
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
        ):
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config

            mock_logger = MagicMock()
            mock_logger.data_dir = "/tmp/test"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(cli, ["setup", "--scope", "user"])

            assert result.exit_code == 0
            assert "Setup complete for user scope" in result.output
            mock_config.set.assert_called_with("scope", "user")

    def test_setup_system_scope(self):
        """Test setup command with system scope."""
        with (
            patch("src.prez_pkglog.config.Config") as mock_config_class,
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
            patch("os.geteuid", return_value=0),
        ):  # Mock as root
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config

            mock_logger = MagicMock()
            mock_logger.data_dir = "/var/log/test"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(cli, ["setup", "--scope", "system"])

            assert result.exit_code == 0
            assert "Setup complete for system scope" in result.output
            mock_config.set.assert_called_with("scope", "system")

    def test_setup_invalid_scope(self):
        """Test setup command with invalid scope."""
        result = self.runner.invoke(cli, ["setup", "--scope", "invalid"])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_status_user_scope(self):
        """Test status command with user scope."""
        with patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger.get_statistics.return_value = {
                "total": 5,
                "installed": 3,
                "removed": 2,
                "downloads": 1,
                "scope": "user",
            }
            mock_logger.data_dir = "/tmp/test"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(cli, ["status", "--scope", "user"])

            assert result.exit_code == 0
            assert "Total packages logged: 5" in result.output
            assert "Installed: 3" in result.output
            assert "Removed: 2" in result.output
            assert "Downloads: 1" in result.output

    def test_status_system_scope(self):
        """Test status command with system scope."""
        with (
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
            patch("os.geteuid", return_value=0),
        ):  # Mock as root
            mock_logger = MagicMock()
            mock_logger.get_statistics.return_value = {
                "total": 10,
                "installed": 8,
                "removed": 2,
                "downloads": 0,
                "scope": "system",
            }
            mock_logger.data_dir = "/var/log/test"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(cli, ["status", "--scope", "system"])

            assert result.exit_code == 0
            assert "Total packages logged: 10" in result.output
            assert "Installed: 8" in result.output
            assert "Removed: 2" in result.output

    def test_export_json_format(self):
        """Test export command with JSON format."""
        with patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger.json_file = MagicMock()
            mock_logger.json_file.read_text.return_value = '[{"name": "test"}]'
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(
                cli, ["export", "--format", "json", "--scope", "user"]
            )

            assert result.exit_code == 0
            assert '{"name": "test"}' in result.output

    def test_export_toml_format(self):
        """Test export command with TOML format."""
        with patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger.toml_file = MagicMock()
            mock_logger.toml_file.read_text.return_value = "# Test package"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(
                cli, ["export", "--format", "toml", "--scope", "user"]
            )

            assert result.exit_code == 0
            assert "# Test package" in result.output

    def test_export_invalid_format(self):
        """Test export command with invalid format."""
        result = self.runner.invoke(
            cli, ["export", "--format", "invalid", "--scope", "user"]
        )

        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_daemon_user_scope(self):
        """Test daemon command with user scope."""
        with (
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
            patch(
                "src.prez_pkglog.monitors.downloads.DownloadsMonitor"
            ) as mock_monitor_class,
        ):
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            mock_monitor = MagicMock()
            mock_monitor_class.return_value = mock_monitor

            # Mock KeyboardInterrupt to exit the daemon
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                result = self.runner.invoke(cli, ["daemon", "--scope", "user"])

            assert result.exit_code == 0
            assert "Monitoring started" in result.output
            assert "Monitoring stopped" in result.output
            mock_monitor.start.assert_called_once()
            mock_monitor.stop.assert_called_once()

    def test_daemon_system_scope(self):
        """Test daemon command with system scope (no download monitoring)."""
        with (
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
            patch("os.geteuid", return_value=0),
        ):  # Mock as root
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Mock KeyboardInterrupt to exit the daemon
            with patch("time.sleep", side_effect=KeyboardInterrupt):
                result = self.runner.invoke(cli, ["daemon", "--scope", "system"])

            assert result.exit_code == 0
            assert "System scope monitoring started" in result.output
            assert "Monitoring stopped" in result.output

    def test_default_scope_is_user(self):
        """Test that default scope is user when not specified."""
        with (
            patch("src.prez_pkglog.config.Config") as mock_config_class,
            patch("src.prez_pkglog.logger.PackageLogger") as mock_logger_class,
        ):
            mock_config = MagicMock()
            mock_config.get.return_value = "user"
            mock_config_class.return_value = mock_config

            mock_logger = MagicMock()
            mock_logger.get_statistics.return_value = {
                "total": 0,
                "installed": 0,
                "removed": 0,
                "downloads": 0,
                "scope": "user",
            }
            mock_logger.data_dir = "/tmp/test"
            mock_logger_class.return_value = mock_logger

            result = self.runner.invoke(cli, ["status"])

            assert result.exit_code == 0
            mock_config.set.assert_called_with("scope", "user")
