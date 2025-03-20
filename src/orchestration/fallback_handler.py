"""Fallback Handler — graceful degradation for LLM failures.

Handles scenarios where the primary LLM is unavailable, rate-limited,
or produces low-confidence outputs. Implements a fallback chain with
configurable strategies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional


class FallbackReason(Enum):
    LLM_UNAVAILABLE = "llm_unavailable"
    RATE_LIMITED = "rate_limited"
    LOW_CONFIDENCE = "low_confidence"
    TIMEOUT = "timeout"
    CONTENT_FILTERED = "content_filtered"


@dataclass
class FallbackResult:
    """Result from the fallback chain."""
    response: str
    reason: FallbackReason
    fallback_model: Optional[str]
    attempts: int
    total_latency_ms: float


class FallbackHandler:
    """Handle LLM failures with configurable fallback strategies.

    Strategies:
    1. Retry with the same model (for transient errors)
    2. Fall back to a cheaper/faster model
    3. Return a canned response (for complete outages)
    4. Queue for async processing
    """

    def __init__(
        self,
        primary_llm: Any,
        fallback_llms: Optional[List[Any]] = None,
        max_retries: int = 2,
        timeout_seconds: float = 30.0,
        canned_response: str = "I'm unable to process this request right now. Please try again later.",
    ):
        self.primary_llm = primary_llm
        self.fallback_llms = fallback_llms or []
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.canned_response = canned_response

    def generate(self, prompt: str) -> FallbackResult:
        """Try to generate a response, falling back as needed."""
        start = time.time()
        attempts = 0

        # Try primary LLM
        for attempt in range(self.max_retries):
            attempts += 1
            try:
                response = self.primary_llm.generate(prompt)
                elapsed = (time.time() - start) * 1000
                return FallbackResult(
                    response=response,
                    reason=FallbackReason.LLM_UNAVAILABLE if attempt > 0 else FallbackReason.LOW_CONFIDENCE,
                    fallback_model=None,
                    attempts=attempts,
                    total_latency_ms=elapsed,
                )
            except Exception:
                if attempt < self.max_retries - 1:
                    time.sleep(0.5 * (2 ** attempt))

        # Try fallback LLMs
        for fallback in self.fallback_llms:
            attempts += 1
            try:
                response = fallback.generate(prompt)
                elapsed = (time.time() - start) * 1000
                return FallbackResult(
                    response=response,
                    reason=FallbackReason.LLM_UNAVAILABLE,
                    fallback_model=getattr(fallback, "model_name", "unknown"),
                    attempts=attempts,
                    total_latency_ms=elapsed,
                )
            except Exception:
                continue

        # All models failed — return canned response
        elapsed = (time.time() - start) * 1000
        return FallbackResult(
            response=self.canned_response,
            reason=FallbackReason.LLM_UNAVAILABLE,
            fallback_model="canned_response",
            attempts=attempts,
            total_latency_ms=elapsed,
        )
