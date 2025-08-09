%package -n prez-pkglog-libdnf5
Summary: DNF5 native plugin for prez-pkglog
Requires: prez-pkglog >= %{version}

%description -n prez-pkglog-libdnf5
Native libdnf5 plugin that forwards DNF5 transactions to prez-pkglog.

%install
%cmake --preset release libdnf5-plugin
%cmake --build build
%cmake_install
