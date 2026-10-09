"""Smoke benchmark for sample_every (derived)."""

import time

from ladder.log_sampler import sample_every


def test_benchmark_budget() -> None:
    start = time.monotonic()
    for _ in range(1000):
        sample_every(["a"], 1)
    assert time.monotonic() - start < 30.0
