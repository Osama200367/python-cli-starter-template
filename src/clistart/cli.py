"""The command-line interface, built with Typer.

Each command is just a Python function with type-hinted parameters; Typer
turns those into arguments, options, ``--help`` text, and validation. The
commands here stay thin on purpose — they gather input, then hand the real
work to :mod:`app.core`. That separation is what keeps the logic testable
on its own (see ``tests/test_core.py``).

Note: unlike the other modules, this one does *not* use
``from __future__ import annotations``. Typer inspects the real annotation
objects at runtime to build the CLI, and the postponed (string) annotations
that import would create can trip it up.
"""

import logging
from pathlib import Path

import typer

from clistart import __version__
from clistart.config import load_settings
from clistart.core import apply_transform, word_count
from clistart.logging_setup import configure_logging

# ``no_args_is_help`` shows the help screen when someone runs the bare
# command with no arguments — friendlier than printing an error.
app = typer.Typer(
    help="A beginner-friendly Python CLI starter template.",
    no_args_is_help=True,
    add_completion=False,
)

# Every module should log through its own named logger. "clistart" groups all
# of this project's log lines together.
log = logging.getLogger("clistart")

# Where we look for a config file by default, relative to the current
# directory. Users copy config.example.toml to config.toml to customize.
DEFAULT_CONFIG_PATH = Path("config.toml")


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug-level logs."),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Show only warnings and errors."),
) -> None:
    """Global options. This runs before whichever command the user chose."""
    configure_logging(verbose=verbose, quiet=quiet)


@app.command()
def version() -> None:
    """Print the installed version and exit."""
    typer.echo(__version__)


@app.command()
def greet(
    name: str = typer.Option("World", "--name", "-n", help="Who to greet."),
    times: int = typer.Option(1, "--times", "-t", min=1, help="How many times to greet."),
) -> None:
    """Say hello — the simplest command, to show basic argument wiring.

    The greeting word comes from your config (default "Hello"), so
    ``CLISTART_GREETING=Hi clistart greet --name Ada`` prints "Hi, Ada!".
    """
    settings = load_settings(config_path=DEFAULT_CONFIG_PATH)
    for _ in range(times):
        typer.echo(f"{settings.greeting}, {name}!")


@app.command()
def process(
    text: str = typer.Argument(..., help="The text to transform."),
    transform: str | None = typer.Option(
        None,
        "--transform",
        "-x",
        help="Transform mode: upper, lower, title, or reverse. "
        "Overrides the config-file value when given.",
    ),
    config: Path = typer.Option(
        DEFAULT_CONFIG_PATH,
        "--config",
        "-c",
        help="Path to a TOML config file.",
    ),
) -> None:
    """Transform TEXT using a config-driven mode — the richer example.

    This single command exercises the whole template at once: it loads
    layered config, logs its progress, and calls into the core logic. The
    transform mode is resolved with the usual precedence — the
    ``--transform`` flag beats the ``CLISTART_TRANSFORM`` environment variable,
    which beats the config file, which beats the built-in default.
    """
    # We pass the CLI value through ``cli_overrides`` and let load_settings
    # decide whether it wins — the precedence rules live in one place, not
    # scattered across the commands.
    settings = load_settings(
        config_path=config,
        cli_overrides={"transform": transform},
    )
    log.debug("Resolved settings: %s", settings)
    log.info("Applying %r transform to %d character(s).", settings.transform, len(text))

    try:
        result = apply_transform(text, settings.transform)
    except ValueError as exc:
        # Turn the library-level error into a clean message + exit code 1,
        # rather than dumping a traceback on the user.
        log.error("%s", exc)
        raise typer.Exit(code=1) from exc

    log.info("Input had %d word(s).", word_count(text))
    typer.echo(result)


if __name__ == "__main__":
    # Lets you run the CLI during development with:  python -m clistart.cli
    app()
