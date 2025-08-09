"""Test configuration and fixtures."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture()
def tmp_home(monkeypatch, tmp_path: Path):
    """Fixture that patches Path.home() and HOME so code writes under tmppath."""
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path


@pytest.fixture()
def sample_package_data():
    """Sample package data for testing."""
    return [
        {
            "name": "test-package-1",
            "manager": "dnf",
            "action": "install",
            "version": "1.0.0",
            "architecture": "x86_64",
            "timestamp": "2024-01-01T12:00:00Z",
            "removed": False,
            "metadata": {"repo": "fedora", "size": "1024"},
        },
        {
            "name": "test-package-2",
            "manager": "dnf",
            "action": "remove",
            "version": "2.0.0",
            "architecture": "x86_64",
            "timestamp": "2024-01-02T12:00:00Z",
            "removed": True,
            "metadata": {"repo": "fedora"},
        },
        {
            "name": "test-file.rpm",
            "manager": "download",
            "action": "install",
            "version": "1.5.0",
            "architecture": "x86_64",
            "timestamp": "2024-01-03T12:00:00Z",
            "removed": False,
            "metadata": {"path": "/tmp/test-file.rpm", "size": "2048"},
        },
    ]


@pytest.fixture()
def mock_config():
    """Mock configuration object."""
    config = MagicMock()
    config.scope = "user"
    config.get.return_value = "user"
    return config


@pytest.fixture()
def mock_logger(tmp_path):
    """Mock logger with temporary directory."""
    logger = MagicMock()
    logger.data_dir = tmp_path / "prez-pkglog"
    logger.json_file = tmp_path / "prez-pkglog" / "packages.json"
    logger.toml_file = tmp_path / "prez-pkglog" / "packages.toml"
    logger.get_statistics.return_value = {
        "total": 3,
        "installed": 2,
        "removed": 1,
        "downloads": 1,
        "scope": "user",
    }
    return logger


@pytest.fixture()
def temp_json_file(tmp_path, sample_package_data):
    """Create a temporary JSON file with sample data."""
    json_file = tmp_path / "test_packages.json"
    with open(json_file, "w") as f:
        json.dump(sample_package_data, f)
    return json_file


@pytest.fixture()
def mock_subprocess():
    """Mock subprocess for testing command execution."""
    with pytest.MonkeyPatch().context() as m:
        mock_run = MagicMock()
        m.setattr("subprocess.run", mock_run)
        yield mock_run


@pytest.fixture()
def mock_platform():
    """Mock platform detection."""
    with pytest.MonkeyPatch().context() as m:
        m.setattr("platform.system", lambda: "Linux")
        m.setattr("platform.machine", lambda: "x86_64")
        yield


@pytest.fixture()
def mock_dnf_transaction():
    """Mock DNF transaction object."""
    transaction = MagicMock()

    # Mock installed packages
    install_pkg1 = MagicMock()
    install_pkg1.name = "test-package-1"
    install_pkg1.version = "1.0.0"
    install_pkg1.arch = "x86_64"
    install_pkg1.repo = MagicMock()
    install_pkg1.repo.name = "fedora"

    install_pkg2 = MagicMock()
    install_pkg2.name = "test-package-2"
    install_pkg2.version = "2.0.0"
    install_pkg2.arch = "x86_64"
    install_pkg2.repo = MagicMock()
    install_pkg2.repo.name = "updates"

    # Mock removed packages
    remove_pkg = MagicMock()
    remove_pkg.name = "old-package"
    remove_pkg.version = "0.9.0"
    remove_pkg.arch = "x86_64"
    remove_pkg.repo = MagicMock()
    remove_pkg.repo.name = "fedora"

    transaction.install_set = [install_pkg1, install_pkg2]
    transaction.remove_set = [remove_pkg]

    return transaction
