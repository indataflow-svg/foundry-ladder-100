"""Locked behavior table for split_sentences (derived)."""

from ladder.chunker import split_sentences


def test_table() -> None:
    assert split_sentences("a") == ["a"]
    assert split_sentences("b c") == ["b c"]
    assert split_sentences("") == []
