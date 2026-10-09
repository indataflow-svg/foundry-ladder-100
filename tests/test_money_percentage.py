"""Tests for ladder.money.percentage."""

from ladder.money import Money


def test_percentage() -> None:
    assert Money(199).percentage(10) == Money(20)
    assert Money(199).percentage(-10) == Money(-20)
    assert Money(199).percentage(10.5) == Money(20)
    assert Money(199, "EUR").percentage(10) == Money(20, "EUR")
    assert Money(199).percentage(0) == Money(0)
    assert Money(199).percentage(100) == Money(199)
