# prez-pkglog - light cross-distro package logger engine
import datetime as dt
import json
import pathlib
import sys
import os
from typing import Dict, Any, Optional, Iterator
import logging
import threading
from contextlib import contextmanager

try:
    import toml
except ImportError:
    toml = None

from .config import Config

logger = logging.getLogger(__name__)

# Cross-platform file-lock helpers
if os.name == "posix":
    import fcntl  # type: ignore

    @contextmanager
    def _file_lock(path: pathlib.Path) -> Iterator[None]:
        """Context manager acquiring an exclusive advisory lock on *path*."""
        # Open file handle (create if absent) strictly for locking
        with path.open("a") as lock_fp:
            try:
                fcntl.flock(lock_fp, fcntl.LOCK_EX)
                yield
            finally:
                fcntl.flock(lock_fp, fcntl.LOCK_UN)

else:  # Windows – use msvcrt
    import msvcrt  # type: ignore

    @contextmanager
    def _file_lock(path: pathlib.Path) -> Iterator[None]:
        with path.open("a") as lock_fp:
            try:
                # Lock entire file
                msvcrt.locking(lock_fp.fileno(), msvcrt.LK_LOCK, 1)
                yield
            finally:
                lock_fp.seek(0)
                msvcrt.locking(lock_fp.fileno(), msvcrt.LK_UNLCK, 1)


class PackageLogger:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._thread_lock = threading.Lock()
        self._setup_paths()
        self._ensure_directories()

    def _setup_paths(self):
        """Setup paths based on scope"""
        if self.config.is_system_scope:
            # System wide logging
            self.data_dir = pathlib.Path("/var/log/prez-pkglog")
            self.json_file = self.data_dir / "packages.json"
            self.toml_file = self.data_dir / "packages.toml"
        else:
            # User logging
            self.data_dir = pathlib.Path.home() / ".local/share/prez-pkglog"
            self.json_file = self.data_dir / "packages.json"
            self.toml_file = self.data_dir / "packages.toml"

    def _ensure_directories(self):
        """Create directories if they don't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Set permissions based on scope
        if self.config.is_system_scope:
            # System wide: read for all, write for root
            self.data_dir.chmod(0o755)
        else:
            # User: user only
            self.data_dir.chmod(0o700)

        if not self.json_file.exists():
            self.json_file.write_text("[]")
        if not self.toml_file.exists():
            self.toml_file.write_text("")

        # Set file permissions
        if self.config.is_system_scope:
            self.json_file.chmod(0o644)
            self.toml_file.chmod(0o644)
        else:
            self.json_file.chmod(0o600)
            self.toml_file.chmod(0o600)

    def log_package(
        self,
        name: str,
        manager: str,
        action: str,
        version: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Log a package action"""
        # Validation check for empty names
        if not name or not name.strip():
            logger.warning(f"Warning: Invalid package name: {name}")
            return

        entry = {
            "name": name.strip(),
            "manager": manager,
            "action": action,
            "date": dt.datetime.now().isoformat(timespec="seconds"),
            "removed": action == "remove",
            "scope": self.config.scope,
        }

        if version:
            entry["version"] = version
        if metadata:
            entry["metadata"] = metadata

        self._append_json(entry)
        self._append_toml(entry)

    def _append_json(self, entry: Dict[str, Any]):
        """Append entry to JSON log file"""
        try:
            with self._thread_lock:
                with _file_lock(self.json_file):
                    # Read existing data
                    if self.json_file.exists() and self.json_file.stat().st_size > 0:
                        data = json.loads(self.json_file.read_text())
                    else:
                        data = []

                    # Append new entry
                    data.append(entry)

                    # Write back to file with memory efficient streaming for large files
                    if len(data) > 1000:
                        self._write_json_streaming(data)
                    else:
                        self._atomic_write(self.json_file, json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error writing to JSON log file: {e}")

    def _atomic_write(self, path: pathlib.Path, content: str) -> None:
        """Write *content* to *path* atomically using a temporary file."""
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(content)
        tmp_path.replace(path)

    def _write_json_streaming(self, data: list):
        """Write JSON data using streaming to avoid memory issues atomically."""
        tmp_path = self.json_file.with_suffix(".json.tmp")
        with tmp_path.open("w") as f:
            f.write("[\n")
            for i, item in enumerate(data):
                json.dump(item, f, indent=2)
                if i < len(data) - 1:
                    f.write(",\n")
            f.write("\n]")
        tmp_path.replace(self.json_file)

    def _append_toml(self, entry: Dict[str, Any]):
        """Append entry to TOML log file"""
        if toml is None:
            return

        try:
            with self._thread_lock:
                with _file_lock(self.toml_file):
                    with self.toml_file.open("a") as f:
                        if entry.get("removed"):
                            f.write("# --REMOVED--\n")
                        f.write(toml.dumps({"package": entry}))
                        f.write("\n")
        except Exception as e:
            logger.error(f"Error writing to TOML log file: {e}")

    def query(
        self,
        name: Optional[str] = None,
        manager: Optional[str] = None,
        since: Optional[dt.date] = None,
    ) -> list:
        """Query the package log"""
        try:
            data = json.loads(self.json_file.read_text())
            results = data

            if name:
                results = [
                    e for e in results if name.lower() in e.get("name", "").lower()
                ]

            if manager:
                results = [e for e in results if e.get("manager") == manager]

            if since:
                results = [
                    e
                    for e in results
                    if dt.datetime.fromisoformat(e.get("date")).date() >= since
                ]

            return results
        except Exception as e:
            logger.error(f"Error querying log file: {e}")
            return []

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from log files"""
        try:
            data = json.loads(self.json_file.read_text())

            # Use more efficient counting
            total = len(data)
            installed = sum(1 for e in data if not e.get("removed", False))
            removed = sum(1 for e in data if e.get("removed", False))
            downloads = sum(1 for e in data if e.get("manager") == "download")

            stats = {
                "total": total,
                "installed": installed,
                "removed": removed,
                "downloads": downloads,
                "scope": self.config.scope,
            }
            return stats
        except Exception:
            return {
                "total": 0,
                "installed": 0,
                "removed": 0,
                "downloads": 0,
                "scope": self.config.scope,
            }
