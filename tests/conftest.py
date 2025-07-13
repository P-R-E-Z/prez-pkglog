from pathlib import Path

import pytest


@pytest.fixture()
def tmp_home(monkeypatch, tmp_path: Path):
    """Fixture that patches Path.home() and HOME so code writes under tmppath."""

    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    return tmp_path
