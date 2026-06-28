"""Tests for topic/keyword matching logic."""

import pytest

from app.services.news import matches_keywords


class TestMatchesKeywords:
    """Tests for the matches_keywords function."""

    @pytest.mark.parametrize(
        "text,keywords,expected",
        [
            ("AI infrastructure boom", "AI", True),
            ("Local news update", "AI", False),
            ("TSMC earnings report", "AI, semiconductor, TSMC", True),
            ("Random headline", "AI, semiconductor, TSMC", False),
            ("Semiconductor stocks rise", "semiconductor", True),
            ("SEMICONDUCTOR stocks rise", "semiconductor", True),
            ("The semiconductor sector", "semiconductor", True),
        ],
        ids=[
            "single_match",
            "single_no_match",
            "multi_any_match",
            "multi_no_match",
            "substring_match",
            "case_insensitive",
            "partial_word_match",
        ],
    )
    def test_matching(self, text: str, keywords: str, expected: bool) -> None:
        """Keyword matching should be case-insensitive and substring-based."""
        assert matches_keywords(text, keywords) == expected

    def test_empty_keywords(self) -> None:
        """Empty keyword string should return False."""
        assert matches_keywords("any text", "") is False

    def test_whitespace_only_keywords(self) -> None:
        """Keywords with only whitespace should return False."""
        assert matches_keywords("any text", "   ,  ") is False

    def test_multiple_matching_keywords(self) -> None:
        """Multiple matching keywords should still return True."""
        assert matches_keywords("AI semiconductor news", "AI, semiconductor") is True

    def test_special_characters_in_text(self) -> None:
        """Matching should work with special characters in text."""
        assert matches_keywords("NVDA: +5% on AI news!", "NVDA") is True
