"""Tests for ladder.password_policy."""

from ladder.password_policy import score, validate


def test_strong_password_passes() -> None:
    assert validate("Correct-Horse-9!") == []


def test_violations_listed() -> None:
    violations = validate("short1!")
    assert "too_short" in violations
    assert "no_uppercase" in violations


def test_score_bands() -> None:
    assert score("a") == 0
    assert score("Correct-Horse-9!") == 4
