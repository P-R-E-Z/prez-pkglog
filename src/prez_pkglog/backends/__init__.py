"""Package containing all package manager backends"""

from __future__ import annotations

# Import all backends to register them
from .dnf import DnfBackend  # noqa: F401

# Re-export the base backend for easier imports
from .base import PackageBackend

# Backends will be registered in the main __init__.py

__all__ = [
    "PackageBackend",
    "DnfBackend",
]
