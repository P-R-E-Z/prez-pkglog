# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.4] - 2025-07-23

### Note From Prez
This is my first DNF plugin and my first time using C++ for this type of programming, due to not thoroughly reading the
DNF5 Docs I missed some key information that resulted in the plugin to only somewhat work. Due to this I did a bunch of
fixes and code changes as I learned more about DNF plugin development hence the jumps in versions within this doc as I made
learning and testing a priority and skipped a lot of documenting. As of right now, DNF4 and DNF5 plugin functionality works
out-of-box. The following updates will be knocking out some TODO's for the DNF plugin and getting Windows functionality, as well as cleaning up the folder structure.  

### Fixed
- **DNF5 Actions Plugin**: Fixed trailing character issue in actions file that prevented transaction logging
- **Scope Detection**: Fixed `sudo prez-pkglog setup` to correctly detect and configure system scope
- **Configuration Priority**: System config now properly overrides user config when both exist
- **DNF4 Plugin**: Fixed conditional import handling and plugin inheritance for better compatibility
- **CLI Setup Command**: Fixed duplicate decorator and parameter mapping issues
- **Scope**: Consistent configuration precedence and scope persistence across commands

### Changed
- **DNF5 Plugin**: Simplified C++ plugin to minimal implementation, relying on Actions Plugin for transaction logging
- **Scope Management**: Improved logic to ensure single source of truth for active scope configuration
- **Config File Location**: Enhanced automatic detection of system vs user configuration files
- **Release Process**: Improved Makefile to automatically update spec file version during releases
- **DNF5 Actions Plugin**: Updated to call CLI with `--scope system` ensuring logs go to `/var/log/prez-pkglog`
- **CLI**: Defaults to system scope when run as root; falls back to user scope if non-root requests system
- **Documentation updated**: Config examples now use JSON and hyphenated file names (`prez-pkglog.conf`)
- **Build/CI/docs** Paths updated to `libdnf5-plugin/dnf5-plugin/`

### Added
- **Debug Output**: Enhanced plugin initialization messages for better troubleshooting
- **DNF5 Actions Plugin** config installed to `/etc/dnf5/plugins/actions.conf` (enabled by default)

## [0.5.0] - 2025-07-11

### Packaging

- **Fixed** PEP 625 underscore tarball naming in Makefile
- **Added** MANIFEST.in so LICENSE, docs, systemd unit, default config are shipped
- **Spec**: %pyproject_wheel, excluded stray __init__.py*, RPM now builds cleanly
- **Wheel + sdist** now built by default via `make build`

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

## [0.6.0] - 2025-07-13

### Added
- **Automatic Release Workflow**: New `.github/workflows/release.yml` builds the sdist/SRPM & RPM, runs the full test suite with `%pytest`, signs the binaries with your GPG key, and uploads the SRPM to Copr when a version tag is pushed.
- **Parsing Helper**: Introduced `parse_pacman_query_line()` in `src/prez_pkglog/backends/helpers.py` for robust Pacman output parsing.
- **Spec Tests**: Added `%check` section to `prez-pkglog.spec` so the RPM build runs `pytest` automatically.

### Changed
- **Pacman Backend** now uses the new parsing helper and gracefully skips malformed lines.
- **RPM Spec** updated to use `%autosetup -S git -n %{name}-%{version}`, added `BuildRequires: python3dist(pytest)`, and switched `Source0` macro to `%{name}-%{version}.tar.gz`.

### Fixed
- Minor packaging clean-ups and logging improvements discovered during the refactor.

[0.5.3]: https://github.com/P-R-E-Z/prez-pkglog/releases/tag/v0.5.3