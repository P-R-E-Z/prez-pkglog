"""Unit tests for the base backend module"""

from unittest.mock import MagicMock
import pytest

from src.prez_pkglog.backends.base import PackageBackend, PackageInfo


class TestPackageInfo:
    """Test the PackageInfo dataclass."""

    def test_package_info_creation(self):
        """Test creating a PackageInfo instance."""
        info = PackageInfo(
            name="test-package",
            version="1.0.0",
            architecture="x86_64",
            installed=True,
            source="test-repo",
        )

        assert info.name == "test-package"
        assert info.version == "1.0.0"
        assert info.architecture == "x86_64"
        assert info.installed is True
        assert info.source == "test-repo"

    def test_package_info_defaults(self):
        """Test PackageInfo with default values."""
        info = PackageInfo(name="test-package", version="1.0.0")

        assert info.name == "test-package"
        assert info.version == "1.0.0"
        assert info.architecture is None
        assert info.installed is False
        assert info.source is None

    def test_package_info_equality(self):
        """Test PackageInfo equality comparison."""
        info1 = PackageInfo(name="pkg", version="1.0.0", architecture="x86_64")
        info2 = PackageInfo(name="pkg", version="1.0.0", architecture="x86_64")
        info3 = PackageInfo(name="pkg", version="2.0.0", architecture="x86_64")

        assert info1 == info2
        assert info1 != info3

    def test_package_info_string_representation(self):
        """Test PackageInfo string representation."""
        info = PackageInfo(name="test-package", version="1.0.0", architecture="x86_64")

        str_repr = str(info)
        assert "test-package" in str_repr
        assert "1.0.0" in str_repr

    def test_package_info_repr(self):
        """Test PackageInfo repr representation."""
        info = PackageInfo(name="test-package", version="1.0.0")

        repr_str = repr(info)
        assert "PackageInfo" in repr_str
        assert "test-package" in repr_str
        assert "1.0.0" in repr_str

    def test_package_info_with_all_fields(self):
        """Test PackageInfo with all fields populated."""
        info = PackageInfo(
            name="complex-package",
            version="2.1.0",
            architecture="aarch64",
            installed=True,
            source="custom-repo",
        )

        assert info.name == "complex-package"
        assert info.version == "2.1.0"
        assert info.architecture == "aarch64"
        assert info.installed is True
        assert info.source == "custom-repo"


class ConcretePackageBackend(PackageBackend):
    """Concrete implementation of PackageBackend for testing."""

    name = "test-backend"

    def __init__(self, config=None):
        super().__init__(config)
        self._available = True

    @classmethod
    def is_available(cls):
        return True

    def get_installed_packages(self):
        return {
            "test-package": PackageInfo(
                name="test-package", version="1.0.0", installed=True
            )
        }

    def register_transaction(self, transaction):
        return True


