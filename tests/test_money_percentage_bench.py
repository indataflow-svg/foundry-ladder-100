"""Smoke benchmark for percentage (derived)."""

import time

from ladder.money import Money


def test_benchmark_budget() -> None:
    start = time.monotonic()
    for _ in range(1000):
        Money(100).percentage(0.0)
    assert time.monotonic() - start < 30.0
