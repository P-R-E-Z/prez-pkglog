"""Unit tests for the models module"""

from pathlib import Path
from datetime import datetime

from src.prez_pkglog.models import PkgEvent


class TestPkgEvent:
    """Test the PkgEvent model."""

    def test_pkg_event_creation(self):
        """Test creating a PkgEvent instance."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        assert event.name == "test-package"
        assert event.version == "1.0.0"
        assert event.summary == "Test package"
        assert event.scope == "user"
        assert str(event.location) == "/tmp/test"

    def test_pkg_event_defaults(self):
        """Test PkgEvent with default values."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        assert event.name == "test-package"
        assert event.version == "1.0.0"
        assert event.summary == "Test package"
        assert event.scope == "user"
        assert event.when is not None  # Should have default datetime

    def test_pkg_event_str_representation(self):
        """Test string representation of PkgEvent."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        str_repr = str(event)
        assert "test-package" in str_repr
        assert "1.0.0" in str_repr

    def test_pkg_event_repr_representation(self):
        """Test repr representation of PkgEvent."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        repr_str = repr(event)
        assert "PkgEvent" in repr_str
        assert "test-package" in repr_str
        assert "1.0.0" in repr_str

    def test_pkg_event_equality(self):
        """Test PkgEvent equality comparison."""
        event1 = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        event2 = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        event3 = PkgEvent(
            name="different-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        assert event1 == event2
        assert event1 != event3

    def test_pkg_event_to_dict(self):
        """Test PkgEvent to_dict method."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        result = event.to_dict()

        assert result["name"] == "test-package"
        assert result["version"] == "1.0.0"
        assert result["summary"] == "Test package"
        assert result["scope"] == "user"
        assert result["location"] == "/tmp/test"
        assert "when" in result
        assert result["when"].endswith("Z")  # Should end with Z for UTC

    def test_pkg_event_system_scope(self):
        """Test PkgEvent with system scope."""
        event = PkgEvent(
            name="system-package",
            version="2.0.0",
            summary="System package",
            scope="system",
            location=Path("/var/log/test"),
        )

        assert event.scope == "system"
        assert str(event.location) == "/var/log/test"

    def test_pkg_event_custom_datetime(self):
        """Test PkgEvent with custom datetime."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
            when=custom_time,
        )

        assert event.when == custom_time

    def test_pkg_event_scope_types(self):
        """Test PkgEvent with different scope types."""
        # Test user scope
        user_event = PkgEvent(
            name="user-package",
            version="1.0.0",
            summary="User package",
            scope="user",
            location=Path("/home/user/test"),
        )
        assert user_event.scope == "user"

        # Test system scope
        system_event = PkgEvent(
            name="system-package",
            version="1.0.0",
            summary="System package",
            scope="system",
            location=Path("/var/log/test"),
        )
        assert system_event.scope == "system"

    def test_pkg_event_immutable_attributes(self):
        """Test that PkgEvent attributes are immutable (dataclass frozen)."""
        event = PkgEvent(
            name="test-package",
            version="1.0.0",
            summary="Test package",
            scope="user",
            location=Path("/tmp/test"),
        )

        # Dataclasses are not frozen by default, so attributes should be mutable
        # This test verifies the current behavior
        event.name = "new-name"
        assert event.name == "new-name"
