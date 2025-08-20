"""Token and cost tracking for GenAI operations."""

from dataclasses import dataclass, field
from typing import Dict, List

MODEL_COSTS = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
}


@dataclass
class Usage:
    operation: str
    model: str
    input_tokens: int
    output_tokens: int

    @property
    def cost(self) -> float:
        pricing = MODEL_COSTS.get(self.model, {"input": 0.001, "output": 0.002})
        return self.input_tokens / 1000 * pricing["input"] + self.output_tokens / 1000 * pricing["output"]


class CostTracker:
    def __init__(self):
        self._usages: List[Usage] = []

    def record(self, operation: str, model: str, input_tokens: int, output_tokens: int = 0):
        self._usages.append(Usage(operation=operation, model=model, input_tokens=input_tokens, output_tokens=output_tokens))

    @property
    def total_cost(self) -> float:
        return sum(u.cost for u in self._usages)

    @property
    def cost_by_operation(self) -> Dict[str, float]:
        costs: Dict[str, float] = {}
        for u in self._usages:
            costs[u.operation] = costs.get(u.operation, 0) + u.cost
        return costs
