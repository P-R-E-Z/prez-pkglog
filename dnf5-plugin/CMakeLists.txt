# Minimal CMake script to build dnf5 plugin for prez-pkglog

cmake_minimum_required(VERSION 3.18)

project(prez_pkglog_dnf5_plugin LANGUAGES CXX)

find_package(dnf5 2.0 REQUIRED COMPONENTS cli)
find_package(libdnf5 2.0 REQUIRED)

add_library(prez_pkglog_dnf5_plugin SHARED prez_pkglog_plugin.cpp)

set_target_properties(prez_pkglog_dnf5_plugin PROPERTIES
    PREFIX ""
    CXX_STANDARD 17
    OUTPUT_NAME "prez_pkglog"
)

target_include_directories(prez_pkglog_dnf5_plugin PRIVATE ${dnf5_INCLUDE_DIRS} ${libdnf5_INCLUDE_DIRS})

target_link_libraries(prez_pkglog_dnf5_plugin PRIVATE dnf5 libdnf5)

install(TARGETS prez_pkglog_dnf5_plugin
        LIBRARY DESTINATION ${CMAKE_INSTALL_FULL_LIBDIR}/dnf5/plugins) 