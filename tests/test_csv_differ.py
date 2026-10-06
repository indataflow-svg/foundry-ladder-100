"""Tests for ladder.csv_differ."""

from ladder.csv_differ import diff_csv


def test_added_removed_changed() -> None:
    old = "id,v\n1,a\n2,b\n3,c\n"
    new = "id,v\n2,B\n3,c\n4,d\n"
    diff = diff_csv(old, new, "id")
    assert [r["id"] for r in diff["added"]] == ["4"]
    assert [r["id"] for r in diff["removed"]] == ["1"]
    assert diff["changed"] == [
        {"key": "2", "before": {"id": "2", "v": "b"}, "after": {"id": "2", "v": "B"}}
    ]


def test_identical_is_empty() -> None:
    text = "id,v\n1,a\n"
    assert diff_csv(text, text, "id") == {"added": [], "removed": [], "changed": []}
