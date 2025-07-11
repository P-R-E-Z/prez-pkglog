"""Unit tests for the backend discovery system"""

from unittest.mock import patch, MagicMock
import pytest

from src.prez_pkglog.backends.base import PackageBackend
from src.prez_pkglog import backends
from src.prez_pkglog import (
    register_backend,
    get_backend,
    detect_available_backends,
    _BACKENDS,
)


class TestBackendDiscovery:
    """Test the dynamic backend discovery system."""

    def test_discovered_backends_exist(self):
        """Test that discovered_backends dictionary exists and has backends."""
        assert hasattr(backends, 'discovered_backends')
        assert isinstance(backends.discovered_backends, dict)
        
        # Should have discovered some backends
        assert len(backends.discovered_backends) > 0

    def test_discovered_backends_contain_expected_backends(self):
        """Test that expected backends are discovered."""
        expected_backends = {'apt', 'dnf', 'pacman', 'brew', 'chocolatey', 'winget'}
        discovered_names = set(backends.discovered_backends.keys())
        
        # All expected backends should be discovered
        assert expected_backends.issubset(discovered_names)

    def test_discovered_backends_are_backend_classes(self):
        """Test that discovered backends are PackageBackend subclasses."""
        for name, backend_class in backends.discovered_backends.items():
            assert isinstance(backend_class, type)
            assert issubclass(backend_class, PackageBackend)
            assert hasattr(backend_class, 'name')
            assert backend_class.name == name  # type: ignore

    def test_discovered_backends_have_required_methods(self):
        """Test that discovered backends implement required abstract methods."""
        for name, backend_class in backends.discovered_backends.items():
            # Check that class has required methods
            assert hasattr(backend_class, 'is_available')
            assert hasattr(backend_class, 'get_installed_packages')
            assert hasattr(backend_class, 'register_transaction')
            
            # Check that methods are callable
            assert callable(backend_class.is_available)
            
            # For instance methods, we need to check they exist on the class
            assert callable(getattr(backend_class, 'get_installed_packages'))
            assert callable(getattr(backend_class, 'register_transaction'))

    def test_no_duplicate_backend_names(self):
        """Test that there are no duplicate backend names."""
        names = list(backends.discovered_backends.keys())
        unique_names = set(names)
        
        assert len(names) == len(unique_names)

    def test_backend_discovery_by_os(self):
        """Test that backends are organized by OS."""
        linux_backends = {'apt', 'dnf', 'pacman'}
        macos_backends = {'brew'}
        windows_backends = {'chocolatey', 'winget'}
        
        discovered_names = set(backends.discovered_backends.keys())
        
        # Check that we have backends from each OS
        assert linux_backends.intersection(discovered_names)
        assert macos_backends.intersection(discovered_names)
        assert windows_backends.intersection(discovered_names)


class TestBackendRegistration:
    """Test the backend registration system."""

    def setup_method(self):
        """Set up test fixtures."""
        # Store original backends to restore later
        self.original_backends = _BACKENDS.copy()

    def teardown_method(self):
        """Clean up after tests."""
        # Restore original backends
        _BACKENDS.clear()
        _BACKENDS.update(self.original_backends)

    def test_register_backend_success(self):
        """Test successful backend registration."""
        class TestBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("test-backend", TestBackend)
        
        assert "test-backend" in _BACKENDS
        assert _BACKENDS["test-backend"] is TestBackend

    def test_register_backend_overwrites_existing(self):
        """Test that registering a backend overwrites existing one."""
        class FirstBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {"first": "backend"}
            
            def register_transaction(self, transaction):
                return True
        
        class SecondBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {"second": "backend"}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("test-backend", FirstBackend)
        register_backend("test-backend", SecondBackend)
        
        assert _BACKENDS["test-backend"] is SecondBackend

    def test_register_backend_with_different_names(self):
        """Test registering multiple backends with different names."""
        class Backend1(PackageBackend):
            name = "backend1"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        class Backend2(PackageBackend):
            name = "backend2"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("backend1", Backend1)
        register_backend("backend2", Backend2)
        
        assert "backend1" in _BACKENDS
        assert "backend2" in _BACKENDS
        assert _BACKENDS["backend1"] is Backend1
        assert _BACKENDS["backend2"] is Backend2


