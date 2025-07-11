"""Dnf package manager backend implementation"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Any, ClassVar, final, Optional

try:
    import dnf
except ImportError:
    dnf = None

from ..base import PackageBackend, PackageInfo

# Configure logging
logger = logging.getLogger(__name__)


@final
class DnfBackend(PackageBackend):
    """Backend for logging dnf package transactions"""

    name: ClassVar[str] = "dnf"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the DnfBackend.

        Args:
            config: Optional configuration object for the backend
        """
        super().__init__(config)
        self.dnf_path = shutil.which("dnf") or "/usr/bin/dnf"
        self.enabled = self.is_available()
        self.logger: Optional[Any] = None  # Will be set by the main logger

    @classmethod
    def is_available(cls) -> bool:
        """Check if the DnfBackend is available on the system

        Returns:
            True if DNF is available, False otherwise
        """
        if dnf is None:
            return False
        return bool(shutil.which("dnf") or Path("/usr/bin/dnf").exists())

    def _check_availability(self) -> bool:
        """Check if DNF backend is configured

        Returns:
            bool: True if configured, False otherwise
        """
        if not self.is_available():
            logger.warning("DNF package manager not found")
            return False
        return True

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information

        Returns:
            Dictionary mapping package names to PackageInfo objects
        """
        if not self.enabled:
            return {}

        packages: dict[str, PackageInfo] = {}
        try:
            with dnf.Base() as base:
                base.fill_sack()
                q = base.sack.query().installed()
                for pkg in q:
                    packages[pkg.name] = PackageInfo(
                        name=pkg.name,
                        version=pkg.version,
                        architecture=pkg.arch,
                        installed=True,
                        source=pkg.reponame,
                    )
        except Exception as e:
            logger.error(f"Failed to get installed packages using dnf API: {e}")
            return {}

        return packages

    def register_transaction(self, transaction: Any) -> bool:
        """Register a DNF transaction for logging

        Args:
            transaction: DNF transaction object with install_set and remove_set attributes

        Returns:
            bool: True if registration was successful, False otherwise
        """
        if not self.enabled:
            return False

        success = True

        # Log installed packages
        for pkg in getattr(transaction, "install_set", []):
            if not self._log_package_install(pkg):
                success = False

        # Log removed packages
        for pkg in getattr(transaction, "remove_set", []):
            if not self._log_package_remove(pkg):
                success = False

        return success

    def _log_package_install(self, pkg: Any) -> bool:
        """Log an installed package

        Args:
            pkg: Package object from DNF

        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            name = getattr(pkg, "name", "")
            version = getattr(pkg, "version", "")
            release = getattr(pkg, "release", "")
            full_version = f"{version}-{release}" if version and release else version

            if self.logger:
                self.logger.log_package(
                    name=name,
                    manager=self.name,
                    action="install",
                    version=full_version,
                    metadata={
                        "arch": getattr(pkg, "arch", None),
                        "repo": getattr(pkg, "reponame", None),
                        "epoch": getattr(pkg, "epoch", None),
                    },
                )
            return True

        except Exception as e:
            logger.error(
                f"Error logging package install {getattr(pkg, 'name', 'unknown')}: {e}"
            )
            return False

    def _log_package_remove(self, pkg: Any) -> bool:
        """Log a removed package

        Args:
            pkg: Package object from DNF

        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            name = getattr(pkg, "name", "")
            version = getattr(pkg, "version", "")
            release = getattr(pkg, "release", "")
            full_version = f"{version}-{release}" if version and release else version

            if self.logger:
                self.logger.log_package(
                    name=name,
                    manager=self.name,
                    action="remove",
                    version=full_version,
                    metadata={
                        "arch": getattr(pkg, "arch", None),
                        "repo": getattr(pkg, "reponame", None),
                        "epoch": getattr(pkg, "epoch", None),
                    },
                )
            return True

        except Exception as e:
            logger.error(
                f"Error logging package removal {getattr(pkg, 'name', 'unknown')}: {e}"
            )
            return False


# Registration will be handled by __init__.py
