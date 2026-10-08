"""Tests for ladder.log_sampler.sample_every."""

import pytest

from ladder.log_sampler import sample_every


def test_sample_every_returns_every_nth_line() -> None:
    lines = [f"line {i}" for i in range(10)]
    assert sample_every(lines, 2) == ["line 0", "line 2", "line 4", "line 6", "line 8"]


def test_sample_every_with_n_1_returns_identity() -> None:
    lines = [f"line {i}" for i in range(5)]
    assert sample_every(lines, 1) == lines


def test_sample_every_with_non_positive_n_raises() -> None:
    with pytest.raises(ValueError):
        sample_every(["line 1", "line 2"], 0)
    with pytest.raises(ValueError):
        sample_every(["line 1", "line 2"], -1)


def test_sample_every_with_empty_input_returns_empty_list() -> None:
    assert sample_every([], 2) == []


def test_sample_every_with_n_larger_than_lines_returns_first_line() -> None:
    lines = ["line 1", "line 2"]
    assert sample_every(lines, 3) == ["line 1"]
