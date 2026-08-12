"""Core logic for the app.

This module deliberately knows *nothing* about the command line, config
files, or logging. Keeping the real work here — separate from ``cli.py`` —
is one of the most useful habits this template teaches:

* You can unit-test the logic directly, without simulating a CLI.
* You can reuse these functions from a web app, a notebook, or another
  script, not just from Typer.

If you take one idea from this template into your own projects, let it be
this separation of "what the program does" from "how the user invokes it".
"""

from __future__ import annotations

from collections.abc import Callable

# The transforms we support, as a name -> function mapping. Using a dict
# keeps ``apply_transform`` tiny and makes extending it obvious: to add a new
# transform, just add one line here (and, ideally, a test for it).
TRANSFORMS: dict[str, Callable[[str], str]] = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "reverse": lambda s: s[::-1],
}


def apply_transform(text: str, mode: str) -> str:
    """Return ``text`` transformed according to ``mode``.

    ``mode`` must be one of the keys in :data:`TRANSFORMS` (for example
    ``"upper"``). We raise a clear ``ValueError`` for anything else, so the
    caller gets an actionable message instead of a mysterious ``KeyError``.
    """
    try:
        func = TRANSFORMS[mode]
    except KeyError:
        valid = ", ".join(sorted(TRANSFORMS))
        # ``from None`` hides the internal KeyError so the user sees only our
        # friendly message, not a confusing chained traceback.
        raise ValueError(f"Unknown transform {mode!r}. Valid options are: {valid}.") from None
    return func(text)


def word_count(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``.

    A small, obviously-correct helper — handy for showing how to test pure
    logic in ``tests/test_core.py``.
    """
    return len(text.split())
