"""Output quality drift detection.

Monitors LLM output quality over time to detect degradation.
Useful when switching models, updating prompts, or when the
underlying model is updated by the provider.
"""

from __future__ import annotations

import statistics
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional


@dataclass
class DriftAlert:
    metric: str
    current_mean: float
    baseline_mean: float
    deviation: float
    is_drifting: bool


class DriftMonitor:
    """Monitor output quality metrics for drift."""

    def __init__(self, window_size: int = 100, threshold_std: float = 2.0):
        self.window_size = window_size
        self.threshold_std = threshold_std
        self._windows: Dict[str, Deque[float]] = {}
        self._baselines: Dict[str, tuple] = {}

    def set_baseline(self, metric: str, values: List[float]) -> None:
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0.0
        self._baselines[metric] = (mean, std)

    def record(self, metric: str, value: float) -> Optional[DriftAlert]:
        if metric not in self._windows:
            self._windows[metric] = deque(maxlen=self.window_size)
        self._windows[metric].append(value)

        if metric not in self._baselines or len(self._windows[metric]) < 10:
            return None

        baseline_mean, baseline_std = self._baselines[metric]
        current_mean = statistics.mean(self._windows[metric])

        if baseline_std == 0:
            deviation = abs(current_mean - baseline_mean)
        else:
            deviation = abs(current_mean - baseline_mean) / baseline_std

        is_drifting = deviation > self.threshold_std

        return DriftAlert(
            metric=metric,
            current_mean=current_mean,
            baseline_mean=baseline_mean,
            deviation=deviation,
            is_drifting=is_drifting,
        )
