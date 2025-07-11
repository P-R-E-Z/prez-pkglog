# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-07-11

### Added
- **Query Command**: New `query` command in the CLI to search and filter package logs by name, manager, or date.
- **Backend Restructuring**: Re-architected the backend system to be OS-specific, with packages now organized under `linux/`, `macos/`, and `windows/` directories for clearer separation and future expansion.
- **Dynamic Backend Loading**: Implemented dynamic discovery and loading of all available package manager backends at runtime.
- **Skeleton Backends**: Added skeleton backends for APT, Pacman, Homebrew (macOS), and Chocolatey/Winget (Windows) to guide future contributors.
- **Systemd User Service**: Added a `systemd` user service file to automatically run the downloads monitor on login.
- **Configuration for Downloads Monitor**: The downloads directory and monitored file extensions are now configurable in `prez_pkglog.conf`.
- **Thread/Process Safe Logging**: Implemented atomic writes and locking to prevent log corruption in concurrent scenarios.
- **Configuration Persistence**: Application settings are now saved to `prez_pkglog.conf` automatically.

### Changed
- **CLI Refactoring**: The `install` and `remove` commands were moved from a standalone script into the main `