"""Password validation with explicit violations + 0-4 strength score."""

from __future__ import annotations

import string

MIN_LENGTH = 12


def validate(password: str) -> list[str]:
    """Return violation codes; empty means the password passes."""
    violations: list[str] = []
    if len(password) < MIN_LENGTH:
        violations.append("too_short")
    if not any(c.islower() for c in password):
        violations.append("no_lowercase")
    if not any(c.isupper() for c in password):
        violations.append("no_uppercase")
    if not any(c.isdigit() for c in password):
        violations.append("no_digit")
    if not any(c in string.punctuation for c in password):
        violations.append("no_symbol")
    return violations


def score(password: str) -> int:
    """Strength score 0-4: length bands plus character-class diversity."""
    classes = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(c in string.punctuation for c in password),
        ]
    )
    length_points = 0 if len(password) < 8 else (1 if len(password) < MIN_LENGTH else 2)
    return min(4, length_points + min(2, classes // 2))


def generate_passphrase(word_list: list[str], count: int) -> str:
    """Generate a passphrase by joining the first count words from the word list."""
    if not word_list:
        raise ValueError("Word list cannot be empty")
    if count <= 0:
        raise ValueError("Count must be a positive integer")
    if len(word_list) < count:
        raise ValueError("Word list is shorter than the requested count")
    return " ".join(word_list[:count])
