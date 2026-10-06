"""Row-level diff of two CSV texts on a key column (pure function)."""

from __future__ import annotations


def _rows(text: str) -> tuple[list[str], list[dict[str, str]]]:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return [], []
    header = [cell.strip() for cell in lines[0].split(",")]
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split(",")]
        rows.append({name: cell for name, cell in zip(header, cells, strict=False)})
    return header, rows


def diff_csv(old: str, new: str, key: str) -> dict[str, list[dict[str, object]]]:
    """Added, removed, and changed rows keyed by ``key`` (changed carry before/after)."""
    _, old_rows = _rows(old)
    _, new_rows = _rows(new)
    old_by_key = {row[key]: row for row in old_rows}
    new_by_key = {row[key]: row for row in new_rows}
    added: list[dict[str, object]] = [
        dict(new_by_key[k]) for k in sorted(set(new_by_key) - set(old_by_key))
    ]
    removed: list[dict[str, object]] = [
        dict(old_by_key[k]) for k in sorted(set(old_by_key) - set(new_by_key))
    ]
    changed: list[dict[str, object]] = [
        {"key": k, "before": old_by_key[k], "after": new_by_key[k]}
        for k in sorted(set(old_by_key) & set(new_by_key))
        if old_by_key[k] != new_by_key[k]
    ]
    return {"added": added, "removed": removed, "changed": changed}
