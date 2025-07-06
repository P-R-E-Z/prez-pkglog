"""Main package for prez-pkglog"""

from __future__ import annotations

import importlib.metadata
from typing import TypeVar, Any

from .package_backend import PackageBackend

# Type variable for package backends
T = TypeVar("T", bound=PackageBackend)

# Dictionary to store registered backends
_BACKENDS: dict[str, type[T]] = {}


def register_backend(name: str, backend_class: type[T]) -> None:
    """Register a new package manager backend

    Args:
        name: Name of the package manager (e.g., 'dnf', apt, etc.)
        backend_class: Backend class to register
    """
    _BACKENDS[name] = backend_class


def get_backend(name: str | None = None) -> PackageBackend | None:
    """Get a package manager backend by name

    Args:
        name: Name of the package manager (e.g., 'dnf', apt, etc.)

    Returns:
        PackageBackend instance or None if not found/available
    """
    if backend_class := _BACKENDS.get(name.lower()):
        return backend_class()
    return None


def detect_available_backends(
    config: Any | None = None,
) -> dict[str, PackageBackend]:
    """Detect and return all available package manager backends

    Args:
        config: Optional configuration to pass to backends

    Returns:
        Dictionary mapping backend names to initialized backend instances
    """
    available = {}
    for name, backend_class in _BACKENDS.items():
        if backend_class.is_available():
            available[name] = backend_class(config)
    return available


# Package version
try:
    __version__ = importlib.metadata.version("prez-pkglog")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Development version

# Import built-in backends to register them
# These imports are at the bottom to avoid circular imports
from . import backends  # noqa: F401, E402
