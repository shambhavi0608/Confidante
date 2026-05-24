"""Sentence building utilities for gesture-to-text conversion."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class SentenceBuilder:
    """Maintain a bounded sentence with backspace, clear, and capitalization rules."""

    word_limit: int = 50

    def __post_init__(self) -> None:
        """Initialize the mutable sentence buffer."""
        self._tokens: List[str] = []

    def add_token(self, token: str) -> str:
        """Add a gesture token to the sentence and return the updated sentence."""
        normalized = token.strip()
        if not normalized or normalized == "NOTHING":
            return self.text
        if normalized == "DELETE":
            return self.backspace()
        if normalized == "SPACE":
            self._append_space()
            return self.text
        if self.word_count >= self.word_limit and normalized.isalnum():
            return self.text
        self._tokens.append(self._format_token(normalized))
        return self.text

    def backspace(self) -> str:
        """Remove the most recent token or trailing space and return the sentence."""
        if self._tokens:
            self._tokens.pop()
        return self.text

    def clear(self) -> str:
        """Clear all sentence content and return an empty string."""
        self._tokens.clear()
        return self.text

    @property
    def text(self) -> str:
        """Return the sentence as normalized display text."""
        sentence = "".join(self._tokens)
        sentence = re.sub(r"\s+", " ", sentence).strip()
        return self._auto_capitalize(sentence)

    @property
    def word_count(self) -> int:
        """Return the current number of words in the sentence."""
        return len([word for word in self.text.split(" ") if word])

    def _append_space(self) -> None:
        """Append one space unless the sentence is empty or already spaced."""
        if self._tokens and not self._tokens[-1].endswith(" "):
            self._tokens.append(" ")

    def _format_token(self, token: str) -> str:
        """Format a gesture token as text suitable for sentence composition."""
        if len(token) == 1:
            return token.lower()
        return token.lower()

    def _auto_capitalize(self, sentence: str) -> str:
        """Capitalize the first letter and letters after sentence punctuation."""
        if not sentence:
            return sentence
        chars = list(sentence)
        capitalize_next = True
        for index, char in enumerate(chars):
            if char.isalpha() and capitalize_next:
                chars[index] = char.upper()
                capitalize_next = False
            elif char in ".!?":
                capitalize_next = True
            elif not char.isspace():
                capitalize_next = False
        return "".join(chars)
