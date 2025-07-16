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

# Dependencies for building the libdnf5 C++ plugin
BuildRequires:  cmake gcc-c++ libdnf5-devel dnf5-devel
## Only need pytest for upstream development; the RPM check phase will just
# verify the package can be imported, so pytest isn’t required as a build dep.
#BuildRequires:  python3dist(pytest)

# Explicit runtime dependencies (until automatic dependency generation is configured)
Requires:  python3dist(appdirs)
Requires:  python3dist(pydantic) >= 2
Requires:  python3dist(python-dotenv)
Requires:  python3dist(rich)
Requires:  python3dist(typer)
Requires:  python3dist(watchdog)

%global _pyproject_buildrequires_extra python-dnf python-watchdog python-appdirs python-rich python-typer python-pydantic python-dotenv python-toml

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

# ---------------------------------------------------------------------------
# Build the native dnf5 plugin (C++/libdnf5)
# ---------------------------------------------------------------------------
%cmake -B build_dnf5_plugin -S dnf5-plugin
%cmake_build --builddir build_dnf5_plugin

%install
%pyproject_install

# Install the compiled dnf5 plugin
%cmake_install --builddir build_dnf5_plugin

# Test suite
%check
# Verify the package can be imported with the system Python.
%{python3} - << 'PY'
import importlib, sys
try:
    importlib.import_module("prez_pkglog")
except Exception as exc:
    print("Failed to import prez_pkglog:", exc, file=sys.stderr)
    sys.exit(1)
print("Import OK")
PY

# Install DNF plugin where DNF looks for Python plugins.
#   • %{python3_sitelib}/dnf-plugins/  (e.g. /usr/lib/python3.13/site-packages/dnf-plugins/)
# Using the macro keeps it version-agnostic.
install -D -m 0644 src/prez_pkglog/hooks/dnf/plugin.py \
  %{buildroot}%{python3_sitelib}/dnf-plugins/prez_pkglog.py
install -D -m 0644 config/prez_pkglog.conf %{buildroot}%{_sysconfdir}/dnf/plugins/prez_pkglog.conf

# Install systemd user service
install -D -m 0644 systemd-user/prez-pkglog.service %{buildroot}%{_userunitdir}/prez-pkglog.service

%files
%exclude %{python3_sitelib}/__init__.*
%exclude %{python3_sitelib}/__pycache__/__init__*
%license LICENSE
%doc README.md CONTRIBUTING.md
%{_bindir}/prez-pkglog
%{python3_sitelib}/prez_pkglog/
%{python3_sitelib}/prez_pkglog-%{version}.dist-info/
%{python3_sitelib}/dnf-plugins/prez_pkglog.py
%{_libdir}/dnf5/plugins/prez_pkglog.so
%{_sysconfdir}/dnf/plugins/prez_pkglog.conf
%{_userunitdir}/prez-pkglog.service

%post
echo "prez-pkglog installed successfully. Refer to the README.md for usage instructions."

%postun
echo "prez-pkglog uninstalled successfully."

%changelog
* Fri Jul 11 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.5.0-1
- 0.5.0 upstream release
- Build using %pyproject_wheel
- Include docs, systemd unit, default config via MANIFEST.in
- Exclude top-level __init__ artifacts from package
- Updated license metadata to SPDX format
- Numerous test and feature additions; see upstream CHANGELOG.md

* Tue Jul 01 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.1.0-1
- Initial package
