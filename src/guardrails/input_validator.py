"""Input validation for GenAI requests.

Validates user inputs before they reach the LLM. Checks for PII,
prompt injection attempts, and content policy violations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ValidationStatus(Enum):
    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"


@dataclass
class ValidationResult:
    status: ValidationStatus
    issues: List[str] = field(default_factory=list)
    sanitized_input: Optional[str] = None


class InputValidator:
    """Validate and sanitize user inputs before LLM processing."""

    _INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous",
        r"you\s+are\s+now",
        r"system\s*:\s*",
        r"\[INST\]|\[/INST\]",
        r"<\|im_start\|>",
    ]

    _PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "phone": r"(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    }

    def __init__(self, block_pii: bool = True, block_injection: bool = True, max_length: int = 10000):
        self.block_pii = block_pii
        self.block_injection = block_injection
        self.max_length = max_length

    def validate(self, text: str) -> ValidationResult:
        issues = []

        if len(text) > self.max_length:
            return ValidationResult(
                status=ValidationStatus.BLOCK,
                issues=[f"Input exceeds maximum length ({len(text)} > {self.max_length})"],
            )

        # Check injection
        if self.block_injection:
            for pattern in self._INJECTION_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    issues.append(f"Potential prompt injection detected")
                    return ValidationResult(status=ValidationStatus.BLOCK, issues=issues)

        # Check PII
        if self.block_pii:
            for pii_type, pattern in self._PII_PATTERNS.items():
                if re.search(pattern, text):
                    issues.append(f"PII detected: {pii_type}")

        if issues:
            return ValidationResult(status=ValidationStatus.WARN, issues=issues, sanitized_input=text)

        return ValidationResult(status=ValidationStatus.PASS, sanitized_input=text)
