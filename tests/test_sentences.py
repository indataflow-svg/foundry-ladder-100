"""Tests for ladder.chunker.split_sentences."""

from ladder.chunker import split_sentences


def test_empty_input() -> None:
    assert split_sentences("") == []


def test_single_sentence() -> None:
    assert split_sentences("Hello, world!") == ["Hello, world!"]


def test_multiple_sentences() -> None:
    assert split_sentences("Hello, world! How are you? I'm fine.") == [
        "Hello, world!",
        "How are you?",
        "I'm fine.",
    ]


def test_no_sentence_boundaries() -> None:
    assert split_sentences("Hello world") == ["Hello world"]


def test_only_punctuation() -> None:
    assert split_sentences("! ") == []
    assert split_sentences("!? ") == []
    assert split_sentences("... ") == []
    assert split_sentences("!!! ") == []
    assert split_sentences("??? ") == []
