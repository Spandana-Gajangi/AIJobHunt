from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeChunk:
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGQuery:
    question: str
    top_k: int = 3
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResult:
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
