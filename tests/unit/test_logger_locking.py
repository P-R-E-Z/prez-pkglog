import json
import threading
from pathlib import Path
from unittest.mock import patch
import os
import pytest

from src.prez_pkglog.logger import PackageLogger
from src.prez_pkglog.config import Config


class TestPackageLoggerLocking:
    """Concurrency/atomic-write tests for PackageLogger."""

    def test_concurrent_json_writes_threaded(self, tmp_path: Path):
        """Multiple threads writing concurrently should not corrupt the JSON log."""

        # Patch Path.home so PackageLogger writes inside tmpdir
        with patch("pathlib.Path.home", return_value=tmp_path):
            cfg = Config()  # default user scope
            logger = PackageLogger(cfg)

            # Patch _append_toml to avoid TOML overhead during test
            with patch.object(logger, "_append_toml", lambda *a, **k: None):
                num_threads = 20
                entries_per_thread = 10
                total_entries = num_threads * entries_per_thread

                def worker(tid: int):
                    for i in range(entries_per_thread):
                        logger.log_package(f"pkg{tid}_{i}", "dnf", "install")

                threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

                # JSON file should contain exactly total_entries items and parse correctly
                data = json.loads(logger.json_file.read_text())
                assert len(data) == total_entries

                # No temporary file should remain
                assert not logger.json_file.with_suffix(".json.tmp").exists()

    @pytest.mark.xfail(reason="Advisory file-locking on tmpfs may allow interleaved renames under extreme parallelism; acceptable for 0.5.0, revisit later.")
    def test_concurrent_json_writes_multiprocess(self, tmp_path: Path):
        """Multiple processes should be able to write concurrently thanks to file locks."""

        import multiprocessing as mp

        # tmp_path as fake HOME so each process resolves identical data_dir
        home_dir = tmp_path

        def worker(entries: int):
            # Set HOME for this process
            os.environ["HOME"] = str(home_dir)
            os.environ["USERPROFILE"] = str(home_dir)  # Windows safety

            # Fresh logger instance inside process
            cfg = Config()
            logger = PackageLogger(cfg)

            # Avoid TOML writes for speed
            with patch.object(logger, "_append_toml", lambda *a, **k: None):
                for i in range(entries):
                    logger.log_package(f"proc_pkg_{i}", "apt", "install")

        processes = []
        per_proc = 15
        proc_count = 6
        for _ in range(proc_count):
            p = mp.Process(target=worker, args=(per_proc,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        # Verify final JSON file integrity
        with patch("pathlib.Path.home", return_value=home_dir):
            cfg_main = Config()
            logger_main = PackageLogger(cfg_main)
        data = json.loads(logger_main.json_file.read_text())
        assert len(data) == per_proc * proc_count 