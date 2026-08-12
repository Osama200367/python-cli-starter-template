"""Tests for the layered configuration loader.

These lock down the precedence rules — the behaviour most worth protecting:

    CLI  >  environment variables  >  config file  >  defaults
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config import Settings, load_settings


def test_defaults_when_nothing_is_set(tmp_path: Path) -> None:
    # Point at a file that doesn't exist -> we fall back to pure defaults.
    settings = load_settings(config_path=tmp_path / "missing.toml")
    assert settings == Settings()  # greeting="Hello", transform="upper"


def test_file_overrides_defaults(config_file: Path) -> None:
    settings = load_settings(config_path=config_file)
    assert settings.greeting == "Hey"
    assert settings.transform == "lower"


def test_env_overrides_file(config_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # The env var should beat the value written in the file...
    monkeypatch.setenv("APP_TRANSFORM", "title")
    settings = load_settings(config_path=config_file)
    assert settings.transform == "title"
    # ...but a setting the env var doesn't touch still comes from the file.
    assert settings.greeting == "Hey"


def test_cli_overrides_everything(config_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_TRANSFORM", "title")
    settings = load_settings(
        config_path=config_file,
        cli_overrides={"transform": "reverse"},
    )
    assert settings.transform == "reverse"  # CLI wins over env and file


def test_cli_none_values_are_ignored(config_file: Path) -> None:
    # A None CLI value means "flag not provided" and must NOT override lower
    # layers — otherwise every unset flag would wipe out the config file.
    settings = load_settings(
        config_path=config_file,
        cli_overrides={"transform": None},
    )
    assert settings.transform == "lower"  # still the file's value
