"""Locked public API surface (derived)."""

import ladder.password_policy as _module


def test_public_api_locked() -> None:
    live = {name for name in dir(_module) if not name.startswith("_")}
    assert {"score", "validate"} <= live
