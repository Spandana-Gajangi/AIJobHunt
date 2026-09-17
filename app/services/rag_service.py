from __future__ import annotations

from app.models.knowledge import KnowledgeChunk, RAGQuery, RAGResult


class KnowledgeBase:
    def __init__(self) -> None:
        self.documents: list[str] = []

    def add_document(self, document: str) -> None:
        if document.strip():
            self.documents.append(document.strip())

    def chunk_text(self, text: str, chunk_size: int = 32, overlap: int = 8) -> list[KnowledgeChunk]:
        if not text.strip():
            return []
        chunks: list[KnowledgeChunk] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            fragment = text[start:end].strip()
            if fragment:
                chunks.append(KnowledgeChunk(text=fragment, metadata={"start": start, "end": end}))
            if end == len(text):
                break
            start += max(1, chunk_size - overlap)
        return chunks

    def search(self, query: RAGQuery) -> list[RAGResult]:
        q = query.question.lower()
        results: list[RAGResult] = []
        for document in self.documents:
            score = 0.0
            for keyword in ["python", "kubernetes", "aws", "rag", "resume", "experience"]:
                if keyword in document.lower() and keyword in q:
                    score += 1.0
            if score > 0 or q in document.lower():
                results.append(RAGResult(text=document, score=score, metadata={"source": "document"}))
        return sorted(results, key=lambda item: item.score, reverse=True)[: query.top_k]
