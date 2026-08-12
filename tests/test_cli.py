"""End-to-end tests for the CLI using Typer's ``CliRunner``.

``CliRunner`` invokes the app in-process and captures its output and exit
code, so we can assert on real command behaviour without spawning a slow
subprocess.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from clistart import __version__
from clistart.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_greet_default() -> None:
    result = runner.invoke(app, ["greet", "--name", "Ada"])
    assert result.exit_code == 0
    assert "Hello, Ada!" in result.output


def test_greet_repeats() -> None:
    result = runner.invoke(app, ["greet", "--name", "Ada", "--times", "3"])
    assert result.exit_code == 0
    assert result.output.count("Hello, Ada!") == 3


def test_process_uses_default_transform() -> None:
    # With no config file and no flag, the default "upper" transform applies.
    result = runner.invoke(app, ["process", "hello"])
    assert result.exit_code == 0
    assert "HELLO" in result.output


def test_process_transform_flag_wins(config_file: Path) -> None:
    # The config file says "lower", but the --transform flag must win.
    result = runner.invoke(
        app,
        ["process", "Hello", "--transform", "reverse", "--config", str(config_file)],
    )
    assert result.exit_code == 0
    assert "olleH" in result.output


def test_process_unknown_transform_exits_nonzero() -> None:
    # A bad transform should exit with a non-zero code, not crash.
    result = runner.invoke(app, ["process", "hello", "--transform", "sideways"])
    assert result.exit_code == 1
