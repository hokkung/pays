"""Tests for article deduplication via content hash."""

import pytest

from app.services.news import compute_content_hash


class TestComputeContentHash:
    """Tests for the compute_content_hash function."""

    def test_consistent_hash(self) -> None:
        """Same title should produce the same hash."""
        assert compute_content_hash("Hello World") == compute_content_hash("Hello World")

    def test_whitespace_normalized(self) -> None:
        """Leading/trailing whitespace should not change the hash."""
        assert compute_content_hash("  Hello  ") == compute_content_hash("Hello")

    def test_case_normalized(self) -> None:
        """Case should not change the hash."""
        assert compute_content_hash("HELLO") == compute_content_hash("hello")

    def test_case_mixed(self) -> None:
        """Mixed case should normalize to the same hash."""
        assert compute_content_hash("HeLLo WoRLD") == compute_content_hash("hello world")

    def test_different_titles_different_hash(self) -> None:
        """Different titles should produce different hashes."""
        assert compute_content_hash("Title A") != compute_content_hash("Title B")

    def test_empty_string_hash(self) -> None:
        """Empty string should produce a valid hash."""
        h = compute_content_hash("")
        assert len(h) == 64  # SHA256 hex digest length

    @pytest.mark.parametrize(
        "title",
        [
            "Breaking: Markets Surge on Fed Cut",
            "Tech Stocks Rally as AI Demand Grows",
            "日経平均が急落",
            "",
            "A" * 1000,
        ],
        ids=["ascii", "long_ascii", "unicode", "empty", "very_long"],
    )
    def test_hash_is_hex_string(self, title: str) -> None:
        """Hash should always be a 64-character hex string."""
        h = compute_content_hash(title)
        assert len(h) == 64
        int(h, 16)  # Should not raise — valid hex
