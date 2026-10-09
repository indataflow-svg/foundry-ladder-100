"""Tests for ladder.password_policy."""

from ladder.password_policy import generate_passphrase, score, validate


def test_strong_password_passes() -> None:
    assert validate("Correct-Horse-9!") == []


def test_violations_listed() -> None:
    violations = validate("short1!")
    assert "too_short" in violations
    assert "no_uppercase" in violations


def test_score_bands() -> None:
    assert score("a") == 0
    assert score("Correct-Horse-9!") == 4


def test_generate_passphrase_valid() -> None:
    word_list = ["apple", "banana", "cherry", "date"]
    assert generate_passphrase(word_list, 2) == "apple banana"


def test_generate_passphrase_empty_word_list() -> None:
    word_list: list[str] = []
    try:
        generate_passphrase(word_list, 2)
    except ValueError as e:
        assert str(e) == "Word list cannot be empty"


def test_generate_passphrase_non_positive_count() -> None:
    word_list = ["apple", "banana", "cherry", "date"]
    try:
        generate_passphrase(word_list, 0)
    except ValueError as e:
        assert str(e) == "Count must be a positive integer"


def test_generate_passphrase_short_word_list() -> None:
    word_list = ["apple", "banana"]
    try:
        generate_passphrase(word_list, 3)
    except ValueError as e:
        assert str(e) == "Word list is shorter than the requested count"
