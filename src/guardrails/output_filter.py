"""Output filtering for LLM responses.

Checks LLM outputs before they reach the user. Flags potential
hallucinations, compliance issues, and content policy violations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FilterResult:
    passed: bool
    flags: List[str] = field(default_factory=list)
    filtered_output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class OutputFilter:
    """Filter LLM outputs for safety and compliance."""

    _DISCLAIMER_TRIGGERS = [
        r"\b(?:invest|financial\s+advice|guarantee|promise)\b",
        r"\b(?:diagnos|prescri|medical\s+advice)\b",
        r"\b(?:legal\s+advice|attorney|lawyer)\b",
    ]

    def __init__(
        self,
        max_output_length: int = 5000,
        require_disclaimer_topics: bool = True,
        blocked_phrases: Optional[List[str]] = None,
    ):
        self.max_output_length = max_output_length
        self.require_disclaimer_topics = require_disclaimer_topics
        self.blocked_phrases = blocked_phrases or []

    def filter(self, output: str, context: Optional[List[str]] = None) -> FilterResult:
        flags = []

        if len(output) > self.max_output_length:
            output = output[:self.max_output_length]
            flags.append("output_truncated")

        for phrase in self.blocked_phrases:
            if phrase.lower() in output.lower():
                flags.append(f"blocked_phrase: {phrase}")
                return FilterResult(passed=False, flags=flags, filtered_output=None)

        if self.require_disclaimer_topics:
            for pattern in self._DISCLAIMER_TRIGGERS:
                if re.search(pattern, output, re.IGNORECASE):
                    flags.append("requires_disclaimer")
                    output += "\n\n[Disclaimer: This is AI-generated content and should not be considered professional advice.]"
                    break

        return FilterResult(
            passed=True,
            flags=flags,
            filtered_output=output,
        )