class TestGetBackend:
    """Test the get_backend function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Store original backends to restore later
        self.original_backends = _BACKENDS.copy()

    def teardown_method(self):
        """Clean up after tests."""
        # Restore original backends
        _BACKENDS.clear()
        _BACKENDS.update(self.original_backends)

    def test_get_backend_existing(self):
        """Test getting an existing backend."""
        class TestBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("test-backend", TestBackend)
        
        backend = get_backend("test-backend")
        
        assert backend is not None
        assert isinstance(backend, TestBackend)

    def test_get_backend_nonexistent(self):
        """Test getting a non-existent backend."""
        backend = get_backend("nonexistent-backend")
        
        assert backend is None

    def test_get_backend_none_name(self):
        """Test getting backend with None name."""
        backend = get_backend(None)
        
        assert backend is None

    def test_get_backend_case_insensitive(self):
        """Test that backend lookup is case insensitive."""
        class TestBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("test-backend", TestBackend)
        
        # Test different cases
        backend1 = get_backend("test-backend")
        backend2 = get_backend("TEST-BACKEND")
        backend3 = get_backend("Test-Backend")
        
        assert backend1 is not None
        assert backend2 is not None
        assert backend3 is not None
        assert isinstance(backend1, TestBackend)
        assert isinstance(backend2, TestBackend)
        assert isinstance(backend3, TestBackend)

    def test_get_backend_returns_new_instance(self):
        """Test that get_backend returns new instances."""
        class TestBackend(PackageBackend):
            name = "test-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        register_backend("test-backend", TestBackend)
        
        backend1 = get_backend("test-backend")
        backend2 = get_backend("test-backend")
        
        assert backend1 is not None
        assert backend2 is not None
        assert backend1 is not backend2  # Different instances


class TestDetectAvailableBackends:
    """Test the detect_available_backends function."""

    def setup_method(self):
        """Set up test fixtures."""
        # Store original backends to restore later
        self.original_backends = _BACKENDS.copy()

    def teardown_method(self):
        """Clean up after tests."""
        # Restore original backends
        _BACKENDS.clear()
        _BACKENDS.update(self.original_backends)

    def test_detect_available_backends_empty(self):
        """Test detecting available backends when none are available."""
        class UnavailableBackend(PackageBackend):
            name = "unavailable-backend"
            
            @classmethod
            def is_available(cls):
                return False
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        _BACKENDS.clear()
        register_backend("unavailable-backend", UnavailableBackend)
        
        available = detect_available_backends()
        
        assert isinstance(available, dict)
        assert len(available) == 0

    def test_detect_available_backends_some_available(self):
        """Test detecting available backends when some are available."""
        class AvailableBackend(PackageBackend):
            name = "available-backend"
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        class UnavailableBackend(PackageBackend):
            name = "unavailable-backend"
            
            @classmethod
            def is_available(cls):
                return False
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        _BACKENDS.clear()
        register_backend("available-backend", AvailableBackend)
        register_backend("unavailable-backend", UnavailableBackend)
        
        available = detect_available_backends()
        
        assert isinstance(available, dict)
        assert len(available) == 1
        assert "available-backend" in available
        assert "unavailable-backend" not in available
        assert isinstance(available["available-backend"], AvailableBackend)

    def test_detect_available_backends_with_config(self):
        """Test detecting available backends with config parameter."""
        class ConfigurableBackend(PackageBackend):
            name = "configurable-backend"
            
            def __init__(self, config=None):
                super().__init__(config)
                self.test_config = config
            
            @classmethod
            def is_available(cls):
                return True
            
            def get_installed_packages(self):
                return {}
            
            def register_transaction(self, transaction):
                return True
        
        _BACKENDS.clear()
        register_backend("configurable-backend", ConfigurableBackend)
        
        mock_config = MagicMock()
        available = detect_available_backends(config=mock_config)
        
        assert len(available) == 1
        backend = available["configurable-backend"]
        assert backend.test_config is mock_config  # type: ignore

    def test_detect_available_backends_return_type(self):
        """Test that detect_available_backends returns correct type."""
        available = detect_available_backends()
        
        assert isinstance(available, dict)
        
        # All values should be PackageBackend instances
        for name, backend in available.items():
            assert isinstance(name, str)
            assert isinstance(backend, PackageBackend)


class TestBackendDiscoveryIntegration:
    """Integration tests for the backend discovery system."""

    def test_main_module_has_backends_registered(self):
        """Test that the main module has backends registered from discovery."""
        # This tests the actual registration that happens during import
        assert len(_BACKENDS) > 0
        
        # Should have the backends we expect
        expected_backends = {'apt', 'dnf', 'pacman', 'brew', 'chocolatey', 'winget'}
        registered_names = set(_BACKENDS.keys())
        
        assert expected_backends.issubset(registered_names)

    def test_get_backend_works_with_discovered_backends(self):
        """Test that get_backend works with actually discovered backends."""
        # Test with a backend we know should be discovered
        dnf_backend = get_backend("dnf")
        
        assert dnf_backend is not None
        assert dnf_backend.name == "dnf"  # type: ignore

    def test_detect_available_backends_with_real_backends(self):
        """Test detect_available_backends with real discovered backends."""
        # This will use the actual backend availability
        available = detect_available_backends()
        
        assert isinstance(available, dict)
        
        # All returned backends should be available
        for name, backend in available.items():
            assert backend.is_available() is True

    def test_backend_discovery_module_exports(self):
        """Test that the backends module exports what we expect."""
        assert hasattr(backends, 'discovered_backends')
        assert hasattr(backends, 'PackageBackend')
        
        # Check __all__ if it exists
        if hasattr(backends, '__all__'):
            assert 'PackageBackend' in backends.__all__
            assert 'discovered_backends' in backends.__all__ 