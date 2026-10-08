"""Tests for ladder.unit_converter."""

import pytest

from ladder.unit_converter import convert


def test_length_and_mass() -> None:
    assert convert(1.0, "km", "m") == 1000.0
    assert convert(1.0, "lb", "kg") == pytest.approx(0.45359237)


def test_temperature() -> None:
    assert convert(32.0, "F", "C") == pytest.approx(0.0)
    assert convert(0.0, "C", "K") == pytest.approx(273.15)


def test_cross_dimension_rejected() -> None:
    with pytest.raises(ValueError):
        convert(1.0, "m", "kg")
