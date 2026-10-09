"""Deterministic reservoir sampling over log lines (seeded RNG)."""

from __future__ import annotations

import random


def reservoir_sample(lines: list[str], k: int, seed: int = 0) -> list[str]:
    """Uniform sample of up to ``k`` lines; same seed always wins the same lines."""
    if k < 0:
        raise ValueError("k must be non-negative")
    rng = random.Random(seed)  # nosec B311  # seeded determinism, not security randomness
    reservoir: list[str] = []
    for index, line in enumerate(lines):
        if index < k:
            reservoir.append(line)
        else:
            pick = rng.randrange(index + 1)
            if pick < k:
                reservoir[pick] = line
    return reservoir


def map_sample_every(items: list[list[str]], n: int) -> list[list[str]]:
    """Apply sample_every to each item (deterministic batch)."""
    return [sample_every(item, n) for item in items]


def sample_every(lines: list[str], n: int) -> list[str]:
    """Return every nth line from the first; n=1 is identity; non-positive n raises; empty input yields []."""
    if n <= 0:
        raise ValueError("n must be positive")
    return lines[::n]
