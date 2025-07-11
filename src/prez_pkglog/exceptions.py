"""Custom exception hierarchy for prez-pkglog."""


class PrezPkglogError(Exception):
    """Base exception for the application."""


class ConfigError(PrezPkglogError):
    """Raised when configuration cannot be loaded or saved."""


class PackageLoggingError(PrezPkglogError):
    """Generic failure while recording a package event."""
