"""Column profiler for CSV text (pure function, no I/O)."""

from __future__ import annotations


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def profile_csv(text: str) -> dict[str, object]:
    """Profile CSV text: row count, per-column nulls, uniques, numeric stats."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return {"row_count": 0, "columns": {}}
    header = [cell.strip() for cell in lines[0].split(",")]
    columns: dict[str, list[str]] = {name: [] for name in header}
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split(",")]
        for name, cell in zip(header, cells, strict=False):
            columns[name].append(cell)
    profile: dict[str, object] = {}
    for name, values in columns.items():
        non_empty = [v for v in values if v != ""]
        numbers = [float(v) for v in non_empty if _is_number(v)]
        entry: dict[str, object] = {
            "count": len(values),
            "nulls": len(values) - len(non_empty),
            "uniques": len(set(non_empty)),
        }
        if numbers and len(numbers) == len(non_empty) and non_empty:
            entry["numeric"] = {
                "min": min(numbers),
                "max": max(numbers),
                "mean": sum(numbers) / len(numbers),
            }
        profile[name] = entry
    return {"row_count": len(lines) - 1, "columns": profile}


def column_top_values(text: str, column: str, n: int) -> list[tuple[str, int]]:
    """Return the top n values and their counts for the specified column."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Empty CSV text")
    header = [cell.strip() for cell in lines[0].split(",")]
    if column not in header:
        raise ValueError(f"Column {column!r} not found")
    if n < 0:
        raise ValueError("n must be non-negative")
    column_index = header.index(column)
    values = [line.split(",")[column_index].strip() for line in lines[1:]]
    value_counts: dict[str, int] = {}
    for value in values:
        if value in value_counts:
            value_counts[value] += 1
        else:
            value_counts[value] = 1
    sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_values[:n]


def can_column_top_values(text: str, column: str, n: int) -> bool:
    """True when column_top_values accepts these arguments (never raises)."""
    try:
        column_top_values(text, column, n)
    except ValueError:
        return False
    return True
