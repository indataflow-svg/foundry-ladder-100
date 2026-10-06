"""Backoff schedules (pure math; randomness is injectable)."""

from __future__ import annotations

import random


def backoff(attempt: int, base_s: float = 1.0, cap_s: float = 60.0) -> float:
    """Exponential backoff: ``base * 2**attempt`` bounded by ``cap``."""
    if attempt < 0:
        raise ValueError("attempt must be non-negative")
    return min(cap_s, base_s * (2.0**attempt))


def full_jitter(
    attempt: int, base_s: float = 1.0, cap_s: float = 60.0, rng: random.Random | None = None
) -> float:
    """Uniform sleep in ``[0, backoff]`` (AWS-style full jitter)."""
    source = rng if rng is not None else random.Random()
    return source.uniform(0.0, backoff(attempt, base_s, cap_s))


def equal_jitter(
    attempt: int, base_s: float = 1.0, cap_s: float = 60.0, rng: random.Random | None = None
) -> float:
    """Half backoff plus uniform noise over the other half."""
    source = rng if rng is not None else random.Random()
    half = backoff(attempt, base_s, cap_s) / 2.0
    return half + source.uniform(0.0, half)
