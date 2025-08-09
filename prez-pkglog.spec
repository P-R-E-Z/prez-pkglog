# RpmSpec
Name:    prez-pkglog
Version: 0.6.3
Release: 1%{?dist}
Summary: Cross-platform package installation logger

License:    MIT
URL:        https://github.com/P-R-E-Z/prez-pkglog
Source0:    %{name}-%{version}.tar.gz

# Contains a native C++ plugin (prez_pkglog.so) → package is now arch-specific.
# BuildArch:  noarch

# Python packaging macros + dependencies for building libdnf5 plugin
BuildRequires:  pyproject-rpm-macros
BuildRequires:  cmake gcc-c++ libdnf5-devel
BuildRequires:  pkgconfig(libdnf5) pkgconfig(libdnf5-cli)
## Only need pytest for upstream development; the RPM check phase will just
# verify the package can be imported, so pytest isn’t required as a build dep.
#BuildRequires:  python3dist(pytest)

# Explicit runtime dependencies (until automatic dependency generation is configured)
Requires:  python3dist(appdirs)
Requires:  python3dist(click)
Requires:  python3dist(pydantic) >= 2
Requires:  python3dist(python-dotenv)
Requires:  python3dist(rich)
Requires:  python3dist(toml)
Requires:  python3dist(watchdog)

%global _pyproject_buildrequires_extra python-dnf python-watchdog python-appdirs python-rich python-click python-pydantic python-dotenv python-toml

%description
Prez-Pkglog is a cross-platform tool to log package installations, downloaded files, and removals from various
package managers. This utility is designed to improve system package management.

# Preparation phase
# The Python sdist created by `python -m build` expands into a directory that
# uses an underscore (prez_pkglog-<version>) instead of the hyphenated project
# name.  Tell %autosetup to cd into that directory so %%prep succeeds.
%prep
%autosetup -S git -n prez_pkglog-%{version}
# Convert SPDX string back to table form for older setuptools in system RPM build
sed -i 's/^license = "MIT"/license = { text = "MIT" }/' pyproject.toml

%build
%pyproject_wheel

# Build the native dnf5 plugin (C++/libdnf5)
%cmake -S libdnf5-plugin/dnf5-plugin
%cmake_build

%install
%pyproject_install

# Install the compiled dnf5 plugin
%cmake_install

# Install DNF4 plugin where DNF looks for Python plugins.
#   • %{python3_sitelib}/dnf-plugins/  (e.g. /usr/lib/python3.13/site-packages/dnf-plugins/)
# Using the macro keeps it version-agnostic.
install -D -m 0644 src/prez_pkglog/hooks/dnf/plugin.py \
  %{buildroot}%{python3_sitelib}/dnf-plugins/prez_pkglog.py
install -D -m 0644 config/prez_pkglog.conf %{buildroot}%{_sysconfdir}/dnf/plugins/prez_pkglog.conf

# Install DNF5 plugin configuration
install -D -m 0644 config/prez_pkglog.conf %{buildroot}%{_sysconfdir}/dnf5/plugins/prez_pkglog.conf
# Enable DNF5 Actions plugin
install -D -m 0644 config/dnf5/actions.conf %{buildroot}%{_sysconfdir}/dnf5/plugins/actions.conf

# Install systemd user service
install -D -m 0644 systemd-user/prez-pkglog.service %{buildroot}%{_userunitdir}/prez-pkglog.service

# Install man page
install -D -m 0644 docs/man/prez-pkglog.1 %{buildroot}%{_mandir}/man1/prez-pkglog.1

%check
# Verify the package can be imported by setting PYTHONPATH to include the installed package
PYTHONPATH=%{buildroot}%{python3_sitelib}:$PYTHONPATH %{python3} - << 'PY'
import importlib, sys
try:
    importlib.import_module("prez_pkglog")
    print("Import OK")
except Exception as exc:
    print("Failed to import prez_pkglog:", exc, file=sys.stderr)
    sys.exit(1)
PY

%files
%exclude %{python3_sitelib}/__init__.*
%exclude %{python3_sitelib}/__pycache__/__init__*
%license LICENSE
%doc README.md CONTRIBUTING.md
%{_bindir}/prez-pkglog
%{python3_sitelib}/prez_pkglog/
%{python3_sitelib}/prez_pkglog-%{version}.dist-info/
%{python3_sitelib}/dnf-plugins/prez_pkglog.py
%{python3_sitelib}/dnf-plugins/__pycache__/prez_pkglog.cpython-*.pyc
%{_libdir}/dnf5/plugins/prez_pkglog.so
%{_datadir}/libdnf5/plugins/actions.d/prez_pkglog.actions
%{_sysconfdir}/dnf/plugins/prez_pkglog.conf
%{_sysconfdir}/dnf5/plugins/prez_pkglog.conf
%{_sysconfdir}/dnf5/plugins/actions.conf
%{_userunitdir}/prez-pkglog.service
%{_mandir}/man1/prez-pkglog.1*

%post
echo "=========================================="
echo "prez-pkglog v%{version} installed successfully!"
echo "=========================================="
echo ""
echo "QUICK START:"
echo "1. Setup configuration: prez-pkglog setup"
echo "2. Check status: prez-pkglog status"
echo "3. View manual: man prez-pkglog"
echo ""
echo "DNF PLUGIN SETUP:"
echo "Both DNF4 (Python) and DNF5 (C++) plugins are installed:"
echo ""
echo "DNF4 Plugin (Python):"
echo "  User scope:   echo 'enabled = 1' >> ~/.config/dnf/plugins/prez_pkglog.conf"
echo "  System scope:  echo 'enabled = 1' >> /etc/dnf/plugins/prez_pkglog.conf"
echo ""
echo "DNF5 Plugin (C++ - enabled by default):"
echo "  User scope:   echo 'enabled = 1' >> ~/.config/dnf5/plugins/prez_pkglog.conf"
echo "  System scope:  echo 'enabled = 1' >> /etc/dnf5/plugins/prez_pkglog.conf"
echo ""
echo "DOWNLOAD MONITORING:"
echo "To enable download monitoring (user scope only):"
echo "  systemctl --user daemon-reload"
echo "  systemctl --user enable --now prez-pkglog.service"
echo ""
echo "SCOPE CONFIGURATION:"
echo "Default scope is 'user'. To change to system scope:"
echo "  sudo prez-pkglog setup --scope system"
echo ""
echo "For more information, see: man prez-pkglog"
echo "Documentation: /usr/share/doc/prez-pkglog/"
echo "=========================================="

%postun
echo "prez-pkglog uninstalled successfully."

%changelog
* Fri Jul 18 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.6.3-1
- 0.6.3 upstream release
- Fixed DNF plugin issues and improved package tracking
- Updated release process to sync .spec file version
- Build using %pyproject_wheel
- Include docs, systemd unit, default config via MANIFEST.in
- Exclude top-level __init__ artifacts from package
- Updated license metadata to SPDX format
- Numerous test and feature additions; see upstream CHANGELOG.md

* Fri Jul 11 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.5.0-1
- 0.5.0 upstream release
- Build using %pyproject_wheel
- Include docs, systemd unit, default config via MANIFEST.in
- Exclude top-level __init__ artifacts from package
- Updated license metadata to SPDX format
- Numerous test and feature additions; see upstream CHANGELOG.md

* Tue Jul 01 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.1.0-1
- Initial package
