# TODO List

## Completed

### DNF5 Plugin Implementation
- [x] **Fixed DNF plugin installation path** - Plugin now installs to correct `/usr/lib/python3.13/site-packages/dnf-plugins/` directory
- [x] **Implemented native libdnf5 C++ plugin** - Created `libdnf5-plugin/dnf5-plugin/` directory with CMake build system
- [x] **Fixed CMake build configuration** - Updated to use C++20 standard and proper pkg-config dependencies
- [x] **Fixed plugin interface implementation** - Added all required virtual functions from `IPlugin` interface
- [x] **Fixed RPM build system** - Corrected CMake macros and build directory issues
- [x] **Fixed installation paths** - Plugin now installs to `/usr/lib64/dnf5/plugins/` for native plugin
- [x] **Fixed TypeError in plugin code** - Resolved naming conflict in plugin implementation
- [x] **System-level systemd service** - Systemd service exists in `systemd-user/prez-pkglog.service` and is installed via RPM spec
  - [x] Enhanced with security hardening (ProtectSystem, ProtectHome, PrivateTmp, NoNewPrivileges)
  - [x] Added proper network dependency handling
  - [x] Fixed Documentation field to use URL instead of man page reference

### Documentation and Installation
- [x] **Fix man page installation** - Man page is missing from RPM install
  - [x] Add man page to RPM spec file (`docs/man/prez-pkglog.1` → `%{_mandir}/man1/`)
  - [x] Ensure man page is properly formatted and installed
  - [x] Test man page accessibility

### CLI User Guidence
- [x] **Add post-install messages** - Provide clear instructions after RPM installation
  - [x] Add post-install script to RPM spec
  - [x] Display configuration instructions
  - [x] Show how to enable DNF plugin
  - [x] Provide systemd service setup instructions

### Code Quality and Documentation (Today's Work)
- [x] **Clean up backend code** - Removed unnecessary comments from all backend files
  - [x] Cleaned dnf.py, apt.py, pacman.py, brew.py, chocolatey.py, winget.py
  - [x] Moved detailed setup instructions to CONTRIBUTING.md
  - [x] Maintained focus on DNF backend while providing basic layouts for other backends

- [x] **Enhanced CONTRIBUTING.md** - Restructured documentation for better navigation
  - [x] Added dropdown menus and collapsible sections
  - [x] Added comprehensive backend setup instructions
  - [x] Added pre-submission checklist for contributors
  - [x] Enhanced troubleshooting section with Git/release-specific issues
  - [x] Added development workflow documentation

- [x] **Fixed critical Makefile issue** - Corrected release process
  - [x] Fixed `make release` to properly commit changes before pushing
  - [x] Added proper git workflow with staging, commit, and push
  - [x] Updated documentation to reflect corrected workflow

- [x] **Enhanced GitHub Actions workflow** - Improved CI/CD pipeline
  - [x] Fixed release.yml with proper dependencies and permissions
  - [x] Enhanced security with step-level environment variables
  - [x] Improved error handling and directory management
  - [x] Fixed context access warnings in shell scripts

- [x] **Comprehensive test suite overhaul** - Created robust testing infrastructure
  - [x] Created integration tests for DNF backend (`tests/integration/test_dnf_backend.py`)
  - [x] Enhanced unit tests with proper mocking and fixtures
  - [x] Added new test files for hooks and monitors
  - [x] Fixed test isolation issues with module reloading
  - [x] Resolved import and mocking issues for missing dnf module

- [x] **Backend code improvements** - Enhanced error handling and type safety
  - [x] Fixed DNF backend with proper TYPE_CHECKING imports
  - [x] Added conditional imports and error handling for missing modules
  - [x] Enhanced plugin imports with proper error handling
  - [x] Improved type hints and error messages throughout codebase

- [x] **Updated documentation** - Reflect DNF5 plugin changes
  - [x] Update README.md with DNF5 plugin information
  - [x] Add troubleshooting section for DNF5 vs DNF4
  - [x] Document plugin configuration for both DNF versions
  - [x] Update installation instructions

### Build System Improvements
- [x] **Add development dependencies to RPM spec**
  - [x] Include `libdnf5-devel` and `libdnf5-cli-devel`
  - [x] Add `cmake` and `pkg-config` as build dependencies
  - [x] Consider adding `gcc-c++` explicitly

## Pending Tasks

