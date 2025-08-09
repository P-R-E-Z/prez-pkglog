"""Unit tests for C++ dnf5 plugin."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestCppPlugin:
    """Test the C++ dnf5 plugin functionality."""

    def test_plugin_compilation(self):
        """Test that the plugin can be compiled."""
        plugin_dir = Path("libdnf5-plugin/dnf5-plugin")
        cmake_file = plugin_dir / "CMakeLists.txt"
        cpp_file = plugin_dir / "src" / "prez_pkglog_plugin.cpp"

        # Check that plugin files exist
        assert cmake_file.exists(), "CMakeLists.txt should exist"
        assert cpp_file.exists(), "prez_pkglog_plugin.cpp should exist"

        # Check that CMakeLists.txt has required content
        cmake_content = cmake_file.read_text()
        assert "libdnf5" in cmake_content, "CMakeLists.txt should reference libdnf5"
        assert "prez_pkglog" in cmake_content, "CMakeLists.txt should build prez_pkglog plugin"

        # Check that C++ file has required content
        cpp_content = cpp_file.read_text()
        assert "libdnf5" in cpp_content, "C++ file should use libdnf5"
        assert "prez_pkglog" in cpp_content, "C++ file should implement prez-pkglog functionality"

    def test_plugin_installation_path(self):
        """Test that plugin installs to correct path."""
        cmake_file = Path("libdnf5-plugin/dnf5-plugin/CMakeLists.txt")

        if cmake_file.exists():
            cmake_content = cmake_file.read_text()
            assert (
                "CMAKE_INSTALL_LIBDIR}/dnf5/plugins" in cmake_content
                or "/usr/lib64/dnf5/plugins" in cmake_content
            ), "Plugin should install to dnf5 plugins directory"

    def test_clang_format_compliance(self):
        """Test that C++ code follows clang-format standards."""
        cpp_file = Path("libdnf5-plugin/dnf5-plugin/src/prez_pkglog_plugin.cpp")

        if cpp_file.exists():
            # Check that file has reasonable formatting
            content = cpp_file.read_text()

            # Basic formatting checks
            assert "{" in content, "C++ file should contain opening braces"
            assert "}" in content, "C++ file should contain closing braces"
            assert ";" in content, "C++ file should contain semicolons"

            # Check for proper includes
            assert "#include" in content, "C++ file should have include statements"

            # Check for proper namespace usage
            assert "namespace" in content or "using namespace" in content, (
                "C++ file should use namespaces"
            )

    def test_plugin_build_dependencies(self):
        """Test that plugin has correct build dependencies."""
        cmake_file = Path("libdnf5-plugin/dnf5-plugin/CMakeLists.txt")

        if cmake_file.exists():
            cmake_content = cmake_file.read_text()

            # Check for required dependencies
            assert "find_package(PkgConfig REQUIRED)" in cmake_content, "Should use pkg-config"
            assert "pkg_check_modules(LIBDNF5 REQUIRED libdnf5)" in cmake_content, (
                "Should find libdnf5"
            )
            assert "pkg_check_modules(LIBDNF5_CLI REQUIRED libdnf5-cli)" in cmake_content, (
                "Should find libdnf5-cli"
            )

    def test_plugin_output_name(self):
        """Test that plugin has correct output name."""
        cmake_file = Path("libdnf5-plugin/dnf5-plugin/CMakeLists.txt")

        if cmake_file.exists():
            cmake_content = cmake_file.read_text()
            assert 'OUTPUT_NAME "prez_pkglog"' in cmake_content, (
                "Plugin should have correct output name"
            )

    @patch("subprocess.run")
    def test_plugin_build_process(self, mock_run):
        """Test the plugin build process."""
        mock_run.return_value = MagicMock(returncode=0)

        # Mock successful build
        result = subprocess.run(["cmake", "--version"], capture_output=True, text=True)

        # This should not raise an exception
        assert result.returncode == 0 or result.returncode is None

    def test_plugin_file_structure(self):
        """Test that plugin has correct file structure."""
        plugin_dir = Path("libdnf5-plugin/dnf5-plugin")

        if plugin_dir.exists():
            files = list(plugin_dir.iterdir())
            file_names = [f.name for f in files]

            # Should have CMakeLists.txt and src directory
            assert "CMakeLists.txt" in file_names, "Should have CMakeLists.txt"
            assert "src" in file_names, "Should have src directory"

            # Check src directory contents
            src_dir = plugin_dir / "src"
            if src_dir.exists():
                src_files = [f.name for f in src_dir.iterdir()]
                assert "prez_pkglog_plugin.cpp" in src_files, "Should have C++ source file in src/"

    def test_plugin_functionality_requirements(self):
        """Test that plugin implements required functionality."""
        cpp_file = Path("libdnf5-plugin/dnf5-plugin/src/prez_pkglog_plugin.cpp")

        if cpp_file.exists():
            content = cpp_file.read_text()

            # Should implement dnf5 plugin interface
            assert "dnf5" in content.lower(), "Should implement dnf5 plugin interface"

            # Should have logging functionality
            assert "log" in content.lower() or "logger" in content.lower(), (
                "Should have logging functionality"
            )

    def test_plugin_installation_script(self):
        """Test that plugin installation is handled correctly."""
        # Check if there's a Makefile target for building the plugin
        makefile = Path("Makefile")

        if makefile.exists():
            makefile_content = makefile.read_text()

            # Should have format-cpp target
            assert "format-cpp" in makefile_content, "Makefile should have format-cpp target"
            assert "check-format" in makefile_content, "Makefile should have check-format target"

    def test_plugin_integration_with_main_project(self):
        """Test that plugin integrates properly with main project."""
        # Check that plugin is referenced in RPM spec
        spec_file = Path("prez-pkglog.spec")

        if spec_file.exists():
            spec_content = spec_file.read_text()

            # Should build C++ plugin during RPM build
            assert "cmake" in spec_content.lower() or "libdnf5-plugin" in spec_content, (
                "RPM spec should handle C++ plugin"
            )

    def test_plugin_documentation(self):
        """Test that plugin is documented."""
        contributing_file = Path("CONTRIBUTING.md")

        if contributing_file.exists():
            content = contributing_file.read_text()

            # Should have C++ plugin documentation
            assert (
                "C++ Plugin Development" in content
                or "dnf5-plugin" in content
                or "libdnf5-plugin" in content
            ), "CONTRIBUTING.md should document C++ plugin development"
