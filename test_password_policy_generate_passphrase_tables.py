"""Locked behavior table for generate_passphrase (derived)."""

import pytest

from ladder.password_policy import generate_passphrase


def test_table() -> None:
    assert generate_passphrase(["a"], 1, "a") == "a"
    assert generate_passphrase(["a"], 1, "b c") == "a"
    assert generate_passphrase(["a"], 1, "") == "a"


def test_rejects() -> None:
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 0, "a")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 0, "b c")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 0, "")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 3, "a")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 3, "b c")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], 3, "")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], -1, "a")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], -1, "b c")
    with pytest.raises(ValueError):
        generate_passphrase(["a"], -1, "")
