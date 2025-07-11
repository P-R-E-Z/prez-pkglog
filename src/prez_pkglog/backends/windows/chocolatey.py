"""Chocolatey package manager backend implementation for Windows"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, ClassVar, final

from ..base import PackageBackend, PackageInfo

# Configure logging
logger = logging.getLogger(__name__)


@final
class ChocolateyBackend(PackageBackend):
    """
    Backend for logging Chocolatey package transactions.

    This backend relies on Chocolatey's hook mechanism for automatic logging.
    A contributor would need to create PowerShell scripts in
    `$env:ChocolateyInstall\\hooks` (e.g., `pre-install.ps1`, `post-uninstall.ps1`)
    that call the `prez-pkglog` CLI.

    See: https://docs.chocolatey.org/en-us/features/hook-scripts
    """

    name: ClassVar[str] = "chocolatey"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the ChocolateyBackend."""
        super().__init__(config)
        self.enabled = self.is_available()

    @classmethod
    def is_available(cls) -> bool:
        """Check if the ChocolateyBackend is available on the system."""
        return bool(shutil.which("choco"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information."""
        if not self.enabled:
            return {}

        try:
            cmd = ["choco", "list", "--local-only", "--limit-output"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=60
            )

            packages: dict[str, PackageInfo] = {}
            for line in result.stdout.splitlines():
                if not line:
                    continue
                # Output is "name|version"
                name, version = line.strip().split("|")
                packages[name] = PackageInfo(
                    name=name, version=version, installed=True
                )
            return packages
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error(f"Failed to get installed packages using choco: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """
        Not implemented for ChocolateyBackend.

        Transaction logging is handled by external hook scripts that call the CLI.
        """
        logger.warning(
            "register_transaction is not supported for the chocolatey backend. "
            "Use hook scripts."
        )
        return False
