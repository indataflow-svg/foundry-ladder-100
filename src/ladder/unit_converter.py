"""Unit conversion for length, mass, and temperature (pure function)."""

from __future__ import annotations

_LENGTH_TO_M = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048}
_MASS_TO_KG = {"g": 0.001, "kg": 1.0, "lb": 0.45359237, "oz": 0.028349523125}
_AREA_TO_SQM = {"sqm": 1.0, "sqft": 0.09290304, "acre": 4046.8564224}


def _temperature_to_c(value: float, unit: str) -> float:
    if unit == "C":
        return value
    if unit == "F":
        return (value - 32.0) * 5.0 / 9.0
    if unit == "K":
        return value - 273.15
    raise ValueError(f"unknown temperature unit {unit!r}")


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between units of the same dimension; mixing dimensions raises."""
    if from_unit in _LENGTH_TO_M and to_unit in _LENGTH_TO_M:
        return value * _LENGTH_TO_M[from_unit] / _LENGTH_TO_M[to_unit]
    if from_unit in _MASS_TO_KG and to_unit in _MASS_TO_KG:
        return value * _MASS_TO_KG[from_unit] / _MASS_TO_KG[to_unit]
    if from_unit in _AREA_TO_SQM and to_unit in _AREA_TO_SQM:
        if value < 0:
            raise ValueError("Area cannot be negative")
        return value * _AREA_TO_SQM[from_unit] / _AREA_TO_SQM[to_unit]
    if from_unit in ("C", "F", "K") and to_unit in ("C", "F", "K"):
        celsius = _temperature_to_c(value, from_unit)
        if to_unit == "C":
            return celsius
        if to_unit == "F":
            return celsius * 9.0 / 5.0 + 32.0
        return celsius + 273.15
    raise ValueError(f"cannot convert {from_unit!r} to {to_unit!r}")
