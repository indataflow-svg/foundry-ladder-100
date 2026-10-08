"""Tiny time-bucket and rolling statistics (pure functions)."""

from __future__ import annotations


def resample(points: list[tuple[int, float]], bucket: int) -> list[tuple[int, float]]:
    """Mean value per ``bucket``-wide timestamp bucket, ordered by bucket."""
    if bucket <= 0:
        raise ValueError("bucket must be positive")
    buckets: dict[int, list[float]] = {}
    for stamp, value in points:
        key = (stamp // bucket) * bucket
        buckets.setdefault(key, []).append(value)
    return [(key, sum(values) / len(values)) for key, values in sorted(buckets.items())]


def rolling_mean(values: list[float], window: int) -> list[float]:
    """Trailing mean over ``window``; first entries use the available prefix."""
    if window <= 0:
        raise ValueError("window must be positive")
    result: list[float] = []
    for index in range(len(values)):
        part = values[max(0, index - window + 1) : index + 1]
        result.append(sum(part) / len(part))
    return result
