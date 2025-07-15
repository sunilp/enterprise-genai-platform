"""Vector store index lifecycle management."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class IndexMetadata:
    name: str
    created_at: float = field(default_factory=time.time)
    document_count: int = 0
    chunk_count: int = 0
    embedding_model: str = ""
    content_hash: str = ""


class IndexManager:
    """Manage vector store index lifecycle."""

    def __init__(self, vector_store: Any, chunker: Any, embedder: Any):
        self.vector_store = vector_store
        self.chunker = chunker
        self.embedder = embedder
        self._indexes: Dict[str, IndexMetadata] = {}

    def create_index(self, name: str, documents: List[str]) -> IndexMetadata:
        all_chunks = []
        for doc in documents:
            chunks = self.chunker(doc)
            all_chunks.extend(chunks)

        content_hash = hashlib.sha256(
            json.dumps(documents, sort_keys=True).encode()
        ).hexdigest()[:16]

        metadata = IndexMetadata(
            name=name,
            document_count=len(documents),
            chunk_count=len(all_chunks),
            embedding_model=getattr(self.embedder, "model_name", "unknown"),
            content_hash=content_hash,
        )
        self._indexes[name] = metadata
        return metadata

    def needs_rebuild(self, name: str, documents: List[str]) -> bool:
        if name not in self._indexes:
            return True
        current_hash = hashlib.sha256(
            json.dumps(documents, sort_keys=True).encode()
        ).hexdigest()[:16]
        return current_hash != self._indexes[name].content_hash