### CLI and Configuration Improvements
- [x] **Improve CLI defaults** - CLI defaults to user scope even when config is system scope
  - [x] Make CLI respect the configured scope by default instead of hard-coded "user"
  - [ ] Add better error messages when scope mismatch occurs
  - [ ] Consider adding `--auto-detect-scope` option

- [ ] **Add background flag to daemon** - Allow daemon to fork into background when not using systemd
  - [ ] Add `--background` flag to `prez-pkglog daemon` command
  - [ ] Implement background forking logic
  - [ ] Add proper signal handling for background mode

### Testing and Quality Assurance
- [x] **Add integration tests for DNF5 plugin**
  - [x] Test plugin loading in DNF5 environment
  - [x] Test transaction logging functionality
  - [x] Test plugin configuration options
  - [x] Test error handling scenarios

- [x] **Add unit tests for C++ plugin**
  - [x] Test plugin interface implementation
  - [ ] Test build system with different compilers
  - [ ] Test installation paths and permissions

### Package Manager Backends
- [ ] **Implement APT backend hooks**
  - [ ] Create `DPkg::Post-Invoke` script
  - [ ] Add APT configuration examples
  - [ ] Test with Debian/Ubuntu systems

- [ ] **Implement Pacman backend hooks**
  - [ ] Create `/etc/pacman.d/hooks/prez-pkglog.hook`
  - [ ] Implement transaction parsing
  - [ ] Test with Arch Linux systems

- [ ] **Implement Homebrew backend hooks**
  - [ ] Create post-install wrapper or tap
  - [ ] Test with macOS systems

- [ ] **Implement Windows backends**
  - [ ] Chocolatey PowerShell extension
  - [ ] Winget source extension or scheduled task

- [x] **Improve CMake configuration**
  - [ ] Add version compatibility checks
  - [ ] Add better error messages for missing dependencies
  - [ ] Consider adding optional features

### Monitoring and Logging
- [ ] **Enhance download monitoring**
  - [ ] Add file type detection improvements
  - [ ] Add virus scanning integration
  - [ ] Add duplicate file detection
  - [ ] Add file metadata extraction

- [ ] **Improve log querying**
  - [ ] Add more search filters
  - [ ] Add date range queries
  - [ ] Add export format options
  - [ ] Add log rotation support

### Performance and Reliability
- [ ] **Optimize log file handling**
  - [ ] Add log file compression
  - [ ] Add log file rotation
  - [ ] Add backup and recovery features
  - [ ] Add log file integrity checks

- [ ] **Add error recovery**
  - [ ] Handle plugin loading failures gracefully
  - [ ] Add retry mechanisms for failed operations
  - [ ] Add fallback logging mechanisms

## Future Enhancements

### Features
- [ ] **Add web interface**
  - [ ] Simple web dashboard for viewing logs
  - [ ] REST API for log access
  - [ ] Real-time log streaming

- [ ] **Add notification system**
  - [ ] Email notifications for package changes
  - [ ] Desktop notifications
  - [ ] Slack/Discord integration

- [ ] **Add analytics and reporting**
  - [ ] Package usage statistics
  - [ ] System change reports
  - [ ] Dependency analysis

### Cross-Platform Support
- [ ] **Improve Windows support**
  - [ ] Native Windows service
  - [ ] Windows-specific package managers
  - [ ] Windows registry monitoring

- [ ] **Improve macOS support**
  - [ ] Native macOS service
  - [ ] macOS-specific package managers
  - [ ] macOS security considerations

### Integration Features
- [ ] **Add Git integration**
  - [ ] Log git clone operations
  - [ ] Track repository changes
  - [ ] Version control integration

- [ ] **Add container support**
  - [ ] Docker container monitoring
  - [ ] Podman container monitoring
  - [ ] Container image tracking

## Priorities

1. **Medium Priority**: Add `--background` flag to daemon (convenience feature)
2. **Low Priority**: Add better error messages for scope mismatch
3. **Low Priority**: Improve CMake configuration with better error handling
4. **Low Priority**: Complete remaining C++ plugin testing (build system, installation paths)

## Notes

- **Priority**: Focus on CLI improvements and documentation first
- **Testing**: Ensure all changes work with both DNF4 and DNF5
- **Backwards Compatibility**: Maintain support for existing configurations
- **Performance**: Monitor impact on package manager performance 