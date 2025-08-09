cmake_minimum_required(VERSION 3.18)

project(prez_pkglog_dnf5_plugin LANGUAGES CXX)

include(GNUInstallDirs)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBDNF5 REQUIRED libdnf5)
pkg_check_modules(LIBDNF5_CLI REQUIRED libdnf5-cli)

add_library(prez_pkglog_dnf5_plugin SHARED src/prez_pkglog_plugin.cpp)

set_target_properties(prez_pkglog_dnf5_plugin PROPERTIES
    PREFIX ""
    CXX_STANDARD 20
    OUTPUT_NAME "prez_pkglog"
)

target_include_directories(prez_pkglog_dnf5_plugin PRIVATE ${LIBDNF5_INCLUDE_DIRS})

target_link_libraries(prez_pkglog_dnf5_plugin PRIVATE ${LIBDNF5_CLI_LIBRARIES} ${LIBDNF5_LIBRARIES})

install(TARGETS prez_pkglog_dnf5_plugin
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/dnf5/plugins)

install(FILES actions.d/prez_pkglog.actions
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/libdnf5/plugins/actions.d) 