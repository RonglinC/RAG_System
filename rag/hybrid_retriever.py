from __future__ import annotations

from typing import Dict, List, Union

from rag.retriever import SimpleRetriever


class HybridRetriever:
    """
    Combines TF-IDF and semantic embeddings via weighted score fusion.
    """

    def __init__(
        self,
        tfidf_weight: float = 0.4,
        embed_weight: float = 0.6,
        model_name: str = "all-MiniLM-L6-v2",
        max_words: int = 40,
        overlap: int = 10,
        verbose: bool = False,
    ) -> None:
        if abs((tfidf_weight + embed_weight) - 1.0) > 1e-6:
            total = tfidf_weight + embed_weight
            tfidf_weight /= total
            embed_weight /= total

        self.tfidf_weight = tfidf_weight
        self.embed_weight = embed_weight
        self.verbose = verbose
        self._model_name = model_name
        self._max_words = max_words
        self._overlap = overlap
        self._tfidf = SimpleRetriever(max_words=max_words, overlap=overlap)
        self._embed = None
        self.corpus_chunks: list = []

    def _get_embed(self):
        if self._embed is None:
            from rag.embedding_retriever import EmbeddingRetriever

            self._embed = EmbeddingRetriever(
                model_name=self._model_name,
                max_words=self._max_words,
                overlap=self._overlap,
                verbose=self.verbose,
            )
        return self._embed

    def index(self, docs: Union[Dict[str, str], List[Dict]]) -> None:
        self._tfidf.index(docs)
        self._get_embed().index(docs)
        self.corpus_chunks = list(self._tfidf.corpus_chunks)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.corpus_chunks:
            return []

        pool_k = min(max(top_k * 3, top_k), len(self.corpus_chunks))
        tfidf_hits = self._tfidf.retrieve(query, top_k=pool_k)
        embed_hits = self._get_embed().retrieve(query, top_k=pool_k)

        combined: Dict[str, Dict] = {}

        def _merge(hits: List[Dict], weight: float) -> None:
            if not hits:
                return
            max_score = max(h["score"] for h in hits) or 1.0
            for hit in hits:
                cid = hit["chunk_id"]
                norm = hit["score"] / max_score
                if cid not in combined:
                    combined[cid] = {**hit, "score": weight * norm}
                else:
                    combined[cid]["score"] += weight * norm

        _merge(tfidf_hits, self.tfidf_weight)
        _merge(embed_hits, self.embed_weight)

        ranked = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:top_k]
