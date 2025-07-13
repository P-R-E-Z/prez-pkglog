# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

## [0.5.4] - 2025-07-13

### Added
- **Automatic Release Workflow**: New `.github/workflows/release.yml` builds the sdist/SRPM & RPM, runs the full test suite with `%pytest`, signs the binaries with your GPG key, and uploads the SRPM to Copr when a version tag is pushed.
- **Parsing Helper**: Introduced `parse_pacman_query_line()` in `src/prez_pkglog/backends/helpers.py` for robust Pacman output parsing.
- **Spec Tests**: Added `%check` section to `prez-pkglog.spec` so the RPM build runs `pytest` automatically.

### Changed
- **Pacman Backend** now uses the new parsing helper and gracefully skips malformed lines.
- **RPM Spec** updated to use `%autosetup -S git -n %{name}-%{version}`, added `BuildRequires: python3dist(pytest)`, and switched `Source0` macro to `%{name}-%{version}.tar.gz`.
- **Release Process** documented in *Contributing* – tagging via `bump2version` triggers the GitHub release pipeline; no more manual `make rpm && copr-cli`.

### Fixed
- Minor packaging clean-ups and logging improvements discovered during the refactor.

[0.5.3]: https://github.com/P-R-E-Z/prez-pkglog/releases/tag/v0.5.3