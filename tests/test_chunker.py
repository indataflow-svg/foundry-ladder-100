"""Tests for ladder.chunker."""

import pytest

from ladder.chunker import chunked


def test_overlap_char_chunks() -> None:
    assert chunked("abcdef", 4, overlap=2) == ["abcd", "cdef"]


def test_line_mode() -> None:
    assert chunked("a\nb\nc\n", 2, by_line=True) == ["a\nb\n", "c\n"]


def test_bad_overlap_rejected() -> None:
    with pytest.raises(ValueError):
        chunked("abc", 2, overlap=2)
