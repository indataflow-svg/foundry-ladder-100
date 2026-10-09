"""Tests for ladder.money."""

import pytest

from ladder.money import Money


def test_add_sub_format() -> None:
    total = Money(199).add(Money(1))
    assert total == Money(200)
    assert total.sub(Money(50)).format() == "USD 1.50"


def test_currency_mismatch_rejected() -> None:
    with pytest.raises(ValueError):
        Money(1, "USD").add(Money(1, "EUR"))


def test_negative_format() -> None:
    assert Money(-5).format() == "-USD 0.05"


def test_percentage() -> None:
    assert Money(199).percentage(10) == Money(20)
    assert Money(199).percentage(-10) == Money(-20)
    assert Money(199).percentage(10.5) == Money(20)
    assert Money(199, "EUR").percentage(10) == Money(20, "EUR")
    assert Money(199).percentage(0) == Money(0)
    assert Money(199).percentage(100) == Money(199)
