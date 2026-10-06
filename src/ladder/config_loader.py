"""Layered configuration with schema validation (pure function)."""

from __future__ import annotations

from typing import Any


class ConfigError(Exception):
    """Raised when a layer violates the schema."""


def load(layers: list[dict[str, Any]], schema: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Merge ``layers`` in order, then validate against ``schema``.

    Schema entry: ``{"type": <type>, "required": <bool>, "default": <value>}``.
    Later layers win. Missing required keys and wrong types raise
    :class:`ConfigError`; optional keys fall back to ``default`` (None).
    """
    merged: dict[str, Any] = {}
    for layer in layers:
        merged.update(layer)
    result: dict[str, Any] = {}
    for key, spec in schema.items():
        if key in merged:
            value = merged[key]
            expected = spec.get("type", object)
            if expected is not object and not isinstance(value, expected):
                raise ConfigError(f"{key!r} must be {expected.__name__}")
            result[key] = value
        elif spec.get("required", False):
            raise ConfigError(f"missing required key {key!r}")
        else:
            result[key] = spec.get("default")
    unknown = sorted(set(merged) - set(schema))
    if unknown:
        raise ConfigError(f"unknown keys: {', '.join(unknown)}")
    return result
