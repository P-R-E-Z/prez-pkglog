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
        self.config_file = Path.home() / ".config/prez-pkglog/prez-pkglog.conf"
        self.data_dir = Path.home() / ".local/share/prez-pkglog"

        # Default settings
        self.settings = {
            "scope": "user",  # "user" or "system"
            "enable_dnf_hooks": True,
            "enable_download_monitoring": True,
            "downloads_dir": (
                "~/Downloads"
                if Path.home() != _ORIGINAL_HOME
                else str(_ORIGINAL_HOME / "Downloads")
            ),
            "log_format": "both",  # json, toml, or both
            "monitored_extensions": ".rpm, .deb, .pkg, .exe, .msi, .dmg",
        }

        # Cache for computed properties
        self._scope_cache = None
        self._is_system_cache = None
        self._is_user_cache = None

        # Load persisted settings (if any) before validation
        self._load_config()
        self._validate_scope()

    # Persistence helpers
    def _load_config(self) -> None:
        """Load configuration from *config_file* if it exists.

        The file is stored as JSON mapping keys→values.  Unknown keys are
        ignored so we can introduce new defaults without breaking older files.
        """

        if not self.config_file.exists():
            return

        try:
            data = json.loads(self.config_file.read_text())
            if not isinstance(data, dict):  # defensive check
                logger.warning(
                    "Config file %s is not a JSON object – ignoring.",
                    self.config_file,
                )
                return

            # Merge persisted settings over defaults
            for key, value in data.items():
                # Skip unknown keys to remain forward-compatible
                if key in self.settings:
                    self.settings[key] = value
        except (OSError, json.JSONDecodeError) as err:
            logger.warning("Could not read config file %s: %s", self.config_file, err)

    def save(self) -> None:
        """Persist the current settings to *config_file* (JSON)."""

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with self.config_file.open("w") as fp:
                json.dump(self.settings, fp, indent=2)
        except OSError as err:
            logger.warning(
                "Failed to save configuration to %s: %s", self.config_file, err
            )

    def _validate_scope(self):
        """Validate scope and permissions"""
        scope = self.settings.get("scope", "user")

        if scope == "system":
            # Check if user is root/admin
            if os.geteuid() != 0:
                logger.warning(
                    "System scope selected but process lacks root privileges – falling back to user scope."
                )
                self.settings["scope"] = "user"

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.settings[key] = value

        # Invalidate caches when scope changes
        if key == "scope":
            self._scope_cache = None
            self._is_system_cache = None
            self._is_user_cache = None

    # Convenience wrapper
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
        # Include scope and a shortened view of settings to avoid long strings.
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
