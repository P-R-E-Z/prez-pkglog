"""Base package backend interface"""

from __future__ import annotations

import abc
import logging
from typing import Any, TypeVar, ClassVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)
T = TypeVar("T", bound="PackageBackend")


class PackageInfo(BaseModel):
    """Information about a package"""

    name: str
    version: str
    source: str | None = None
    description: str | None = None
    architecture: str | None = None
    repository: str | None = None
    installed: bool = False
    metadata: dict[str, Any] = {}


class PackageBackend(abc.ABC):
    """Abstract base class for package manager backends"""

    name: ClassVar[str] = ""

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the backend

        Args:
            config: Optional configuration object for the backend
        """
        self.config = config
        self.enabled = True

    @classmethod
    @abc.abstractmethod
    def is_available(cls) -> bool:
        """Check if the backend is available on the system

        Returns:
            True if the backend is available, False otherwise
        """
        ...

    @abc.abstractmethod
    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information

        Returns:
            Dictionary mapping package names to PackageInfo objects
        """
        ...

    @abc.abstractmethod
    def register_transaction(self, transaction: Any) -> bool:
        """Register a package transaction for logging

        Args:
            transaction: Package transaction object with install_set and remove_set attributes

        Returns:
            True if registration was successful, False otherwise
        """
        ...

    def refresh(self) -> bool:
        """Refresh the package database/cache

        Returns:
            True if refresh was successful, False otherwise
        """
        return True  # Default implementation does nothing

    def get_package_info(self, package_name: str) -> PackageInfo | None:
        """Get detailed information about a specific package

        Args:
            package_name: Name of the package to get info for

        Returns:
            package_name: Name of the package to get info for
        """
        installed = self.get_installed_packages()
        return installed.get(package_name)

    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed

        Args:
            package_name: Name of the package to check

        Returns:
            True if the package is installed, False otherwise
        """
        return package_name in self.get_installed_packages()

    def search_packages(self, query: str) -> list[PackageInfo]:
        """Search for packages based on a query

        Args:
            query: Search query string

        Returns:
            List of matching packages
        """
        installed = self.get_installed_packages()
        query = query.lower()
        return [
            pkg
            for name, pkg in installed.items()
            if query in name.lower()
            or (pkg.description and query in pkg.description.lower())
        ]

    def get_package_files(self, package_name: str) -> list[str]:
        """Get a list of files installed by a package

        Args:
            package_name: Name of the package to get files for

        Returns:
            List of file paths
        """
        return []  # Default implementation returns an empty list

    def get_package_dependencies(
        self, package_name: str, *, recursive: bool = False
    ) -> dict[str, list[str]]:
        """Get dependencies for a package

        Args:
            package_name: Name of the package to get dependencies for
            recursive: If True, include transitive dependencies (default: False)

        Returns:
            Dictionary mapping package names to a list of dependencies
        """
        return {}  # Default implementation returns an empty dictionary

    def get_package_changelog(self, package_name: str) -> str | None:
        """Get the changelog for a package

        Args:
            package_name: Name of the package to get changelog for

        Returns:
            Changelog text if available, None otherwise
        """
        return None  # Default implementation returns None
