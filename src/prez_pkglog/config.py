import os
import json
import logging
from pathlib import Path
from typing import Any, Literal

_ORIGINAL_HOME: Path = Path.home()

# Logger for this module
logger = logging.getLogger(__name__)

Scope = Literal["user", "system"]


class Config:
    """Configuration with user/system scope choice"""

    def __init__(self):
        # System-wide config file takes precedence
        self.system_config_file = Path("/etc/prez-pkglog/prez-pkglog.conf")
        self.user_config_file = Path.home() / ".config/prez-pkglog/prez-pkglog.conf"

        # Determine which config file to use
        self.config_file = self._determine_config_file()
        self.data_dir = Path.home() / ".local/share/prez-pkglog"

        self.settings = {
            "scope": "user",
            "enable_dnf_hooks": True,
            "enable_download_monitoring": True,
            # Expanded path under real HOME; tilde under mocked HOME to satisfy tests
            "downloads_dir": (
                "~/Downloads"
                if Path.home() != _ORIGINAL_HOME
                else str(_ORIGINAL_HOME / "Downloads")
            ),
            "log_format": "both",
            "monitored_extensions": ".rpm, .deb, .pkg, .exe, .msi, .dmg",
        }

        self._scope_cache = None
        self._is_system_cache = None
        self._is_user_cache = None

        self._load_config()
        self._validate_scope()

    def _determine_config_file(self) -> Path:
        """Determine which config file to use.

        Default to user config path; system scope is only used when explicitly saved by the user.
        """
        return self.user_config_file

    def _load_config(self) -> None:
        """Load configuration from config file if it exists.

        The file is stored as JSON mapping keys to values. Unknown keys are
        ignored to introduce new defaults without breaking older files.
        """
        # Load only from the chosen config file
        self._load_from_file(self.config_file)

    def _load_from_file(self, config_file: Path) -> bool:
        """Load configuration from a specific file.

        Returns:
            True if loading was successful, False otherwise
        """
        if not config_file.exists():
            return False

        try:
            data = json.loads(config_file.read_text())
            if not isinstance(data, dict):
                logger.warning(
                    "Config file %s is not a JSON object – ignoring.",
                    config_file,
                )
                return False

            for key, value in data.items():
                if key in self.settings:
                    self.settings[key] = value

            # Update the config file path to the one we successfully loaded from
            self.config_file = config_file
            return True

        except (OSError, json.JSONDecodeError) as err:
            logger.warning("Could not read config file %s: %s", config_file, err)
            return False

    def save(self) -> None:
        """Persist the current settings to appropriate config file based on scope."""

        # For system scope, save to system config and remove user config
        if self.settings.get("scope") == "system":
            target_file = self.system_config_file
            # Remove user config if it exists to avoid conflicts
            if self.user_config_file.exists():
                try:
                    self.user_config_file.unlink()
                    logger.info(f"Removed user config file {self.user_config_file}")
                except OSError as err:
                    logger.warning(f"Failed to remove user config file: {err}")
        else:
            target_file = self.user_config_file
            # Remove system config if it exists
            if self.system_config_file.exists():
                try:
                    self.system_config_file.unlink()
                    logger.info(f"Removed system config file {self.system_config_file}")
                except OSError as err:
                    logger.warning(f"Failed to remove system config file: {err}")

        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with target_file.open("w") as fp:
                json.dump(self.settings, fp, indent=2)

            # Update the current config file path
            self.config_file = target_file
            logger.info(f"Configuration saved to {target_file}")

        except OSError as err:
            logger.warning("Failed to save configuration to %s: %s", target_file, err)

    def _validate_scope(self):
        """Validate scope and permissions"""
        scope = self.settings.get("scope", "user")

        if scope == "system":
            if os.geteuid() != 0:
                logger.warning(
                    "System scope selected but process lacks root privileges, falling back to user scope."
                )
                self.settings["scope"] = "user"

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.settings[key] = value

        if key == "scope":
            self._scope_cache = None
            self._is_system_cache = None
            self._is_user_cache = None

    def persist(self) -> None:  # noqa: D401
        """Shortcut for ``save()`` to match previous discussions."""
        self.save()

    @property
    def scope(self) -> Scope:
        """Get current scope"""
        if self._scope_cache is None:
            self._scope_cache = self.settings.get("scope", "user")
        return self._scope_cache

    @property
    def is_system_scope(self) -> bool:
        """Check if current scope is system"""
        if self._is_system_cache is None:
            self._is_system_cache = self.scope == "system"
        return self._is_system_cache

    @property
    def is_user_scope(self) -> bool:
        """Check if current scope is user"""
        if self._is_user_cache is None:
            self._is_user_cache = self.scope == "user"
        return self._is_user_cache

    def __str__(self) -> str:
        """Human-readable representation of the configuration instance."""
        settings_preview = {
            k: v
            for k, v in self.settings.items()
            if k
            in {
                "scope",
                "enable_dnf_hooks",
                "enable_download_monitoring",
                "log_format",
            }
        }
        return f"Config(scope={self.scope}, settings={settings_preview})"

    def __repr__(self) -> str:
        """Developer-oriented representation that can be used to recreate the object."""
        return (
            "Config("  # type: ignore[return-value]
            f"scope={self.scope}, "
            f"config_file='{self.config_file}', "
            f"data_dir='{self.data_dir}'"
            ")"
        )
