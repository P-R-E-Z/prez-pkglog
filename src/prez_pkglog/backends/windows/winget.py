"""Winget package manager backend implementation for Windows"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, ClassVar, final

from ..base import PackageBackend, PackageInfo

# Configure logging
logger = logging.getLogger(__name__)


@final
class WingetBackend(PackageBackend):
    """
    Backend for logging Winget package transactions.

    Winget does not currently have a hook or scriptable event system.
    A contributor could potentially implement logging by either:
    1. Creating a PowerShell wrapper function for `winget`.
    2. Periodically polling and diffing the output of `winget list`.
    """

    name: ClassVar[str] = "winget"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the WingetBackend."""
        super().__init__(config)
        self.enabled = self.is_available()

    @classmethod
    def is_available(cls) -> bool:
        """Check if the WingetBackend is available on the system."""
        return bool(shutil.which("winget"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information."""
        if not self.enabled:
            return {}

        try:
            # --accept-source-agreements is needed for first run
            cmd = ["winget", "list", "--accept-source-agreements"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=120
            )

            packages: dict[str, PackageInfo] = {}
            # Skip the header lines of the output
            for line in result.stdout.splitlines()[2:]:
                if not line or line.startswith("---"):
                    continue
                # Winget's output is column-based and can be tricky.
                # This is a best-effort parse.
                parts = [p for p in line.split(" ") if p]
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1]
                    packages[name] = PackageInfo(
                        name=name, version=version, installed=True
                    )
            return packages
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error(f"Failed to get installed packages using winget: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """
        Not implemented for WingetBackend.

        Transaction logging would require a wrapper or polling mechanism.
        """
        logger.warning("register_transaction is not supported for the winget backend.")
        return False
