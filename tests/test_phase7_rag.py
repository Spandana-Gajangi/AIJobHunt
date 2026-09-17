from app.models.knowledge import KnowledgeChunk, RAGQuery
from app.services.rag_service import KnowledgeBase


def test_chunk_text_splits_documents_with_overlap() -> None:
    knowledge_base = KnowledgeBase()
    text = "Python Kubernetes AWS RAG resume story for strong backend engineering work and cloud operations."

    chunks = knowledge_base.chunk_text(text, chunk_size=24, overlap=6)

    assert len(chunks) >= 2
    assert all(isinstance(chunk, KnowledgeChunk) for chunk in chunks)
    assert all(chunk.text for chunk in chunks)


def test_search_returns_relevant_context_for_query() -> None:
    knowledge_base = KnowledgeBase()
    knowledge_base.add_document("Python developer with strong Kubernetes and AWS experience.")
    knowledge_base.add_document("Senior product manager with strategy and stakeholder communication skills.")

    results = knowledge_base.search(RAGQuery(question="Tell me about Python and Kubernetes experience", top_k=3))

    assert len(results) >= 1
    assert any("Python" in result.text for result in results)
    assert any("Kubernetes" in result.text for result in results)
