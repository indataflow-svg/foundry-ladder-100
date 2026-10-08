"""Tests for ladder.config_loader."""

import pytest

from ladder.config_loader import ConfigError, load

SCHEMA = {
    "host": {"type": str, "required": True},
    "port": {"type": int, "required": False, "default": 80},
}


def test_layers_merge_and_defaults() -> None:
    assert load([{"host": "a"}, {"port": 8080}], SCHEMA) == {"host": "a", "port": 8080}
    assert load([{"host": "a"}], SCHEMA)["port"] == 80


def test_missing_required_rejected() -> None:
    with pytest.raises(ConfigError):
        load([{}], SCHEMA)


def test_wrong_type_and_unknown_rejected() -> None:
    with pytest.raises(ConfigError):
        load([{"host": "a", "port": "x"}], SCHEMA)
    with pytest.raises(ConfigError):
        load([{"host": "a", "zzz": 1}], SCHEMA)
