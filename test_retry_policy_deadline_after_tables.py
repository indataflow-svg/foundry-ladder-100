"""Locked behavior table for deadline_after (derived)."""

from ladder.retry_policy import deadline_after


def test_table() -> None:
    assert deadline_after(0, 0.0, 0.0) == 0
    assert deadline_after(0, 0.0, 2.5) == 0
    assert deadline_after(0, 0.0, -1.5) == 0
    assert deadline_after(0, 2.5, 0.0) == 0
    assert deadline_after(0, 2.5, 2.5) == 0
    assert deadline_after(0, 2.5, -1.5) == 0
    assert deadline_after(0, -1.5, 0.0) == 0
    assert deadline_after(0, -1.5, 2.5) == 0
    assert deadline_after(0, -1.5, -1.5) == 0
    assert deadline_after(1, 0.0, 0.0) == 0.0
    assert deadline_after(1, 0.0, 2.5) == 0.0
    assert deadline_after(1, 0.0, -1.5) == -1.5
