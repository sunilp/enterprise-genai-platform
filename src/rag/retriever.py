"""Document retriever with configurable strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class RetrievedDocument:
    text: str
    score: float
    metadata: dict


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        ...


class VectorRetriever(BaseRetriever):
    """Retrieve documents using vector similarity search."""

    def __init__(self, vector_store: Any, embedder: Any):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedDocument]:
        results = self.vector_store.similarity_search(query, k=top_k)
        return [
            RetrievedDocument(
                text=r.get("text", r.get("page_content", "")),
                score=r.get("score", 0.0),
                metadata=r.get("metadata", {}),
            )
            for r in results
        ]
