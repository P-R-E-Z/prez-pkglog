"""Unit tests for the logger module"""

import json
from unittest.mock import patch


from src.prez_pkglog.logger import PackageLogger
from src.prez_pkglog.config import Config


class TestPackageLogger:
    """Test the PackageLogger class."""

    def test_init_user_scope(self):
        """Test logger initialization with user scope."""
        config = Config()
        config.set("scope", "user")

        logger = PackageLogger(config)

        assert logger.config.scope == "user"
        assert "prez-pkglog" in str(logger.data_dir)

    def test_init_system_scope(self):
        """Test logger initialization with system scope."""
        config = Config()
        config.set("scope", "system")

        # Mock the data directory creation to avoid permission issues
        with (
            patch("pathlib.Path.mkdir") as mock_mkdir,
            patch("pathlib.Path.chmod") as mock_chmod,
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            logger = PackageLogger(config)

            assert logger.config.scope == "system"
            assert "/var/log/prez-pkglog" in str(logger.data_dir)
            mock_mkdir.assert_called_once()
            mock_chmod.assert_called()
            mock_write.assert_called()

    def test_log_package_success(self, tmp_path):
        """Test successful package logging."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = tmp_path

            config = Config()
            config.set("scope", "user")
            logger = PackageLogger(config)

            # Test logging a package
            logger.log_package("test-package", "dnf", "install")

            # Verify log file was created and contains entry
            assert logger.json_file.exists()

            with open(logger.json_file) as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]["name"] == "test-package"
                assert data[0]["manager"] == "dnf"
                assert data[0]["action"] == "install"

    def test_log_package_invalid_name(self, tmp_path):
        """Test logging with invalid package name."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = tmp_path

            config = Config()
            config.set("scope", "user")
            logger = PackageLogger(config)

            # Test with empty name
            logger.log_package("", "dnf", "install")

            # Verify no entry was added
            assert logger.json_file.exists()

            with open(logger.json_file) as f:
                data = json.load(f)
                assert len(data) == 0

    def test_get_statistics(self, tmp_path):
        """Test statistics calculation."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = tmp_path

            config = Config()
            config.set("scope", "user")
            logger = PackageLogger(config)

            # Add some test data
            test_data = [
                {
                    "name": "pkg1",
                    "manager": "dnf",
                    "action": "install",
                    "removed": False,
                },
                {
                    "name": "pkg2",
                    "manager": "dnf",
                    "action": "remove",
                    "removed": True,
                },
                {
                    "name": "file.rpm",
                    "manager": "download",
                    "action": "install",
                    "removed": False,
                },
            ]

            with open(logger.json_file, "w") as f:
                json.dump(test_data, f)

            stats = logger.get_statistics()

            assert stats["total"] == 3
            assert stats["installed"] == 2
            assert stats["removed"] == 1
            assert stats["downloads"] == 1
            assert stats["scope"] == "user"
