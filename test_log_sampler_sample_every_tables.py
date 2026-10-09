"""Locked behavior table for sample_every (derived)."""

import pytest

from ladder.log_sampler import sample_every


def test_table() -> None:
    assert sample_every(["a"], 1) == ["a"]
    assert sample_every(["a"], 3) == ["a"]
    assert sample_every(["b c"], 1) == ["b c"]
    assert sample_every(["b c"], 3) == ["b c"]
    assert sample_every([], 1) == []
    assert sample_every([], 3) == []


def test_rejects() -> None:
    with pytest.raises(ValueError):
        sample_every(["a"], 0)
    with pytest.raises(ValueError):
        sample_every(["a"], -1)
    with pytest.raises(ValueError):
        sample_every(["b c"], 0)
    with pytest.raises(ValueError):
        sample_every(["b c"], -1)
    with pytest.raises(ValueError):
        sample_every([], 0)
    with pytest.raises(ValueError):
        sample_every([], -1)
