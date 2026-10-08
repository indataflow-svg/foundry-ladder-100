"""Tests for ladder.rate_limiter."""

from ladder.rate_limiter import TokenBucket


def test_burst_then_refuse() -> None:
    now = [0.0]
    bucket = TokenBucket(2, 1.0, clock=lambda: now[0])
    assert bucket.allow()
    assert bucket.allow()
    assert not bucket.allow()


def test_refill_over_time() -> None:
    now = [0.0]
    bucket = TokenBucket(1, 1.0, clock=lambda: now[0])
    assert bucket.allow()
    assert not bucket.allow()
    now[0] = 2.0
    assert bucket.allow()
