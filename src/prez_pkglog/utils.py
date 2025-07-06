"""Utility functions for cross-platform support"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Set, Union


def get_platform() -> str:
    """Get the current platform identifier

    Returns:
        str: The platform identifier (e.g., 'linux', 'windows', 'darwin', etc.)
    """
    return sys.platform.lower()


def is_windows() -> bool:
    """Check if the current platform is Windows

    Returns:
        bool: True if the platform is Windows, False otherwise
    """
    return get_platform() == "win32"


def is_linux() -> bool:
    """Check if the current platform is Linux

    Returns:
        bool: True if the platform is Linux, False otherwise
    """
    return get_platform() == "linux"


def is_macos() -> bool:
    """Check if the current platform is macOS

    Returns:
        bool: True if the platform is macOS, False otherwise
    """
    return get_platform() == "darwin"


def is_wsl() -> bool:
    """Check if the current platform is WSL

    Returns:
        bool: True if the platform is WSL, False otherwise
    """
    return get_platform() == "linux" and shutil.which("wslpath")


def get_downloads_dir() -> List[Path]:
    """Get the list of directories to search for downloads

    Returns:
        List[Path]: List of directories to search for downloads
    """
    home = Path.home()
    if is_windows():
        # On Windows, check both the default Downloads folder and OneDrive if it exists
        dirs = [
            home / "Downloads",
            home / "OneDrive" / "Downloads",
        ]
    elif is_macos():
        # I don't know MacOS so let me know if this works
        dirs = [
            home / "Downloads",
        ]
    elif is_wsl():
        # Same thing as MacOS... Let me know if this works lol
        dirs = [
            home / "Downloads",
            home / "OneDrive" / "Downloads",
        ]
    else:  # Linux and other Unix systems
        # Check XDG_DOWNLOAD_DIR first, then fall back to ~/Downloads
        xdg_download = os.environ.get("XDG_DOWNLOAD_DIR")
        dirs = [
            Path(xdg_download) if xdg_download else None,
            home / "Downloads",
        ]

    # Filter out None values and non-existent directories
    return [d for d in dirs if d and d.exists()]


def get_package_managers() -> Set[str]:
    """Detect available package managers on the system

    Returns:
        Set[str]: Set of available package manager commands
    """
    managers = set()

    # Common package managers
    common_managers = [
        "apt",  # Linux
        "apt-get",
        "dnf",
        "yum",
        "zypper",
        "pacman",  # Arch Linux
        "yay",
        "paru",
        "pamac",
        "brew",  # macOS
        "port",
        "choco",  # Windows
        "scoop",
        "winget",
        "snap",  # Cross-platform
        "flatpak",
        "nix-env",
    ]

    for manager in common_managers:
        if shutil.which(manager):
            managers.add(manager)

    return managers


def normalize_path(path: Union[str, Path]) -> Path:
    """Normalize a path, expanding user and resolving to absolute path

    Args:
        path: Path to normalize (string or Path object)

    Returns:
        Path: Normalized Path object
    """
    path = Path(path).expanduser().absolute()
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        # If the path doesn't exist, return the original path
        return path


def ensure_directory(path: Union[str, Path]) -> None:
    """Ensure that a directory exists at the given path, creating it if necessary

    Args:
        path: Path to directory to ensure (string or Path object)

    Returns:
        Path: Path to the directory
    """
    path = normalize_path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_checksum(file_path: Union[str, Path], algorith: str = "sha256") -> str:
    """Get the checksum of a file using the specified algorithm

    Args:
        file_path: Path to the file to get the checksum of (string or Path object)
        algorithm: Hash algorithm to use for checksum (default is 'sha256')

    Returns:
        str: Hexadecimal checksum of the file's hash
        :param algorith:
    """
