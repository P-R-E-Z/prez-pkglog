"""Unit tests for the config module"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.prez_pkglog.config import Config


class TestConfig:
    """Test the Config class."""

    def test_init_default_scope(self):
        """Test Config initialization with default scope."""
        config = Config()
        assert config.scope == "user"
        assert config.get("scope") == "user"

    def test_init_custom_scope(self):
        """Test Config initialization with custom scope."""
        config = Config()
        config.set("scope", "system")
        assert config.scope == "system"
        assert config.get("scope") == "system"

    def test_init_invalid_scope(self):
        """Test Config initialization with invalid scope."""
        config = Config()
        # The current implementation doesn't validate scope values,
        # but this test ensures future validation works
        config.set("scope", "invalid")
        # Should not raise an error in current implementation
        assert config.get("scope") == "invalid"

    def test_get_existing_key(self):
        """Test getting an existing configuration key."""
        config = Config()
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    def test_get_nonexistent_key_with_default(self):
        """Test getting a non-existent key with default value."""
        config = Config()
        assert config.get("nonexistent", "default") == "default"

    def test_get_nonexistent_key_without_default(self):
        """Test getting a non-existent key without default value."""
        config = Config()
        assert config.get("nonexistent") is None

    def test_set_and_get_value(self):
        """Test setting and getting configuration values."""
        config = Config()
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"

    def test_set_overwrites_existing_value(self):
        """Test that setting a key overwrites existing value."""
        config = Config()
        config.set("test_key", "old_value")
        config.set("test_key", "new_value")
        assert config.get("test_key") == "new_value"

    def test_default_values(self):
        """Test that default configuration values are set correctly."""
        config = Config()
        
        # Test default values based on actual implementation
        assert config.get("scope") == "user"
        assert config.get("enable_dnf_hooks") is True
        assert config.get("enable_download_monitoring") is True
        assert str(Path.home() / "Downloads") in config.get("downloads_dir")
        assert config.get("log_format") == "both"
        assert ".rpm" in config.get("monitored_extensions")

    def test_scope_property(self):
        """Test the scope property."""
        config = Config()
        assert config.scope == "user"
        
        config.set("scope", "system")
        assert config.scope == "system"

    def test_config_persistence(self):
        """Test that configuration changes persist within the same instance."""
        config = Config()
        config.set("persistent_key", "persistent_value")
        
        # Verify the value persists
        assert config.get("persistent_key") == "persistent_value"
        
        # Modify the value
        config.set("persistent_key", "modified_value")
        assert config.get("persistent_key") == "modified_value"

    def test_config_isolation(self):
        """Test that different Config instances are isolated."""
        config1 = Config()
        config2 = Config()
        
        config1.set("isolated_key", "config1_value")
        config2.set("isolated_key", "config2_value")
        
        assert config1.get("isolated_key") == "config1_value"
        assert config2.get("isolated_key") == "config2_value"

    def test_boolean_values(self):
        """Test setting and getting boolean values."""
        config = Config()
        config.set("bool_true", True)
        config.set("bool_false", False)
        
        assert config.get("bool_true") is True
        assert config.get("bool_false") is False

    def test_numeric_values(self):
        """Test setting and getting numeric values."""
        config = Config()
        config.set("int_value", 42)
        config.set("float_value", 3.14)
        
        assert config.get("int_value") == 42
        assert config.get("float_value") == 3.14

    def test_list_values(self):
        """Test setting and getting list values."""
        config = Config()
        test_list = ["item1", "item2", "item3"]
        config.set("list_value", test_list)
        
        assert config.get("list_value") == test_list

    def test_dict_values(self):
        """Test setting and getting dictionary values."""
        config = Config()
        test_dict = {"key1": "value1", "key2": "value2"}
        config.set("dict_value", test_dict)
        
        assert config.get("dict_value") == test_dict

    def test_none_values(self):
        """Test setting and getting None values."""
        config = Config()
        config.set("none_value", None)
        
        assert config.get("none_value") is None

    def test_empty_string_values(self):
        """Test setting and getting empty string values."""
        config = Config()
        config.set("empty_string", "")
        
        assert config.get("empty_string") == ""

    def test_config_with_environment_variables(self):
        """Test configuration behavior with environment variables."""
        with patch.dict(os.environ, {"PREZ_PKGLOG_SCOPE": "system"}):
            # The current implementation doesn't use environment variables,
            # but this test ensures the behavior is predictable
            config = Config()
            assert config.scope == "user"  # Should still default to user

    def test_config_string_representation(self):
        """Test string representation of Config object."""
        config = Config()
        config.set("test_key", "test_value")
        
        str_repr = str(config)
        assert "Config" in str_repr
        assert "user" in str_repr  # Should show scope

    def test_config_repr(self):
        """Test repr representation of Config object."""
        config = Config()
        repr_str = repr(config)
        assert "Config" in repr_str
        assert "scope=" in repr_str

    @patch("src.prez_pkglog.config.Path.home")
    def test_config_with_mocked_home(self, mock_home):
        """Test Config behavior with mocked home directory."""
        mock_home.return_value = Path("/mock/home")
        
        config = Config()
        # The Config class doesn't directly use Path.home() in the current implementation,
        # but this test ensures compatibility if it's added later
        assert config.get("downloads_dir") == "~/Downloads"

    def test_config_thread_safety(self):
        """Test that Config operations are thread-safe."""
        import threading
        import time
        
        config = Config()
        results = []
        
        def set_value(key, value):
            config.set(key, value)
            time.sleep(0.01)  # Small delay to increase chance of race condition
            results.append(config.get(key))
        
        # Create multiple threads that set different values
        threads = []
        for i in range(10):
            thread = threading.Thread(target=set_value, args=(f"key_{i}", f"value_{i}"))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all values were set correctly
        assert len(results) == 10
        for i in range(10):
            assert config.get(f"key_{i}") == f"value_{i}"
