"""Pattern redaction with an auditable report (pure function)."""

from __future__ import annotations

import re

DEFAULT_PATTERNS: dict[str, str] = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}


def redact(text: str, patterns: dict[str, str] | None = None) -> tuple[str, dict[str, int]]:
    """Replace each pattern hit with ``[REDACTED:<name>]``; return text + counts."""
    active = patterns if patterns is not None else DEFAULT_PATTERNS
    counts: dict[str, int] = {}
    redacted = text
    for name in sorted(active):
        found = re.findall(active[name], redacted)
        counts[name] = len(found)
        redacted = re.sub(active[name], f"[REDACTED:{name}]", redacted)
    return redacted, counts
