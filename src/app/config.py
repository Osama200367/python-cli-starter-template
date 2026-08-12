"""Layered configuration loading — the most reusable part of this template.

Real programs almost always need to read the same setting from more than one
place and agree on which source wins. Ours, from lowest priority to highest:

    defaults  <  config file  <  environment variables  <  CLI flags

So a value passed on the command line always beats an environment variable,
which beats the config file, which beats the built-in default. Read
:func:`load_settings` from top to bottom to watch each layer applied in turn.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

# Environment variables are read with this prefix, e.g. ``APP_GREETING``.
# A prefix keeps us from clashing with unrelated variables already in the
# shell (like a system-wide ``TRANSFORM``, however unlikely).
ENV_PREFIX = "APP_"


@dataclass
class Settings:
    """Every configurable option, together with its default value.

    Using a dataclass instead of a bare dict buys us three things at once:
    a documented list of valid settings, type hints, and the built-in
    defaults — all in one place. To add a new setting, add a field here.
    """

    greeting: str = "Hello"
    transform: str = "upper"


def _load_file(config_path: Path) -> dict[str, Any]:
    """Read a TOML config file and return its ``[app]`` table as a dict.

    Returns an empty dict if the file does not exist, so a missing config
    file simply means "no overrides" rather than an error.
    """
    if not config_path.exists():
        return {}
    with config_path.open("rb") as fh:  # tomllib requires binary mode
        data = tomllib.load(fh)
    # We namespace our settings under an [app] table so the file can grow
    # other sections later without colliding with these keys.
    return data.get("app", {})


def _load_env() -> dict[str, Any]:
    """Collect settings from environment variables named ``APP_<FIELD>``."""
    overrides: dict[str, Any] = {}
    for field in fields(Settings):
        env_name = f"{ENV_PREFIX}{field.name.upper()}"
        if env_name in os.environ:
            overrides[field.name] = os.environ[env_name]
    return overrides


def load_settings(
    config_path: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
) -> Settings:
    """Build a :class:`Settings` by merging every source in precedence order.

    Later layers overwrite earlier ones. ``cli_overrides`` should hold only
    the values the user actually set on the command line — pass ``None`` for
    flags they left off, so we don't clobber lower layers with a flag's own
    default value.
    """
    # Layer 1 (lowest priority): start from the dataclass defaults.
    defaults = Settings()
    values: dict[str, Any] = {
        field.name: getattr(defaults, field.name) for field in fields(Settings)
    }

    # Layer 2: apply the config file, if a path was given.
    if config_path is not None:
        values.update(_load_file(config_path))

    # Layer 3: apply environment variables.
    values.update(_load_env())

    # Layer 4 (highest priority): apply CLI flags, ignoring any left unset.
    if cli_overrides:
        values.update({key: val for key, val in cli_overrides.items() if val is not None})

    # Only keep keys that are real Settings fields, so a stray/typo'd key in
    # the TOML file can't crash the Settings(...) constructor below.
    known = {field.name for field in fields(Settings)}
    filtered = {key: val for key, val in values.items() if key in known}
    return Settings(**filtered)
