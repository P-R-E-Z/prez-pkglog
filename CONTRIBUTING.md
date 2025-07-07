# Contributing to prez-pkglog

This document provides guidelines and instructions for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Adding New Package Manager Backends](#adding-new-package-manager-backends)
- [Adding New Platforms](#adding-new-platforms)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

---

## Getting Started

### Prerequisites

- Python 3.13+
- Git

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/prez-pkglog.git
   cd prez-pkglog
   ```

3. Add the upstream repository:

   ```bash
   git remote add upstream https://github.com/P-R-E-Z/prez-pkglog.git
   ```

---

## Development Setup

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install
```

---

## Adding New Package Manager Backends

### Backend Structure

Each backend should inherit from `PackageBackend` and implement the required methods:

```python
# src/prez_pkglog/backends/example.py
from __future__ import annotations

import shutil
import subprocess
from typing import Any

from .base import PackageBackend, PackageInfo
from .. import register_backend

class ExampleBackend(PackageBackend):
    """Backend for Example package manager"""

    @classmethod
    def is_available(cls) -> bool:
        """Check if the package manager is available"""
        return bool(shutil.which("example-package-manager"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get installed packages"""
        if not self.enabled:
            return {}

        try:
            # Use subprocess to query package manager
            result = subprocess.run(
                ["example-package-manager", "list", "--installed"],
                capture_output=True,
                text=True,
                check=True
            )

            packages = {}
            for line in result.stdout.splitlines():
                if line.strip():
                    # Parse package information
                    name, version, arch = self._parse_package_line(line)
                    packages[name] = PackageInfo(
                        name=name,
                        version=version,
                        architecture=arch,
                        installed=True,
                    )

            return packages

        except (subprocess.SubprocessError, OSError) as e:
            logger.error(f"Failed to get installed packages: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """Register a package transaction for logging"""
        if not self.enabled:
            return False

        success = True

        # Log installed packages
        for pkg in getattr(transaction, "install_set", []):
            if not self._log_package_install(pkg):
                success = False

        # Log removed packages
        for pkg in getattr(transaction, "remove_set", []):
            if not self._log_package_remove(pkg):
                success = False

        return success

    def _parse_package_line(self, line: str) -> tuple[str, str, str]:
        """Parse a package line from package manager output"""
        # Implement parsing logic for your package manager
        parts = line.split()
        name = parts[0]
        version = parts[1] if len(parts) > 1 else ""
        arch = parts[2] if len(parts) > 2 else ""
        return name, version, arch

    def _log_package_install(self, pkg: Any) -> bool:
        """Log an installed package"""
        try:
            name = getattr(pkg, "name", "")
            version = getattr(pkg, "version", "")

            self.logger.log_package(
                name=name,
                manager=self.name,
                action="install",
                version=version,
                metadata={
                    "arch": getattr(pkg, "arch", None),
                    "repo": getattr(getattr(pkg, "repo", {}), "name", None),
                },
            )
            return True

        except Exception as e:
            logger.error(f"Error logging package install {getattr(pkg, 'name', 'unknown')}: {e}")
            return False

    def _log_package_remove(self, pkg: Any) -> bool:
        """Log a removed package"""
        try:
            name = getattr(pkg, "name", "")
            version = getattr(pkg, "version", "")

            self.logger.log_package(
                name=name,
                manager=self.name,
                action="remove",
                version=version,
                metadata={
                    "arch": getattr(pkg, "arch", None),
                    "repo": getattr(getattr(pkg, "repo", {}), "name", None),
                },
            )
            return True

        except Exception as e:
            logger.error(f"Error logging package removal {getattr(pkg, 'name', 'unknown')}: {e}")
            return False

# Register the backend
register_backend(ExampleBackend.name, ExampleBackend)
```

### Backend Registration

Add your backend to the registration in `src/prez_pkglog/backends/__init__.py`:

```python
# Import your new backend
from .example import ExampleBackend  # noqa: F401
```

### Testing Your Backend

Create tests in `tests/backends/test_example.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from src.prez_pkglog.backends.example import ExampleBackend

class TestExampleBackend:
    def test_is_available(self):
        """Test availability detection"""
        with patch('shutil.which') as mock_which:
            mock_which.return_value = "/usr/bin/example-package-manager"
            assert ExampleBackend.is_available() is True

            mock_which.return_value = None
            assert ExampleBackend.is_available() is False

    def test_get_installed_packages(self):
        """Test package listing"""
        backend = ExampleBackend()

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="package1 1.0.0 x86_64\npackage2 2.0.0 x86_64",
                returncode=0
            )

            packages = backend.get_installed_packages()
            assert len(packages) == 2
            assert "package1" in packages
            assert "package2" in packages

    def test_register_transaction(self):
        """Test transaction logging"""
        backend = ExampleBackend()

        # Mock transaction object
        transaction = MagicMock()
        transaction.install_set = [MagicMock(name="package1")]
        transaction.remove_set = [MagicMock(name="package2")]

        # Mock logger
        backend.logger = MagicMock()

        result = backend.register_transaction(transaction)
        assert result is True
```

---

## Adding New Platforms

### Platform Detection

Add platform-specific utilities in `src/prez_pkglog/utils/platform.py`:

```python
import sys
import platform

def detect_platform() -> str:
    """Detect the current platform"""
    system = platform.system().lower()

    if system == "linux":
        # Detect specific Linux distributions
        try:
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return "debian"
                elif "fedora" in content:
                    return "fedora"
                elif "arch" in content:
                    return "arch"
                else:
                    return "linux"
        except FileNotFoundError:
            return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"

def get_platform_specific_paths() -> dict[str, str]:
    """Get platform-specific file paths"""
    platform = detect_platform()

    if platform == "fedora":
        return {
            "config_dir": "/etc/prez-pkglog",
            "log_dir": "/var/log/prez-pkglog",
            "user_config": "~/.config/prez-pkglog",
            "user_log": "~/.local/share/prez-pkglog"
        }
    elif platform == "debian":
        return {
            "config_dir": "/etc/prez-pkglog",
            "log_dir": "/var/log/prez-pkglog",
            "user_config": "~/.config/prez-pkglog",
            "user_log": "~/.local/share/prez-pkglog"
        }
    # Add more platforms as needed

    return {
        "config_dir": "/etc/prez-pkglog",
        "log_dir": "/var/log/prez-pkglog",
        "user_config": "~/.config/prez-pkglog",
        "user_log": "~/.local/share/prez-pkglog"
    }
```

### Platform-Specific Configuration

Create platform-specific configuration templates in `config/platforms/`:

```ini
# config/platforms/fedora.conf
[main]
scope = user
enable_dnf_hooks = true
enable_download_monitoring = true
downloads_dir = ~/Downloads
log_format = both

[dnf]
enabled = true
plugin_config = /etc/dnf/plugins/prez_pkglogger.conf
```

---

## Code Style

### Python Code

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Use f-strings for string formatting
- Keep functions small and focused
- Add docstrings for all public functions and classes

### Example

```python
from typing import Optional, Dict, Any
from pathlib import Path

def process_package_info(
    package_name: str,
    version: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process package information and return standardized format.

    Args:
        package_name: Name of the package
        version: Version string (optional)
        metadata: Additional metadata (optional)

    Returns:
        Dictionary containing processed package information

    Raises:
        ValueError: If package_name is empty or invalid
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    result = {
        "name": package_name.strip(),
        "processed_at": datetime.now().isoformat()
    }

    if version:
        result["version"] = version

    if metadata:
        result["metadata"] = metadata

    return result
```

### Configuration Files

- Use INI format for configuration files
- Use descriptive section and key names
- Include comments for complex settings
- Provide default values where appropriate

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/backends/test_dnf.py

# Run with coverage
pytest --cov=src/prez_pkglog

# Run linting
ruff check src/

# Run type checking
mypy src/
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Mock external dependencies
- Test both success and failure cases
- Test edge cases and error conditions

### Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock
from src.prez_pkglog.core.logger import PackageLogger

class TestPackageLogger:
    """Test the PackageLogger class."""

    def test_log_package_success(self, tmp_path):
        """Test successful package logging."""
        logger = PackageLogger()

        # Test logging a package
        logger.log_package("test-package", "dnf", "install")

        # Verify log file was created and contains entry
        log_file = logger.json_file
        assert log_file.exists()

        with open(log_file) as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["name"] == "test-package"

    def test_log_package_invalid_name(self):
        """Test logging with invalid package name."""
        logger = PackageLogger()

        with pytest.raises(ValueError):
            logger.log_package("", "dnf", "install")

    @patch('pathlib.Path.exists')
    def test_setup_directories(self, mock_exists):
        """Test directory setup."""
        mock_exists.return_value = False

        logger = PackageLogger()
        # Verify directories were created
        assert logger.data_dir.exists()
```

---

## Submitting Changes

### Creating a Pull Request

1. Create a new branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:

   ```bash
   git add .
   git commit -m "Add new package manager backend for Example"
   ```

3. Push your branch and create a pull request:

   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Use conventional commit format:

```ini
type(scope): description

[optional body]

[optional footer]
```

Examples:

- `feat(backend): add apt package manager backend`
- `fix(logger): handle empty package names gracefully`
- `docs(readme): update installation instructions`
- `test(backend): add tests for dnf backend`

### Pull Request Guidelines

- Provide a clear description of your changes
- Include tests for new functionality
- Update documentation if needed
- Ensure all tests pass
- Follow the code style guidelines

---

## Release Process

### Version Bumping

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Creating a Release

1. Update version in `prez-pkglog.spec`
2. Update `CHANGELOG.md`
3. Create a git tag:

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. Create a GitHub release with release notes

---

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions for questions
- Check existing issues and pull requests

## Anyone Can Help

I welcome contributors from all backgrounds and experience levels.

---

Thank you for contributing to prez-pkglog
