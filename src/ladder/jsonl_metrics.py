"""Group-by aggregation over JSONL text (pure function, no I/O)."""

from __future__ import annotations

import json
from typing import Any


def aggregate(text: str, group_key: str, value_key: str) -> dict[str, dict[str, float]]:
    """Aggregate numeric ``value_key`` per ``group_key``: count/sum/mean/min/max."""
    groups: dict[str, list[float]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        record: dict[str, Any] = json.loads(line)
        group = str(record[group_key])
        groups.setdefault(group, []).append(float(record[value_key]))
    result: dict[str, dict[str, float]] = {}
    for group, values in sorted(groups.items()):
        result[group] = {
            "count": float(len(values)),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
    return result
