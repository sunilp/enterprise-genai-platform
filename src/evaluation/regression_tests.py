"""Regression tests for LLM quality.

Catches quality degradation when switching models, updating prompts,
or modifying the RAG pipeline. Runs a fixed set of test cases and
compares against baseline scores.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Dict, List


@dataclass
class RegressionResult:
    test_name: str
    baseline_score: float
    current_score: float
    passed: bool
    regression_delta: float


class RegressionRunner:
    """Run regression tests against a baseline."""

    def __init__(
        self,
        generate_fn: Callable[[str], str],
        score_fn: Callable[[str, str, str], float],
        tolerance: float = 0.05,
    ):
        self.generate_fn = generate_fn
        self.score_fn = score_fn
        self.tolerance = tolerance

    def run(
        self, test_cases: List[Dict], baseline_scores: Dict[str, float]
    ) -> List[RegressionResult]:
        results = []
        for case in test_cases:
            name = case["name"]
            output = self.generate_fn(case["input"])
            score = self.score_fn(case["input"], output, case.get("expected", ""))

            baseline = baseline_scores.get(name, 0.0)
            delta = baseline - score
            passed = delta <= self.tolerance

            results.append(RegressionResult(
                test_name=name,
                baseline_score=baseline,
                current_score=score,
                passed=passed,
                regression_delta=delta,
            ))
        return results

    @staticmethod
    def save_baseline(scores: Dict[str, float], path: str) -> None:
        with open(path, "w") as f:
            json.dump(scores, f, indent=2)

    @staticmethod
    def load_baseline(path: str) -> Dict[str, float]:
        with open(path) as f:
            return json.load(f)
