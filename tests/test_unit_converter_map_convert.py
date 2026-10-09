"""Tests for map_convert."""

from ladder.unit_converter import convert, map_convert


def test_batch_matches_singles() -> None:
    items = [0.0, 2.5]
    assert map_convert(items, "m", "m") == [convert(item, "m", "m") for item in items]


def test_empty_batch() -> None:
    assert map_convert([], "m", "m") == []
