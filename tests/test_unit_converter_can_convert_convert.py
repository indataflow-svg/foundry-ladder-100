"""Tests for can_convert."""

from ladder.unit_converter import can_convert


def test_accepts() -> None:
    assert can_convert(0.0, "m", "m") is True


def test_rejects() -> None:
    assert can_convert(0.0, "m", "zzz") is False
