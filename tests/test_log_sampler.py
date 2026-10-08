"""Tests for ladder.log_sampler."""

import pytest

from ladder.log_sampler import reservoir_sample


def test_deterministic_per_seed() -> None:
    lines = [f"line {i}" for i in range(100)]
    assert reservoir_sample(lines, 5, seed=3) == reservoir_sample(lines, 5, seed=3)
    assert len(reservoir_sample(lines, 5, seed=3)) == 5


def test_small_input_kept_whole() -> None:
    assert reservoir_sample(["a", "b"], 5) == ["a", "b"]


def test_negative_k_rejected() -> None:
    with pytest.raises(ValueError):
        reservoir_sample(["a"], -1)
