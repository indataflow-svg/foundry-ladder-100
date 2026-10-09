"""Tests for can_sample_every."""

from ladder.log_sampler import can_sample_every


def test_accepts() -> None:
    assert can_sample_every(["a"], 1) is True


def test_rejects() -> None:
    assert can_sample_every(["a"], 0) is False
