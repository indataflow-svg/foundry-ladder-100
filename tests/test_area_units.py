"""Tests for area conversion."""

import pytest

from ladder.unit_converter import convert


def test_area_conversion() -> None:
    """Test conversion between sqm, sqft, and acre within the same dimension."""
    assert convert(1.0, "sqm", "sqft") == pytest.approx(10.7639104)
    assert convert(1.0, "sqft", "acre") == pytest.approx(2.29568411e-05)
    assert convert(1.0, "acre", "sqm") == pytest.approx(4046.8564224)


def test_cross_dimension_rejected() -> None:
    """Test that cross-dimension conversions with length raise a ValueError."""
    with pytest.raises(ValueError):
        convert(1.0, "m", "sqm")


def test_negative_values() -> None:
    """Test negative values for area units."""
    with pytest.raises(ValueError):
        convert(-1.0, "sqm", "sqft")


def test_non_numeric_inputs() -> None:
    """Test non-numeric inputs for area units."""
    with pytest.raises(TypeError):
        convert("one", "sqm", "sqft")  # type: ignore[arg-type]


def test_invalid_unit_strings() -> None:
    """Test invalid area unit strings."""
    with pytest.raises(ValueError):
        convert(1.0, "invalid", "sqm")
    with pytest.raises(ValueError):
        convert(1.0, "sqm", "invalid")
