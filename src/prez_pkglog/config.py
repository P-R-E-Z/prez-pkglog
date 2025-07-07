import os
from pathlib import Path
from typing import Any, Literal

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
            "downloads_dir": str(Path.home() / "Downloads"),
            "log_format": "both",  # json, toml, or both
        }

        # Cache for computed properties
        self._scope_cache = None
        self._is_system_cache = None
        self._is_user_cache = None

        self._load_config()
        self._validate_scope()

    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            # Will expand on this later (WIP)
            pass

    def _validate_scope(self):
        """Validate scope and permissions"""
        scope = self.settings.get("scope", "user")

        if scope == "system":
            # Check if user is root/admin
            if os.geteuid() != 0:
                print("Warning: System scope requires root/admin privileges")
                print("Please run with sudo or switch to user scope")
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
