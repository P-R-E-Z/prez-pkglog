# RpmSpec
%global python_version 3.13
%global plugin_name prez-pkglog

Name:    prez_pkglog
Version: 0.1.0
Release: 1%{?dist}
Summary: Cross-platform package installation logger

# License information
License:    MIT
URL:        https://github.com/P-R-E-Z/prez-pkglog
Source0:    prez_pkglog-0.1.0.tar.gz

# Build architecture
BuildArch:  noarch
BuildRequires:  python%{python_version}-devel

# Runtime Dependencies
Requires:       python%{python_version}-dnf
Requires:       python%{python_version}-watchdog
Requires:       python%{python_version}-appdirs
Requires:       python%{python_version}-rich

Requires(post): python%{python_version}
Requires(postun): python%{python_version}

%description
Prez-Pkglog is a cross-platform tool to log package installations, downloaded files, and removals from various
package managers. This utility is designed to improve system package management.

%prep
%autosetup -n prez_pkglog-0.1.0

%build
uv build --output-dir dist

%install
uv install --wheel-dir dist --destdir %{buildroot}

# Install DNF plugin
install -D -m 0644 prez_pkglogger.py %{buildroot}%{_libdir}/dnf-plugins/%{plugin_name}.py
install -D -m 0644 prez_pkglogger.conf %{buildroot}%{_sysconfdir}/dnf/plugins/%{plugin_name}.conf

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/prez_pkglog
%{python3_sitelib}/prez_pkglog-*.dist-info
%{_bindir}/prez-pkglog
%{_libdir}/dnf-plugins/%{plugin_name}.py
%{_sysconfdir}/dnf/plugins/%{plugin_name}.conf

%post
echo "prez-pkglog installed successfully. Refer to the README.md for usage instructions."

%postun
echo "prez-pkglog uninstalled successfully."

%changelog
* Tue Jul 01 2025 Prez <154857421+P-R-E-Z@users.noreply.github.com> - 0.1.0-1
- Initial package
