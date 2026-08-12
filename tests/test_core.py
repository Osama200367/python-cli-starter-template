"""Tests for the pure logic in ``app.core`` — no CLI or config involved.

These are the easiest tests to write precisely *because* core.py has no
dependencies on the command line or config files. That is the payoff of
keeping logic separate.
"""

from __future__ import annotations

import pytest

from clistart.core import apply_transform, word_count


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("upper", "HELLO WORLD"),
        ("lower", "hello world"),
        ("title", "Hello World"),
        ("reverse", "dlroW olleH"),
    ],
)
def test_apply_transform_modes(mode: str, expected: str) -> None:
    # parametrize runs this test once per row above — one assertion, four cases.
    assert apply_transform("Hello World", mode) == expected


def test_apply_transform_rejects_unknown_mode() -> None:
    # An unknown mode should raise a clear ValueError (not a raw KeyError).
    with pytest.raises(ValueError, match="Unknown transform"):
        apply_transform("hello", "sideways")


def test_word_count() -> None:
    assert word_count("one two three") == 3
    assert word_count("   ") == 0  # only whitespace -> zero words
