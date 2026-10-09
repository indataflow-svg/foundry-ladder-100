"""Tests for sampled_violations."""

import pytest

from ladder.password_policy import sampled_violations


def test_composition() -> None:
    assert sampled_violations("a", 0, 0) == []


def test_rejects() -> None:
    with pytest.raises(ValueError):
        sampled_violations("a", -1, 0)