class TestPackageBackend:
    """Test the PackageBackend base class."""

    def test_package_backend_initialization(self):
        """Test PackageBackend initialization."""
        backend = ConcretePackageBackend()

        assert backend.name == "test-backend"
        assert backend.config is None

    def test_package_backend_with_config(self):
        """Test PackageBackend initialization with config."""
        mock_config = MagicMock()
        backend = ConcretePackageBackend(config=mock_config)

        assert backend.config is mock_config

    def test_package_backend_is_abstract(self):
        """Test that PackageBackend cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            PackageBackend()  # type: ignore

    def test_concrete_backend_implements_abstract_methods(self):
        """Test that concrete backend implements all abstract methods."""
        backend = ConcretePackageBackend()

        # Test is_available class method
        assert backend.is_available() is True

        # Test get_installed_packages method
        packages = backend.get_installed_packages()
        assert isinstance(packages, dict)
        assert "test-package" in packages

        # Test register_transaction method
        result = backend.register_transaction(None)
        assert result is True

    def test_package_backend_name_attribute(self):
        """Test that PackageBackend has a name attribute."""
        backend = ConcretePackageBackend()
        assert hasattr(backend, "name")
        assert backend.name == "test-backend"

    def test_package_backend_subclass_requirements(self):
        """Test that PackageBackend subclasses must implement required methods."""

        class IncompleteBackend(PackageBackend):
            name = "incomplete"

            @classmethod
            def is_available(cls):
                return True

            # Missing get_installed_packages and register_transaction

        # Should raise TypeError when trying to instantiate
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteBackend()  # type: ignore

    def test_package_backend_get_installed_packages_return_type(self):
        """Test that get_installed_packages returns correct type."""
        backend = ConcretePackageBackend()
        packages = backend.get_installed_packages()

        assert isinstance(packages, dict)
        for name, info in packages.items():
            assert isinstance(name, str)
            assert isinstance(info, PackageInfo)

    def test_package_backend_register_transaction_return_type(self):
        """Test that register_transaction returns boolean."""
        backend = ConcretePackageBackend()
        result = backend.register_transaction(None)

        assert isinstance(result, bool)

    def test_package_backend_is_available_class_method(self):
        """Test that is_available is a class method."""
        # Can be called on class
        assert ConcretePackageBackend.is_available() is True

        # Can be called on instance
        backend = ConcretePackageBackend()
        assert backend.is_available() is True

    def test_package_backend_inheritance_chain(self):
        """Test PackageBackend inheritance chain."""
        backend = ConcretePackageBackend()

        assert isinstance(backend, PackageBackend)
        assert isinstance(backend, ConcretePackageBackend)
        assert issubclass(ConcretePackageBackend, PackageBackend)

    def test_package_backend_config_handling(self):
        """Test PackageBackend config handling."""
        # Test with None config
        backend1 = ConcretePackageBackend(config=None)
        assert backend1.config is None

        # Test with mock config
        mock_config = MagicMock()
        mock_config.get.return_value = "test_value"
        backend2 = ConcretePackageBackend(config=mock_config)
        assert backend2.config is mock_config

    def test_package_backend_multiple_instances(self):
        """Test that multiple PackageBackend instances are independent."""
        config1 = MagicMock()
        config2 = MagicMock()

        backend1 = ConcretePackageBackend(config=config1)
        backend2 = ConcretePackageBackend(config=config2)

        assert backend1.config is config1
        assert backend2.config is config2
        assert backend1 is not backend2

    def test_package_backend_method_signatures(self):
        """Test that abstract methods have correct signatures."""
        backend = ConcretePackageBackend()

        # Test method signatures exist and are callable
        assert callable(backend.is_available)
        assert callable(backend.get_installed_packages)
        assert callable(backend.register_transaction)

    def test_package_backend_with_custom_name(self):
        """Test PackageBackend with custom name."""

        class CustomBackend(PackageBackend):
            name = "custom-manager"

            @classmethod
            def is_available(cls):
                return False

            def get_installed_packages(self):
                return {}

            def register_transaction(self, transaction):
                return False

        backend = CustomBackend()
        assert backend.name == "custom-manager"
        assert backend.is_available() is False
        assert backend.get_installed_packages() == {}
        assert backend.register_transaction(None) is False

    def test_package_backend_error_handling(self):
        """Test PackageBackend error handling in concrete implementation."""

        class ErrorBackend(PackageBackend):
            name = "error-backend"

            @classmethod
            def is_available(cls):
                return True

            def get_installed_packages(self):
                raise Exception("Test error")

            def register_transaction(self, transaction):
                raise Exception("Transaction error")

        backend = ErrorBackend()

        # These should raise exceptions as implemented
        with pytest.raises(Exception, match="Test error"):
            backend.get_installed_packages()

        with pytest.raises(Exception, match="Transaction error"):
            backend.register_transaction(None)

    def test_package_backend_documentation(self):
        """Test that PackageBackend has proper documentation."""
        assert PackageBackend.__doc__ is not None
        assert (
            "Abstract base class" in PackageBackend.__doc__
            or "Base class" in PackageBackend.__doc__
        )
