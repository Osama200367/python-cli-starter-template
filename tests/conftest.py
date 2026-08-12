"""Shared pytest fixtures.

Fixtures are reusable setup helpers. Placing them in ``conftest.py`` makes
them available to every test file in this folder automatically — no import
needed.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Write a temporary config.toml and return its path.

    ``tmp_path`` is a built-in pytest fixture that hands each test its own
    empty temporary directory, so tests never read or clobber your real
    config file.
    """
    path = tmp_path / "config.toml"
    path.write_text(
        '[clistart]\ngreeting = "Hey"\ntransform = "lower"\n',
        encoding="utf-8",
    )
    return path
