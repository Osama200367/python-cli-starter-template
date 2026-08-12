"""Extra tests for the transform logic in ``clistart.core.apply_transform``.

These complement (and do not touch) ``tests/test_core.py``. Every test name
is written so that the name alone tells you exactly what is being checked:
read the function name, know the behaviour.

Coverage here:
* happy path — each transform mode does what it says;
* edge cases — empty input, whitespace, unicode, boundaries, wrong types;
* failure case — an unknown mode raises a clear ``ValueError``.
"""

from __future__ import annotations

import pytest

from clistart.core import TRANSFORMS, apply_transform

ALL_MODES = ["upper", "lower", "title", "reverse"]


# --------------------------------------------------------------------------- #
# Happy path: each mode transforms typical text correctly.
# --------------------------------------------------------------------------- #


def test_upper_mode_converts_all_letters_to_uppercase() -> None:
    assert apply_transform("Hello World", "upper") == "HELLO WORLD"


def test_lower_mode_converts_all_letters_to_lowercase() -> None:
    assert apply_transform("Hello World", "lower") == "hello world"


def test_title_mode_capitalizes_the_first_letter_of_each_word() -> None:
    assert apply_transform("hello world", "title") == "Hello World"


def test_reverse_mode_returns_characters_in_reverse_order() -> None:
    assert apply_transform("Hello World", "reverse") == "dlroW olleH"


# --------------------------------------------------------------------------- #
# Edge case: empty input is valid for every mode and yields an empty string.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("mode", ALL_MODES)
def test_empty_string_input_returns_empty_string_for_every_mode(mode: str) -> None:
    assert apply_transform("", mode) == ""


# --------------------------------------------------------------------------- #
# Edge case: boundaries — single char, whitespace, idempotence, round-trips,
# multiple separators, and non-ASCII input.
# --------------------------------------------------------------------------- #


def test_single_character_reverse_returns_the_same_character() -> None:
    assert apply_transform("x", "reverse") == "x"


def test_reversing_a_string_twice_returns_the_original_string() -> None:
    assert apply_transform(apply_transform("Hello", "reverse"), "reverse") == "Hello"


def test_upper_mode_is_idempotent_on_already_uppercase_text() -> None:
    once = apply_transform("HELLO", "upper")
    assert apply_transform(once, "upper") == once == "HELLO"


def test_whitespace_only_input_is_left_unchanged_by_upper_mode() -> None:
    assert apply_transform("   ", "upper") == "   "


def test_title_mode_preserves_multiple_spaces_between_words() -> None:
    assert apply_transform("a  b", "title") == "A  B"


def test_upper_mode_uppercases_non_ascii_unicode_letters() -> None:
    assert apply_transform("café", "upper") == "CAFÉ"


# --------------------------------------------------------------------------- #
# Edge case: wrong types. Note the two different errors this can produce —
# the tests pin down which is which.
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("bad_text", [123, None, ["a"], 4.5])
def test_non_string_text_raises_type_error(bad_text: object) -> None:
    # The underlying str methods reject non-string input with a TypeError,
    # which we deliberately let propagate (it signals a programming error).
    with pytest.raises(TypeError):
        apply_transform(bad_text, "upper")  # type: ignore[arg-type]


def test_unhashable_mode_raises_type_error_not_value_error() -> None:
    # A list can't be a dict key, so the lookup fails with TypeError *before*
    # our KeyError guard runs — so this is a TypeError, not our ValueError.
    with pytest.raises(TypeError):
        apply_transform("hello", ["upper"])  # type: ignore[arg-type]


def test_hashable_but_unknown_mode_is_reported_as_value_error() -> None:
    # A hashable-but-unknown key (here an int) is caught by the guard and
    # re-raised as our friendly ValueError.
    with pytest.raises(ValueError, match="Unknown transform"):
        apply_transform("hello", 42)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Failure case: an unknown string mode raises ValueError and the message
# lists the valid options so the caller can correct it.
# --------------------------------------------------------------------------- #


def test_unknown_mode_raises_value_error_that_lists_every_valid_option() -> None:
    with pytest.raises(ValueError) as excinfo:
        apply_transform("hello", "sideways")

    message = str(excinfo.value)
    assert "sideways" in message  # names the bad mode
    for valid_mode in TRANSFORMS:  # and lists each supported one
        assert valid_mode in message
