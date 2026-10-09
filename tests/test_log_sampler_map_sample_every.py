"""Tests for map_sample_every."""

from ladder.log_sampler import map_sample_every, sample_every


def test_batch_matches_singles() -> None:
    items = [["a"], ["b c"]]
    assert map_sample_every(items, 1) == [sample_every(item, 1) for item in items]


def test_empty_batch() -> None:
    assert map_sample_every([], 1) == []
