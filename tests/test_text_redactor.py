"""Tests for ladder.text_redactor."""

from ladder.text_redactor import redact


def test_email_redacted_with_report() -> None:
    text, counts = redact("mail bob@example.com twice bob@example.com")
    assert counts == {"email": 2, "ipv4": 0}
    assert "bob@" not in text
    assert text.count("[REDACTED:email]") == 2


def test_custom_patterns() -> None:
    text, counts = redact("id 123-45", {"ssn": r"\d{3}-\d{2}"})
    assert counts == {"ssn": 1}
    assert "[REDACTED:ssn]" in text
