"""Locked public API surface (derived)."""

import ladder.csv_profiler as _module


def test_public_api_locked() -> None:
    live = {name for name in dir(_module) if not name.startswith("_")}
    assert {"profile_csv"} <= live
