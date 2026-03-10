"""Request trace logging for GenAI pipelines."""

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List


@dataclass
class Span:
    name: str
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    spans: List[Span] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, default=str)


class TraceLogger:
    def __init__(self):
        self._traces: List[Trace] = []

    @contextmanager
    def trace(self, name: str):
        t = Trace()
        t.spans.append(Span(name=name, start_time=time.time()))
        try:
            yield t
        finally:
            t.spans[0].end_time = time.time()
            self._traces.append(t)

    @contextmanager
    def span(self, trace: Trace, name: str):
        s = Span(name=name, start_time=time.time())
        try:
            yield s
        finally:
            s.end_time = time.time()
            trace.spans.append(s)
