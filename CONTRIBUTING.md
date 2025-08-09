# Contributing to prez-pkglog

Welcome! This guide helps you contribute to prez-pkglog. Don't worry if you're new, this will guide you through everything step by step.

<details>
<summary><strong> Quick Start</strong></summary>

### For New Contributors

1. **Fork and clone** the repository
2. **Set up your environment** with `uv sync` or `pip install -e ".[dev]"`
3. **Make a small change** (like fixing a typo)
4. **Test your changes** with `make test`
5. **Submit a pull request**

</details>

<details>
<summary><strong>Table of Contents</strong></summary>

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing Your Changes](#testing-your-changes)
- [Submitting Changes](#submitting-changes)
- [Advanced Topics](#advanced-topics)
- [Getting Help](#getting-help)

</details>

---

## Getting Started

<details>
<summary><strong>What you need to get started</strong></summary>

### Prerequisites

- Python 3.13+
- Git
- C++ compiler (for dnf5 plugin development)
- CMake 3.18+ (for dnf5 plugin builds)
- pkg-config (for finding libdnf5)

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

</details>

---

## Development Setup

<details>
<summary><strong>Setting up your development environment</strong></summary>

### Virtual Environment

This project uses `uv` for dependency management. Install it first if you haven't:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync
```

Alternatively, you can use traditional pip:

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

The pre-commit hooks will automatically:
- Check for large files, case conflicts, merge conflicts
- Fix trailing whitespace and end-of-file issues
- Run ruff for linting and formatting
- Validate YAML files

</details>

---

## Making Changes

<details>
<summary><strong>Common development tasks and commands</strong></summary>

### Development Commands

The project includes a Makefile with common development tasks:

```bash
# Code quality
make lint          # Run ruff linting
make mypy          # Run type checking
make format        # Format Python and C++ code
make check-format  # Check formatting without fixing

# Testing
make test          # Run pytest

# Building
make build         # Build sdist and wheel
make sdist         # Build source distribution
make wheel         # Build wheel distribution

# RPM packaging (Fedora/RHEL)
make srpm          # Build source RPM
make rpm           # Build binary RPM
make mock          # Build in mock environment
make install       # Install built RPM

# Release (maintainer only)
make release v=patch|minor|major  # Bump version, commit, and push
```

### Code Style

<details>
<summary><strong>Python Code Guidelines</strong></summary>

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Use f-strings for string formatting
- Keep functions small and focused
- Add docstrings for all public functions and classes
- Line length: 100 characters (configured in ruff and black)

</details>

<details>
<summary><strong>C++ Code Guidelines</strong></summary>

- Follow the project's `.clang-format` configuration
- Use C++20 standard
- Include proper error handling
- Add comments for complex logic
- Test plugin functionality thoroughly

</details>

</details>

---

## Testing Your Changes

<details>
<summary><strong>How to test your changes</strong></summary>

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

# Check C++ formatting
clang-format --dry-run --Werror libdnf5-plugin/dnf5-plugin/src/*.cpp

# Format C++ code
clang-format -i libdnf5-plugin/dnf5-plugin/src/*.cpp
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Mock external dependencies
- Test both success and failure cases
- Test edge cases and error conditions
- For C++ plugins, test compilation and basic functionality

</details>

---

## Submitting Changes

<details>
<summary><strong>How to submit your changes</strong></summary>

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
- For C++ changes, ensure the plugin builds and installs correctly
- Run `make check-format` to verify formatting

**Note**: All pull requests will be reviewed before approval. The maintainer will determine the appropriate version bump type (patch/minor/major) based on the scope and impact of changes.

### Pre-submission Checklist

Before submitting your pull request, ensure:

- [ ] All tests pass (`make test`)
- [ ] Code is properly formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`make mypy`)
- [ ] Documentation is updated if needed
- [ ] New functionality has tests
- [ ] Commit messages follow conventional format

</details>

---

## Advanced Topics

<details>
<summary><strong>Adding new package manager backends</strong></summary>

### Backend Structure

Backends are located in `src/prez_pkglog/backends/` under their respective operating system directory (`linux/`, `macos/`, or `windows/`). For example, the APT backend should be located at `src/prez_pkglog/backends/linux/apt.py`.

Each backend must inherit from `PackageBackend` and implement the required methods. The application will automatically discover and load any valid backend from these directories at runtime.

### Backend Setup Instructions

Different package managers require different setup approaches for automatic logging:

#### APT (Debian/Ubuntu)
Create a file at `/etc/apt/apt.conf.d/99prez-pkglog` with:
```
DPkg::Post-Invoke {
    "if [ -x /usr/local/bin/prez-pkglog-apt ]; then /usr/local/bin/prez-pkglog-apt; fi";
};
```

#### Pacman (Arch Linux)
Create a hook file at `/etc/pacman.d/hooks/prez-pkglog.hook` with:
```ini
[Trigger]
Operation = Install
Operation = Upgrade
Operation = Remove
Type = Package
Target = *

[Action]
Description = Log package transaction with prez-pkglog
When = PostTransaction
Exec = /usr/bin/prez-pkglog-pacman
```

#### Homebrew (macOS)
Add this to your `~/.zshrc` or `~/.bash_profile`:
```bash
function brew() {
    case "$1" in
        install|uninstall|reinstall|upgrade)
            command brew "$@"
            /usr/local/bin/prez-pkglog-brew-hook
            ;;
        *)
            command brew "$@"
            ;;
    esac
}
```

#### Chocolatey (Windows)
Create PowerShell scripts in `$env:ChocolateyInstall\hooks` (e.g., `pre-install.ps1`, `post-uninstall.ps1`) that call the `prez-pkglog` CLI.

#### Winget (Windows)
Winget doesn't have hooks, so implement logging by either:
1. Creating a PowerShell wrapper function for `winget`
2. Periodically polling and diffing the output of `winget list`

### Backend Template

Here is a generic template for a new backend:

```python
# src/prez_pkglog/backends/linux/example.py
from __future__ import annotations

import shutil
import subprocess
from typing import Any

from ..base import PackageBackend, PackageInfo

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

# No registration needed
# The backend is loaded automatically from its location.
```

### Testing Your Backend

Create tests for your new backend in the corresponding `tests/` directory (e.g., `tests/unit/backends/linux/test_example.py`):

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

</details>

<details>
<summary><strong>C++ Plugin Development</strong></summary>

### DNF5 Plugin

The project includes a C++ plugin for DNF5 (Fedora's package manager). The plugin is located in `dnf5-plugin/` and uses CMake for building.

#### Building the Plugin

```bash
# Install C++ build dependencies (Fedora/RHEL)
sudo dnf install cmake clang-tools-extra pkgconfig libdnf5-devel

# Build the plugin
cd libdnf5-plugin/dnf5-plugin
mkdir build && cd build
cmake ..
make

# Install the plugin
sudo make install
```

#### Plugin Structure

- `libdnf5-plugin/dnf5-plugin/src/prez_pkglog_plugin.cpp` - Main plugin implementation (minimal loader)
- `libdnf5-plugin/dnf5-plugin/CMakeLists.txt` - Build configuration
- `libdnf5-plugin/dnf5-plugin/actions.d/prez_pkglog.actions` - Actions Plugin hooks for transaction logging

The plugin uses the DNF5 Actions Plugin system for actual transaction logging rather than direct C++ hooks.

#### Testing the Plugin

```bash
# Test that the plugin loads correctly
dnf5 --version

# Test with a package operation (requires root)
sudo dnf5 install test-package

# Verify transactions are logged
sudo prez-pkglog status
```

#### Scope Management

The DNF integration respects prez-pkglog's scope configuration:
- System scope (`/etc/prez-pkglog/`) takes precedence over user scope (`~/.config/prez-pkglog/`)
- Configuration files are automatically detected and prioritized
- Use `sudo prez-pkglog setup` to configure system scope properly

</details>

<details>
<summary><strong>Adding new platforms</strong></summary>

Supporting a new platform or distribution involves two main steps: ensuring the application can detect the platform and providing packaging files.

### Platform Detection

Platform-specific logic is handled in `src/prez_pkglog/utils/platform.py`. If you are adding a new Linux distribution or operating system, you may need to update the `detect_platform()` function to recognize it.

```python
# src/prez_pkglog/utils/platform.py

def detect_platform() -> str:
    """Detect the current platform"""
    system = platform.system().lower()
    if system == "linux":
        # ... distribution detection logic ...
```

You may also need to add platform-specific paths in `get_platform_specific_paths()` if they differ from the defaults.

### Packaging

To make it easier for users to install `prez-pkglog` on other systems, I encourage contributions of packaging templates. These should be placed in the `packaging/` directory, in a subdirectory named after the distribution (e.g., `packaging/suse/`).

I have existing examples for Arch Linux (`packaging/archlinux/`) and Debian (`packaging/debian/`) that can be used as a reference. These templates provide a starting point for creating native packages (`.pkg.tar.zst`, `.deb`, etc.) and setting up any necessary hooks for the native package manager.

A good packaging contribution includes:

- All necessary metadata files (`PKGBUILD`, `debian/control`, etc.).
- A build recipe (`debian/rules`, etc.).
- Any hooks or scripts needed to integrate with the package manager.

</details>

<details>
<summary><strong>Release process</strong></summary>

### Version Bumping

All version bumps are performed with **bump2version**. The tool updates
`pyproject.toml`, `prez-pkglog.spec`, `CHANGELOG.md`, and any other version
strings, then creates an annotated Git tag.

The `make release v=patch|minor|major` target automates the entire process:
1. Bumps the version using bump2version
2. Stages all modified files
3. Commits the version bump changes
4. Pushes the commit and tags to the remote repository

```bash
# Automated release process (recommended)
make release v=patch|minor|major

# Manual process (alternative)
bump2version patch
git add -A
git commit -m "Bump version to X.Y.Z"
git push && git push --tags
```

### Automated Release Pipeline (GitHub Actions)

When the tag hits GitHub, the **release.yml** workflow performs the heavy
lifting:

1. Builds the sdist, SRPM, and RPM for every enabled Fedora/EPEL target.
2. Runs `rpmlint` and executes the whole pytest suite in the spec's `%check`
   section.
3. Signs the resulting RPMs with the project's GPG key (provided as encrypted
   secrets `GPG_PRIVATE_KEY` + `GPG_PASSPHRASE`).
4. Uploads the SRPM to your Copr project via `copr-cli` using the
   `COPR_LOGIN`/`COPR_TOKEN` secrets.

No manual `rpmbuild` or `copr-cli build` steps are required.

### Preparing the Secrets

Set the following **repository secrets** so the workflow can operate:

| Secret name         | Description                                   |
|---------------------|-----------------------------------------------|
| `GPG_PRIVATE_KEY`   | Base-64-encoded *private* key block            |
| `GPG_PASSPHRASE`    | Passphrase for the key (may be empty)          |
| `COPR_LOGIN`        | Your Copr username                             |
| `COPR_TOKEN`        | API token from the Copr *API* tab              |

> Tip : create a dedicated key used **only** for package signing.

### Manual RPM Builds (optional)

If you still need a local build:

```bash
make rpm         # build SRPM+RPM in ~/rpmbuild
make install     # install the freshly built package
```

Those targets now mimic what the CI does (including running the test-suite via
%check).

### Development Workflow

For day-to-day development:

```bash
# Set up environment
uv sync

# Run tests and quality checks
make test
make lint
make check-format

# Make changes and test

# Before submitting
make format  # Auto-format code
make test    # Ensure tests pass
```

</details>

---

## Getting Help

<details>
<summary><strong>Troubleshooting common issues</strong></summary>

### Common Issues

#### C++ Build Issues
- **Missing libdnf5-devel**: Install with `sudo dnf install libdnf5-devel`
- **CMake not found**: Install with `sudo dnf install cmake`
- **clang-format not found**: Install with `sudo dnf install clang-tools-extra`

#### Python Development Issues
- **Import errors**: Ensure you're in the virtual environment and dependencies are installed
- **Type checking errors**: Run `make mypy` to see specific issues
- **Formatting issues**: Run `make format` to fix automatically
- **Test failures**: Check that all dependencies are installed with `uv sync`

#### Plugin Issues
- **Plugin not loading**: Check that it's installed to `/usr/lib64/dnf5/plugins/`
- **Permission errors**: Ensure you have write access to the log directory

#### Git/Release Issues
- **Version bump fails**: Ensure you're on the main branch and have uncommitted changes
- **Push fails**: Check that you have write access to the repository

#### DNF Integration Issues
- **Actions Plugin not working**: Check that `/usr/share/libdnf5/plugins/actions.d/prez_pkglog.actions` has no trailing characters or extra whitespace
- **Scope detection problems**: Verify that system config at `/etc/prez-pkglog/` takes precedence over user config at `~/.config/prez-pkglog/`
- **Conditional imports failing**: Use `try/except ImportError` patterns and `dnf.Plugin if dnf else object` inheritance
- **Setup command issues**: Ensure Click option decorators are properly mapped to function parameters

</details>

### Getting Help

- Open an issue for bugs or feature requests
- Join discussions for questions
- Check existing issues and pull requests

## Anyone Can Help

I welcome contributors from all backgrounds and experience levels.

---

Thank you for contributing to prez-pkglog
