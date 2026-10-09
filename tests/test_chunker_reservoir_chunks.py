"""Tests for reservoir_chunks."""

import pytest

from ladder.chunker import reservoir_chunks


def test_composition() -> None:
    assert reservoir_chunks("a", 1, 0, 0, 0) == []


def test_rejects() -> None:
    with pytest.raises(ValueError):
        reservoir_chunks("a", 0, 0, 0, 0)
