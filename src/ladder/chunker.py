"""Text chunking with overlap, by characters or lines (pure function)."""

from __future__ import annotations

import re


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences based on . ! ? followed by whitespace."""
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out: list[str] = []
    for sentence in sentences:
        stripped = sentence.strip()
        if stripped and not re.fullmatch(r"[.!?\s]+", stripped):
            out.append(stripped)
    return out


def chunked(text: str, size: int, overlap: int = 0, *, by_line: bool = False) -> list[str]:
    """Split ``text`` into ``size``-unit chunks with ``overlap``-unit overlap."""
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= overlap < size:
        raise ValueError("overlap must satisfy 0 <= overlap < size")
    units: list[str] = text.splitlines(keepends=True) if by_line else list(text)
    if not units:
        return []
    step = size - overlap
    chunks: list[str] = []
    for start in range(0, len(units), step):
        part = units[start : start + size]
        chunks.append("".join(part))
        if start + size >= len(units):
            break
    return [c for c in chunks if c]


def reservoir_chunks(text: str, size: int, overlap: int, k: int, seed: int) -> list[str]:
    """Large files cannot be chunked wholesale."""
    from ladder.log_sampler import reservoir_sample

    return reservoir_sample(chunked(text, size, overlap), k, seed)
