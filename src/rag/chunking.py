"""Document chunking for the RAG pipeline."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    text: str
    index: int
    metadata: dict


def recursive_chunk(text: str, max_size: int = 512, separators: List[str] = None) -> List[Chunk]:
    """Recursively chunk text using separator hierarchy."""
    separators = separators or ["\n\n", "\n", ". ", " "]

    if len(text) <= max_size:
        return [Chunk(text=text, index=0, metadata={})] if text.strip() else []

    sep = separators[0] if separators else " "
    parts = text.split(sep)
    chunks = []
    current = ""

    for part in parts:
        candidate = current + sep + part if current else part
        if len(candidate) <= max_size:
            current = candidate
        else:
            if current.strip():
                if len(current) <= max_size:
                    chunks.append(Chunk(text=current, index=len(chunks), metadata={}))
                elif len(separators) > 1:
                    sub = recursive_chunk(current, max_size, separators[1:])
                    for sc in sub:
                        sc.index = len(chunks)
                        chunks.append(sc)
            current = part

    if current.strip():
        chunks.append(Chunk(text=current, index=len(chunks), metadata={}))

    return chunks
