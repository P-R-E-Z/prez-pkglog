import dnf
import subprocess
from pathlib import Path
import logging
from typing import List, Optional

# Configure Logging
logger = logging.getLogger(__name__)

# Constants
PLUGIN_NAME = "prez_pkglogger"
CONFIG_PATH = Path(f"/etc/dnf/plugins/{PLUGIN_NAME}.conf")
DEFAULT_COMMAND = "prez-pkglog"


class PkgLogger(dnf.Plugin):
    """DNF plugin for logging package transactions to prez-pkglog"""

    name = PLUGIN_NAME

    def __init__(self, base: dnf.Base, cli: Optional[dnf.cli.Cli] = None) -> None:
        """Initialize the plugin"""
        super().__init__(base, cli)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._load_config()

    def _load_config(self) -> None:
        """Load the plugin configuration"""
        self.command = DEFAULT_COMMAND
        self.scope = "user"  # Default to user scope

        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH) as f:
                    for line in f:
                        if line.startswith("scope"):
                            self.scope = line.split("=")[1].strip()
                self.logger.info(f"Loaded config from {CONFIG_PATH}")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

    def _log_packages(self, packages: List[dnf.package.Package], action: str) -> None:
        """Log packages to prez-pkglog"""
        if not packages:
            return

        for pkg in packages:
            try:
                cmd = [self.command, action, pkg.name, "dnf", "--scope", self.scope]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=False
                )
                if result.returncode != 0:
                    self.logger.error(
                        f"Failed to log {action} for package {pkg.name}: "
                        f"{result.stderr or 'unknown error'}"
                    )
            except Exception as e:
                self.logger.error(f"Error logging package {pkg.name}: {e}")

    def transaction(self) -> None:
        """Log package transactions to prez-pkglog"""
        if not hasattr(self.base, "transaction"):
            self.logger.warning("No transaction data available")
            return

        if hasattr(self.base.transaction, "install_set"):
            self._log_packages(list(self.base.transaction.install_set), "install")

        if hasattr(self.base.transaction, "remove_set"):
            self._log_packages(list(self.base.transaction.remove_set), "remove")


# Enable with: echo 'enabled=1' | sudo tee /etc/dnf/plugins/prez_pkglogger.conf
# Add scope: echo 'scope=system' | sudo tee -a /etc/dnf/plugins/prez_pkglogger.conf
