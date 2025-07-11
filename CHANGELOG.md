# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-07-16

### Added
- **Query Command**: New `query` command in the CLI to search and filter package logs by name, manager, or date.
- **Backend Restructuring**: Re-architected the backend system to be OS-specific, with packages now organized under `linux/`, `macos/`, and `windows/` directories for clearer separation and future expansion.
- **Dynamic Backend Loading**: Implemented dynamic discovery and loading of all available package manager backends at runtime.
- **Skeleton Backends**: Added skeleton backends for APT, Pacman, Homebrew (macOS), and Chocolatey/Winget (Windows) to guide future contributors.
- **Systemd User Service**: Added a `systemd` user service file to automatically run the downloads monitor on login.
- **Configuration for Downloads Monitor**: The downloads directory and monitored file extensions are now configurable in `prez_pkglog.conf`.

### Changed
- **CLI Refactoring**: The `install` and `remove` commands were moved from a standalone script into the main `click`-based CLI for a unified user experience.
- **DNF Backend uses Python API**: The DNF backend was refactored to use the native `dnf` Python API instead of `subprocess` calls, improving performance and reliability.
- **DNF Plugin Integration**: The DNF plugin now integrates directly with the application's logger via Python imports instead of a `subprocess` call, making it more efficient.
- **Standardized Logging**: Replaced all `print()` statements throughout the codebase with the standard `logging` module for consistent and configurable output.
- **RPM Spec File**: Overhauled `prez-pkglog.spec` to use `pyproject-rpm-macros`, which automates dependency handling and follows current Fedora packaging best practices.
- **Makefile**: Significantly improved the `Makefile` for a more robust and portable RPM build process, dynamically locating `rpmbuild` directories and streamlining targets.
- **Sudo Checks**: Refactored repetitive `sudo` permission checks in the CLI into a reusable decorator.

### Fixed
- **Systemd Service Configuration**: Corrected the `prez-pkglog.service` to function correctly as a user-level service instead of a system-wide one.
- **Hardcoded Paths**: Removed hardcoded paths from the `Makefile` in favor of dynamic discovery.
- **Build Process**: Fixed inconsistencies in the build process that would cause `rpmbuild` to fail.
