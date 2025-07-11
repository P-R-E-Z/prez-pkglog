import json
import contextlib
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.prez_pkglog.config import Config, _ORIGINAL_HOME


class TestConfigPersistence:
    """Tests covering the new load/save logic in Config."""

    def test_save_and_load_roundtrip(self, tmp_path: Path):
        """Changes saved with save() should be re-loaded by a fresh instance."""
        cfg_path = tmp_path / "test.conf"

        # First instance – modify and save
        cfg1 = Config()
        cfg1.config_file = cfg_path  # redirect to temp file
        cfg1.set("enable_dnf_hooks", False)
        cfg1.save()

        # Second instance – should pick up persisted value
        cfg2 = Config()
        cfg2.config_file = cfg_path
        cfg2._load_config()  # force reload because we replaced path after __init__

        assert cfg2.get("enable_dnf_hooks") is False

    def test_load_ignores_unknown_keys(self, tmp_path: Path):
        cfg_path = tmp_path / "unknown.conf"
        cfg_path.write_text(json.dumps({"nonexistent": 123, "scope": "user"}))

        cfg = Config()
        cfg.config_file = cfg_path
        cfg._load_config()

        assert cfg.get("scope") == "user"
        assert cfg.get("nonexistent") is None

    def test_save_failure_logs_warning(self, tmp_path: Path):
        """save() should log a warning when IO fails."""
        cfg = Config()
        cfg.config_file = tmp_path / "failure.json"

        # Patch Path.open to raise OSError to simulate disk failure
        with patch("pathlib.Path.open", side_effect=OSError("disk full")):
            with patch("src.prez_pkglog.config.logger") as mock_logger:
                cfg.save()
                mock_logger.warning.assert_called()


class TestCLIScopePersistence:
    """Verify that CLI commands persist scope changes via Config.save()."""

    @pytest.mark.parametrize("command", ["status", "daemon", "setup", "export", "install", "remove", "query"])
    def test_cli_commands_call_save(self, command, tmp_path, monkeypatch):
        """Each CLI command should invoke Config.save() after setting scope."""
        from click.testing import CliRunner
        from src.prez_pkglog.cli import cli

        # Patch underlying Config class so that calls inside CLI pick up mock
        with (
            patch("src.prez_pkglog.config.Config") as mock_cfg_cls,
            patch("src.prez_pkglog.logger.PackageLogger"),
        ):
            cfg_instance = MagicMock()
            mock_cfg_cls.return_value = cfg_instance

            # CLI runner
            runner = CliRunner()

            # Build command arguments
            args = [command]
            if command in {"install", "remove"}:
                args += ["sample", "dnf"]
            if command == "query":
                args += ["--name", "sample"]
            # Ensure explicit scope flag
            args += ["--scope", "user"]

            extra_patches = []
            if command == "daemon":
                extra_patches.append(patch("src.prez_pkglog.monitors.downloads.DownloadsMonitor"))
                extra_patches.append(patch("time.sleep", side_effect=KeyboardInterrupt))

            with contextlib.ExitStack() as stack:
                for p in extra_patches:
                    stack.enter_context(p)

                runner.invoke(cli, args, catch_exceptions=False)

            # save() must have been called exactly once
            assert cfg_instance.save.called 