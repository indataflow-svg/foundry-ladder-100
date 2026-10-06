"""Fixed-point money arithmetic (integer cents, no float drift)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """An amount in minor units with an ISO currency code."""

    cents: int
    currency: str = "USD"

    def _checked(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError(f"currency mismatch: {self.currency} vs {other.currency}")
        return other

    def add(self, other: Money) -> Money:
        """Add two amounts in the same currency."""
        self._checked(other)
        return Money(self.cents + other.cents, self.currency)

    def sub(self, other: Money) -> Money:
        """Subtract two amounts in the same currency."""
        self._checked(other)
        return Money(self.cents - other.cents, self.currency)

    def mul(self, factor: int) -> Money:
        """Scale by an integer factor."""
        return Money(self.cents * factor, self.currency)

    def format(self) -> str:
        """Render as ``<CUR> <major>.<minor>``, sign-aware."""
        sign = "-" if self.cents < 0 else ""
        whole, rest = divmod(abs(self.cents), 100)
        return f"{sign}{self.currency} {whole}.{rest:02d}"
