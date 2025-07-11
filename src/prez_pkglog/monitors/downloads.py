"""Downloads folder monitoring"""
import logging
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

logger = logging.getLogger(__name__)


class DownloadsMonitor:
    """Monitor Downloads folder for new files"""

    def __init__(self, logger_instance=None):
        self.pkg_logger = logger_instance
        self.config = self.pkg_logger.config
        self.downloads_dir = Path(self.config.get("downloads_dir")).expanduser()
        self.observer = None

    def start(self):
        """Start monitoring Downloads folder"""
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog library not found. Download monitoring disabled.")
            return

        if not self.downloads_dir.exists():
            logger.warning(
                f"Downloads directory {self.downloads_dir} not found. "
                "Monitoring disabled."
            )
            return

        self.observer = Observer()
        self.observer.schedule(
            DownloadsEventHandler(self.pkg_logger),
            str(self.downloads_dir),
            recursive=False,
        )
        self.observer.start()
        logger.info(f"Monitoring downloads folder: {self.downloads_dir}")

    def stop(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()


class DownloadsEventHandler(FileSystemEventHandler):
    """Handle file system events in Downloads folder"""

    def __init__(self, logger_instance):
        self.pkg_logger = logger_instance
        self.config = self.pkg_logger.config

    def on_created(self, event):
        if not event.is_directory:
            self._log_download(str(event.src_path))

    def _log_download(self, file_path: str):
        """Log a downloaded file"""
        path = Path(file_path)

        # Get monitored extensions from config, with a fallback
        ext_str = self.config.get(
            "monitored_extensions", ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        )
        package_extensions = {f".{ext.strip().lstrip('.')}" for ext in ext_str.split(",")}

        if path.suffix.lower() in package_extensions:
            if self.pkg_logger:
                self.pkg_logger.log_package(
                    path.name,  # Use full filename
                    "download",
                    "install",
                    metadata={
                        "file_path": str(path),
                        "file_size": path.stat().st_size,
                        "file_type": path.suffix.lower(),
                    },
                )
