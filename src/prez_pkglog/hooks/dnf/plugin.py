from pathlib import Path
import logging
from typing import List, Optional, Any

try:
    import dnf  # type: ignore[import-untyped]
except ImportError:
    dnf = None  # type: ignore[assignment]

from prez_pkglog.config import Config
from prez_pkglog.logger import PackageLogger

logger = logging.getLogger(__name__)

PLUGIN_NAME = "prez_pkglog"
USER_CONFIG_PATH = Path.home() / f".config/dnf/plugins/{PLUGIN_NAME}.conf"
SYSTEM_CONFIG_PATH = Path(f"/etc/dnf/plugins/{PLUGIN_NAME}.conf")


class PkgLogger(dnf.Plugin if dnf else object):  # type: ignore[misc]
    """DNF plugin for logging package transactions to prez-pkglog"""

    name = PLUGIN_NAME
    enabled = True

    def __init__(self, base: Any, cli: Optional[Any] = None) -> None:
        """Initialize the plugin"""
        if dnf is None:
            raise ImportError("dnf module is required but not available")
        super().__init__(base, cli)

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._load_config()
        self.cfg = Config()
        self.cfg.set("scope", self.scope)
        self.pkg_logger = PackageLogger(self.cfg)

    def _load_config(self) -> None:
        """Load the plugin configuration"""
        self.scope = "user"
        config_path = SYSTEM_CONFIG_PATH if Path("/etc/dnf/plugins").exists() else USER_CONFIG_PATH

        if config_path.exists():
            try:
                with open(config_path) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("scope"):
                            self.scope = line.split("=")[1].strip()
                        elif line.startswith("enabled"):
                            # Check if plugin is enabled
                            enabled = line.split("=")[1].strip()
                            if enabled == "0":
                                self.enabled = False
                                return
                self.logger.info(f"Loaded config from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

    def _log_packages(self, packages: List[Any], action: str) -> None:
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
        self.logger.info("prez_pkglog plugin transaction method called")

        if not hasattr(self.base, "transaction"):
            self.logger.warning("No transaction data available")
            return

        if hasattr(self.base.transaction, "install_set"):
            install_packages = list(self.base.transaction.install_set)
            self.logger.info(f"Found {len(install_packages)} packages to install")
            self._log_packages(install_packages, "install")

        if hasattr(self.base.transaction, "remove_set"):
            remove_packages = list(self.base.transaction.remove_set)
            self.logger.info(f"Found {len(remove_packages)} packages to remove")
            self._log_packages(remove_packages, "remove")
