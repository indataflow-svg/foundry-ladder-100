"""Locked behavior table for profile_sample (derived)."""

from ladder.csv_profiler import profile_sample


def test_table() -> None:
    assert profile_sample("a", 0, 0) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 0, 1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 0, 3) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 0, -1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 1, 0) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 1, 1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 1, 3) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 1, -1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 3, 0) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 3, 1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 3, 3) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
    assert profile_sample("a", 3, -1) == {
        "row_count": 0,
        "columns": {"a": {"count": 0, "nulls": 0, "uniques": 0}},
    }
