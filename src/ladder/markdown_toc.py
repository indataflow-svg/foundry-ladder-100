"""Markdown table-of-contents builder (fences excluded, duplicates suffixed)."""

from __future__ import annotations

import re


def _anchor(title: str) -> str:
    slug = re.sub(r"[^a-z0-9 _-]", "", title.lower()).strip().replace(" ", "-")
    return re.sub(r"-+", "-", slug)


def toc(markdown: str) -> list[dict[str, object]]:
    """Headings as ``{level, title, anchor}``; fenced code blocks ignored."""
    entries: list[dict[str, object]] = []
    seen: dict[str, int] = {}
    in_fence = False
    for line in markdown.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if not match:
            continue
        title = match.group(2).strip()
        anchor = _anchor(title)
        seen[anchor] = seen.get(anchor, 0) + 1
        if seen[anchor] > 1:
            anchor = f"{anchor}-{seen[anchor] - 1}"
        entries.append({"level": len(match.group(1)), "title": title, "anchor": anchor})
    return entries
