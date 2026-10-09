"""Locked public API surface (derived)."""

import ladder.log_sampler as _module


def test_public_api_locked() -> None:
    live = {name for name in dir(_module) if not name.startswith("_")}
    assert {"reservoir_sample"} <= live
