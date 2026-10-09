"""Tests for can_column_top_values."""

from ladder.csv_profiler import can_column_top_values


def test_accepts() -> None:
    assert can_column_top_values("a,b\n1,x\n2,y\n3,y\n", "a", 2) is True


def test_rejects() -> None:
    assert can_column_top_values("a,b\n1,x\n2,y\n3,y\n", "c", 2) is False


def test_empty_csv_text() -> None:
    assert can_column_top_values("", "a", 2) is False


def test_csv_text_with_only_headers() -> None:
    assert can_column_top_values("a,b", "a", 2) is True
