"""Tests for ladder.retry_policy."""

import random

import pytest

from ladder.retry_policy import backoff, equal_jitter, full_jitter


def test_backoff_caps() -> None:
    assert backoff(0) == 1.0
    assert backoff(3) == 8.0
    assert backoff(100, cap_s=60.0) == 60.0


def test_jitter_stays_in_bounds() -> None:
    rng = random.Random(7)
    top = backoff(2)
    assert 0.0 <= full_jitter(2, rng=rng) <= top
    assert top / 2.0 <= equal_jitter(2, rng=rng) <= top


def test_negative_attempt_rejected() -> None:
    with pytest.raises(ValueError):
        backoff(-1)
