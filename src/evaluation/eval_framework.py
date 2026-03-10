"""Evaluation framework for GenAI outputs.

Automated quality testing for LLM-based applications.
Runs evaluation suites on each deployment to catch quality regressions.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional


@dataclass
class EvalCase:
    input: str
    expected_output: Optional[str] = None
    criteria: Optional[Dict[str, str]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class EvalScore:
    case_id: int
    scores: Dict[str, float]
    latency_ms: float
    passed: bool
    actual_output: str


class EvalFramework:
    """Run evaluation suites for GenAI applications."""

    def __init__(self, generate_fn: Callable[[str], str], threshold: float = 0.7):
        self.generate_fn = generate_fn
        self.threshold = threshold

    def run_suite(self, cases: List[EvalCase]) -> List[EvalScore]:
        results = []
        for i, case in enumerate(cases):
            start = time.time()
            output = self.generate_fn(case.input)
            elapsed = (time.time() - start) * 1000

            scores = {}
            if case.expected_output:
                scores["similarity"] = self._text_similarity(output, case.expected_output)

            passed = all(s >= self.threshold for s in scores.values()) if scores else True

            results.append(EvalScore(
                case_id=i,
                scores=scores,
                latency_ms=elapsed,
                passed=passed,
                actual_output=output,
            ))
        return results

    @staticmethod
    def _text_similarity(a: str, b: str) -> float:
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        return len(words_a & words_b) / max(len(words_a), len(words_b))

    @staticmethod
    def save_results(results: List[EvalScore], path: str) -> None:
        with open(path, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
