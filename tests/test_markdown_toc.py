"""Tests for ladder.markdown_toc."""

from ladder.markdown_toc import toc


def test_headings_and_anchors() -> None:
    entries = toc("# Hello World\n\n## Hello World\n")
    assert entries[0] == {"level": 1, "title": "Hello World", "anchor": "hello-world"}
    assert entries[1]["anchor"] == "hello-world-1"


def test_fences_ignored() -> None:
    assert toc("```\n# not a heading\n```\n") == []
