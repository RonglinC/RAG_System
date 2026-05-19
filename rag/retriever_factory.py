from __future__ import annotations

from typing import Any, Literal

from rag.retriever import SimpleRetriever

RetrieverType = Literal["tfidf", "embedding", "hybrid"]
AnyRetriever = Any


def create_retriever(
    retriever_type: RetrieverType = "tfidf",
    *,
    model_name: str = "all-MiniLM-L6-v2",
    tfidf_weight: float = 0.4,
    embed_weight: float = 0.6,
) -> AnyRetriever:
    """Build a retriever by name."""
    kind = retriever_type.lower().strip()
    if kind == "tfidf":
        return SimpleRetriever()
    if kind in ("embedding", "embed", "semantic"):
        from rag.embedding_retriever import EmbeddingRetriever

        return EmbeddingRetriever(model_name=model_name)
    if kind == "hybrid":
        from rag.hybrid_retriever import HybridRetriever

        return HybridRetriever(
            tfidf_weight=tfidf_weight,
            embed_weight=embed_weight,
            model_name=model_name,
        )
    raise ValueError(f"Unknown retriever type: {retriever_type}")
