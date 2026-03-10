"""Toxicity and content safety filtering.

Lightweight toxicity detection using keyword matching and pattern rules.
For production use, integrate with a dedicated content safety API
(Perspective API, Azure Content Safety, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class SafetyResult:
    is_safe: bool
    score: float
    categories: List[str]


class ToxicityGate:
    """Content safety filtering for LLM inputs and outputs."""

    _CATEGORIES = {
        "profanity": [
            # Placeholder — in production, use a comprehensive word list
            # or a content safety API
        ],
        "violence": [
            r"\b(?:kill|murder|attack|weapon|bomb|shoot)\b",
        ],
        "self_harm": [
            r"\b(?:suicide|self.harm|end\s+my\s+life)\b",
        ],
    }

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        import re
        self._compiled = {
            category: [re.compile(p, re.IGNORECASE) for p in patterns]
            for category, patterns in self._CATEGORIES.items()
            if patterns
        }

    def check(self, text: str) -> SafetyResult:
        flagged = []
        for category, patterns in self._compiled.items():
            for pattern in patterns:
                if pattern.search(text):
                    flagged.append(category)
                    break

        score = len(flagged) / max(len(self._compiled), 1)
        return SafetyResult(
            is_safe=score < self.threshold,
            score=score,
            categories=flagged,
        )
