import dnf  # type: ignore
from pathlib import Path
import logging
from typing import List, Optional

from prez_pkglog.config import Config
from prez_pkglog.logger import PackageLogger

# Configure Logging
logger = logging.getLogger(__name__)

# Constants
# The plugin name must match 1) this *module* filename (prez_pkglog.py) and 2)
# the *.conf* file shipped under */etc/dnf/plugins/*.  Using the same string
# everywhere ensures DNF can discover and enable the plugin when
# ``enabled=1`` is set.
PLUGIN_NAME = "prez_pkglog"
USER_CONFIG_PATH = Path.home() / f".config/dnf/plugins/{PLUGIN_NAME}.conf"
SYSTEM_CONFIG_PATH = Path(f"/etc/dnf/plugins/{PLUGIN_NAME}.conf")


class PkgLogger(dnf.Plugin):
    """DNF plugin for logging package transactions to prez-pkglog"""

    name = PLUGIN_NAME

    def __init__(self, base: dnf.Base, cli: Optional[dnf.cli.Cli] = None) -> None:
        """Initialize the plugin"""
        super().__init__(base, cli)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._load_config()
        # Initialize configuration for PackageLogger.  Name it *cfg* to avoid
        # colliding with the ``config`` hook method that DNF calls during
        # plugin initialisation.
        self.cfg = Config()
        self.cfg.set("scope", self.scope)
        self.pkg_logger = PackageLogger(self.cfg)

    def _load_config(self) -> None:
        """Load the plugin configuration"""
        self.scope = "user"  # Default to user scope
        config_path = (
            SYSTEM_CONFIG_PATH
            if Path("/etc/dnf/plugins").exists()
            else USER_CONFIG_PATH
        )

        if config_path.exists():
            try:
                with open(config_path) as f:
                    for line in f:
                        if line.strip().startswith("scope"):
                            self.scope = line.split("=")[1].strip()
                self.logger.info(f"Loaded config from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")


    def _log_packages(self, packages: List[dnf.package.Package], action: str) -> None:
        """Log packages to prez-pkglog"""
        if not packages:
            return

        for pkg in packages:
            try:
                self.pkg_logger.log_package(
                    name=pkg.name,
                    manager="dnf",
                    action=action,
                    version=f"{pkg.version}-{pkg.release}",
                    metadata={
                        "arch": pkg.arch,
                        "repo": pkg.reponame,
                        "epoch": pkg.epoch,
                    },
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


# Enable with: echo 'enabled=1' | sudo tee /etc/dnf/plugins/prez_pkglog.conf
# Optional: set the scope to *system* so logs go to /var/log/prez-pkglog
#   echo 'scope=system' | sudo tee -a /etc/dnf/plugins/prez_pkglog.conf
