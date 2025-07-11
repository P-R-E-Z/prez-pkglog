"""Apt package manager backend implementation"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, ClassVar, final

from .base import PackageBackend, PackageInfo

# Configure logging
logger = logging.getLogger(__name__)


@final
class AptBackend(PackageBackend):
    """
    Backend for logging apt package transactions.
    To enable, create a file at /etc/apt/apt.conf.d/99prez-pkglog
    with the following:

    DPkg::Post-Invoke {
        "if [ -x /usr/local/bin/prez-pkglog-apt ]; then /usr/local/bin/prez-pkglog-apt; fi";
    }
    """

    name: ClassVar[str] = "apt"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the AptBackend."""
        super().__init__(config)
        self.enabled = self.is_available()

    @classmethod
    def is_available(cls) -> bool:
        """Check if the AptBackend is available on the system."""
        return bool(shutil.which("dpkg"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information."""
        if not self.enabled:
            return {}

        try:
            cmd = [
                "dpkg-query",
                "-W",
                "-f=${Package}\\t${Version}\\t${Architecture}\\n",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )

            packages: dict[str, PackageInfo] = {}
            for line in result.stdout.splitlines():
                if not line:
                    continue
                name, version, arch = line.strip().split("\t")
                packages[name] = PackageInfo(
                    name=name, version=version, architecture=arch, installed=True
                )
            return packages
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error(f"Failed to get installed packages using dpkg-query: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """
        Not implemented for AptBackend.

        Transaction logging is handled by an external hook that calls the CLI.
        """
        logger.warning(
            "register_transaction is not supported for the apt backend. "
            "Use a DPkg::Post-Invoke hook."
        )
        return False
