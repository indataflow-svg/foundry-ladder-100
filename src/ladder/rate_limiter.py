"""Token-bucket rate limiter with an injectable clock (no sleeps)."""

from __future__ import annotations

from collections.abc import Callable


class TokenBucket:
    """Allow at most ``rate_per_s`` events with bursts up to ``capacity``."""

    def __init__(
        self, capacity: int, rate_per_s: float, clock: Callable[[], float] | None = None
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if rate_per_s <= 0:
            raise ValueError("rate_per_s must be positive")
        import time as _time

        self.capacity = capacity
        self.rate_per_s = rate_per_s
        self._clock = clock if clock is not None else _time.monotonic
        self._tokens = float(capacity)
        self._updated = self._clock()

    def allow(self, cost: int = 1) -> bool:
        """Consume ``cost`` tokens when available; otherwise refuse."""
        now = self._clock()
        self._tokens = min(
            float(self.capacity), self._tokens + (now - self._updated) * self.rate_per_s
        )
        self._updated = now
        if self._tokens >= cost:
            self._tokens -= cost
            return True
        return False
