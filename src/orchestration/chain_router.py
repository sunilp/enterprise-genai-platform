"""Chain Router — routes requests to appropriate LLM chains.

Classifies incoming requests by intent and routes them to specialized
chains (Q&A, summarization, extraction, etc.). Each chain has its own
prompt template, model configuration, and guardrail settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import re


class Intent(Enum):
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    GENERAL = "general"


@dataclass
class ChainConfig:
    """Configuration for an LLM chain."""
    intent: Intent
    model: str
    prompt_template: str
    temperature: float = 0.0
    max_tokens: int = 1024
    requires_rag: bool = False
    guardrail_level: str = "standard"


@dataclass
class RouteResult:
    """Result of routing a request."""
    intent: Intent
    chain_config: ChainConfig
    confidence: float
    metadata: dict = field(default_factory=dict)


class ChainRouter:
    """Route requests to the appropriate LLM chain.

    Uses keyword-based intent classification by default.
    Can be extended with an LLM-based classifier for higher accuracy.
    """

    # Simple keyword patterns for intent classification
    _INTENT_PATTERNS = {
        Intent.QUESTION_ANSWERING: [
            r"\bwhat\b", r"\bhow\b", r"\bwhy\b", r"\bwhen\b", r"\bwhere\b",
            r"\bexplain\b", r"\bdescribe\b", r"\?$",
        ],
        Intent.SUMMARIZATION: [
            r"\bsummar", r"\bbrief\b", r"\boverview\b", r"\btl;?dr\b",
            r"\bkey\s+points\b", r"\bhighlight",
        ],
        Intent.EXTRACTION: [
            r"\bextract\b", r"\bfind\s+(?:all|the)\b", r"\blist\s+(?:all|the)\b",
            r"\bidentify\b", r"\bpull\s+out\b",
        ],
        Intent.CLASSIFICATION: [
            r"\bclassif", r"\bcategoriz", r"\blabel\b", r"\bwhich\s+type\b",
            r"\bis\s+(?:this|it)\s+a\b",
        ],
    }

    def __init__(self, chains: Dict[Intent, ChainConfig], default_intent: Intent = Intent.GENERAL):
        self.chains = chains
        self.default_intent = default_intent
        self._compiled_patterns = {
            intent: [re.compile(p, re.IGNORECASE) for p in patterns]
            for intent, patterns in self._INTENT_PATTERNS.items()
        }

    def route(self, query: str) -> RouteResult:
        """Classify intent and return the matching chain configuration."""
        scores: Dict[Intent, int] = {}

        for intent, patterns in self._compiled_patterns.items():
            score = sum(1 for p in patterns if p.search(query))
            if score > 0:
                scores[intent] = score

        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(1.0, scores[best_intent] / 3)
        else:
            best_intent = self.default_intent
            confidence = 0.3

        chain_config = self.chains.get(best_intent, self.chains.get(self.default_intent))
        if chain_config is None:
            raise ValueError(f"No chain configured for intent {best_intent}")

        return RouteResult(
            intent=best_intent,
            chain_config=chain_config,
            confidence=confidence,
        )
