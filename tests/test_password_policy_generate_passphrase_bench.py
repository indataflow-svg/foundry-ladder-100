"""Smoke benchmark for generate_passphrase (derived)."""

import time

from ladder.password_policy import generate_passphrase


def test_benchmark_budget() -> None:
    start = time.monotonic()
    for _ in range(1000):
        generate_passphrase(["a"], 1)
    assert time.monotonic() - start < 30.0
