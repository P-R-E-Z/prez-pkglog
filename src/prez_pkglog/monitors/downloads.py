"""Downloads folder monitoring"""

from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class DownloadsMonitor:
    """Monitor Downloads folder for new files"""

    def __init__(self, logger=None):
        self.logger = logger
        self.downloads_dir = Path.home() / "Downloads"
        self.observer = None

    def start(self):
        """Start monitoring Downloads folder"""
        if not WATCHDOG_AVAILABLE:
            print("Warning: watchdog not available. Download monitoring disabled.")
            return

        if not self.downloads_dir.exists():
            print(f"Warning: Downloads directory {self.downloads_dir} not found.")
            return

        self.observer = Observer()
        self.observer.schedule(
            DownloadsEventHandler(self.logger), str(self.downloads_dir), recursive=False
        )
        self.observer.start()
        print(f"Monitoring Downloads folder: {self.downloads_dir}")

    def stop(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()


class DownloadsEventHandler(FileSystemEventHandler):
    """Handle file system events in Downloads folder"""

    def __init__(self, logger):
        self.logger = logger

    def on_created(self, event):
        if not event.is_directory:
            self._log_download(str(event.src_path))

    def _log_download(self, file_path: str):
        """Log a downloaded file"""
        path = Path(file_path)

        # Only log certain file types
        package_extensions = {".rpm", ".deb", ".pkg", ".exe", ".msi", ".dmg"}
        if path.suffix.lower() in package_extensions:
            if self.logger:
                self.logger.log_package(
                    path.stem,
                    "download",
                    "install",
                    metadata={
                        "file_path": str(path),
                        "file_size": path.stat().st_size,
                        "file_type": path.suffix.lower(),
                    },
                )
