"""Tests for ladder.jsonl_metrics."""

from ladder.jsonl_metrics import aggregate


def test_group_means() -> None:
    text = '{"g": "a", "v": 1}\n{"g": "b", "v": 4}\n{"g": "a", "v": 3}\n'
    result = aggregate(text, "g", "v")
    assert result["a"] == {"count": 2.0, "sum": 4.0, "mean": 2.0, "min": 1.0, "max": 3.0}
    assert result["b"]["count"] == 1.0


def test_blank_lines_skipped() -> None:
    assert aggregate('\n{"g": "a", "v": 2}\n\n', "g", "v")["a"]["sum"] == 2.0
