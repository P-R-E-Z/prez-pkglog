"""Homebrew package manager backend implementation"""

from __future__ import annotations

import logging
import shutil
import subprocess
from typing import Any, ClassVar, final

from ..base import PackageBackend, PackageInfo

# Configure logging
logger = logging.getLogger(__name__)


@final
class BrewBackend(PackageBackend):
    """
    Backend for logging Homebrew package transactions.

    Homebrew does not have a traditional post-transaction hook system.
    Automatic logging can be achieved by creating a shell wrapper
    function for `brew`. Add this to your ~/.zshrc or ~/.bash_profile:

    function brew() {
        case "$1" in
            install|uninstall|reinstall|upgrade)
                command brew "$@"
                # This part requires a separate script to parse brew's
                # actions and call `prez-pkglog`.
                /usr/local/bin/prez-pkglog-brew-hook
                ;;
            *)
                command brew "$@"
                ;;
        esac
    }
    """

    name: ClassVar[str] = "brew"

    def __init__(self, config: Any | None = None) -> None:
        """Initialize the BrewBackend."""
        super().__init__(config)
        self.enabled = self.is_available()

    @classmethod
    def is_available(cls) -> bool:
        """Check if the BrewBackend is available on the system."""
        return bool(shutil.which("brew"))

    def get_installed_packages(self) -> dict[str, PackageInfo]:
        """Get a dictionary of installed packages and their information."""
        if not self.enabled:
            return {}

        try:
            # --formula is used to list only formulae, not casks
            cmd = ["brew", "list", "--formula", "--versions"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )

            packages: dict[str, PackageInfo] = {}
            for line in result.stdout.splitlines():
                if not line:
                    continue
                # Output is like "neovim 0.7.2", "python@3.10 3.10.6"
                name, version = line.strip().rsplit(" ", 1)
                packages[name] = PackageInfo(name=name, version=version, installed=True)
            return packages
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            logger.error(f"Failed to get installed packages using brew: {e}")
            return {}

    def register_transaction(self, transaction: Any) -> bool:
        """
        Not implemented for BrewBackend.

        Transaction logging should be handled by an external script
        called from a shell wrapper function.
        """
        logger.warning(
            "register_transaction is not supported for the brew backend. "
            "Use a shell wrapper function."
        )
        return False
