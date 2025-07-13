"""Downloads folder monitoring"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# Assume watchdog is unavailable until proven otherwise so that the
# constant is defined for both runtime *and* static-analysis passes.
WATCHDOG_AVAILABLE = False

if TYPE_CHECKING:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
else:
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        WATCHDOG_AVAILABLE = True
    except ImportError:
        WATCHDOG_AVAILABLE = False

        class FileSystemEventHandler:  # type: ignore
            """Fallback no-op event handler when watchdog is unavailable."""

            def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
                pass

            # Define the methods used in DownloadsEventHandler to avoid attribute errors
            def on_created(self, event):  # noqa: D401
                pass

        class Observer:
            """Fallback no-op observer when watchdog is unavailable."""

            def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
                pass

            def schedule(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401
                pass

            def start(self) -> None:  # noqa: D401
                pass

            def stop(self) -> None:  # noqa: D401
                pass

            def join(self) -> None:  # noqa: D401
                pass


logger = logging.getLogger(__name__)


class DownloadsMonitor:
    """Monitor the user’s *Downloads* folder for new package files."""

    def __init__(self, logger_instance: Any):
        if logger_instance is None:
            raise ValueError("logger_instance must be provided")

        self.pkg_logger = logger_instance
        self.config = self.pkg_logger.config
        self.downloads_dir = Path(self.config.get("downloads_dir")).expanduser()
        self.observer: Optional[Any] = None

    def start(self):
        """Start monitoring Downloads folder"""
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog library not found. Download monitoring disabled.")
            return

        if not self.downloads_dir.exists():
            logger.warning(
                f"Downloads directory {self.downloads_dir} not found. Monitoring disabled."
            )
            return

        # Local variable avoids “None” type issues in static analysis.
        observer = Observer()
        observer.schedule(
            DownloadsEventHandler(self.pkg_logger),
            str(self.downloads_dir),
            recursive=False,
        )
        observer.start()

        self.observer = observer
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

        ext_str = self.config.get(
            "monitored_extensions", ".rpm,.deb,.pkg,.exe,.msi,.dmg"
        )
        package_extensions = {
            f".{ext.strip().lstrip('.')}" for ext in ext_str.split(",")
        }

        if path.suffix.lower() in package_extensions:
            if self.pkg_logger:
                try:
                    file_size = path.stat().st_size
                except OSError as e:
                    logger.warning(f"Could not get file size for {path}: {e}")
                    file_size = 0

                self.pkg_logger.log_package(
                    path.name,
                    "download",
                    "install",
                    metadata={
                        "file_path": str(path),
                        "file_size": file_size,
                        "file_type": path.suffix.lower(),
                    },
                )
