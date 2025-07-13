"""Pacman package manager backend implementation"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, ClassVar, final

from ..base import PackageBackend, PackageInfo
from ..helpers import parse_pacman_query_line

# Configure logging
logger = logging.getLogger(__name__)


@final
class PacmanBackend(PackageBackend):
    """
    Backend for logging pacman package transactions.

    This backend relies on an external hook for automatic logging.
    To enable, create a hook file at /etc/pacman.d/hooks/prez-pkglog.hook
    with:

    [Trigger]
    Operation = Install
    Operation = Upgrade
    Operation = Remove
    Type = Package
    Target = *

    [Action]
    Description = Log package transaction with prez-pkglog
    When = PostTransaction
    Exec = /usr/bin/prez-pkglog-pacman
    """

    name: ClassVar[str] = "pacman"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the PacmanBackend."""
        super().__init__(config)
        self.enabled = self.is_available()

    @classmethod
    def is_available(cls) -> bool:
        """Check if the PacmanBackend is available on the system."""
        return bool(shutil.which("pacman"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information."""
        if not self.enabled:
            return {}

        try:
            cmd = ["pacman", "-Q"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )

            packages: dict[str, PackageInfo] = {}
            for line in result.stdout.splitlines():
                parsed = parse_pacman_query_line(line)
                if parsed is None:
                    # Malformed line was already logged by the helper
                    continue

                name, version = parsed
                packages[name] = PackageInfo(name=name, version=version, installed=True)
            return packages
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error(f"Failed to get installed packages using pacman: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """
        Not implemented for PacmanBackend.

        Transaction logging is handled by an external hook that calls the CLI.
        """
        logger.warning(
            "register_transaction is not supported for the pacman backend. "
            "Use a pacman hook."
        )
        return False
