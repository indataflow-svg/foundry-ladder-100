"""Tests for ladder.csv_profiler."""

from ladder.csv_profiler import profile_csv


def test_row_count_and_columns() -> None:
    report = profile_csv("a,b\n1,x\n2,y\n3,y\n")
    assert report["row_count"] == 3
    assert set(report["columns"]) == {"a", "b"}


def test_numeric_stats_and_nulls() -> None:
    report = profile_csv("a,b\n1,x\n, y\n3,\n")
    assert report["columns"]["a"]["nulls"] == 1
    assert report["columns"]["a"]["numeric"]["mean"] == 2.0
    assert report["columns"]["b"]["uniques"] == 2


def test_empty_text() -> None:
    assert profile_csv("") == {"row_count": 0, "columns": {}}
