from __future__ import annotations


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def column_top_values(text: str, column: str, limit: int) -> list[tuple[str, int]]:
    """Return the top values in a column, limited by the given limit."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    header = [cell.strip() for cell in lines[0].split(",")]
    if column not in header:
        return []
    column_index = header.index(column)
    values: dict[str, int] = {}
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split(",")]
        if len(cells) > column_index:
            value = cells[column_index]
            values[value] = values.get(value, 0) + 1
    sorted_values = sorted(values.items(), key=lambda x: x[1], reverse=True)
    return sorted_values[:limit]


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
