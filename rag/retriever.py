from __future__ import annotations
from typing import List, Dict, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from rag.chunker import simple_chunk


class SimpleRetriever:
    """TF-IDF based retriever for semantic search."""
    
    def __init__(self, max_words: int = 40, overlap: int = 10):
        self.max_words = max_words
        self.overlap = overlap
        self.corpus_chunks = []
        self.vectorizer = TfidfVectorizer()
        self.embeddings = None

    def index(self, docs: Union[Dict[str, str], List[Dict]]) -> None:
        """
        Index documents or chunks.
        
        Args:
            docs: Either dict of {doc_id: text} or list of chunk dicts with metadata
        """
        self.corpus_chunks = []

        if isinstance(docs, dict) and not self.is_chunk_format(docs):
            # Legacy format: {doc_id: text}
            for doc_id, text in docs.items():
                chunks = simple_chunk(text, max_words=self.max_words, overlap=self.overlap)
                for i, chunk in enumerate(chunks):
                    self.corpus_chunks.append({
                        "chunk_id": f"{doc_id}_chunk{i}",
                        "doc_id": doc_id,
                        "text": chunk,
                        "metadata": {}
                    })
        elif isinstance(docs, list):
            # New format: list of {text, metadata} dicts
            for i, chunk_dict in enumerate(docs):
                self.corpus_chunks.append({
                    "chunk_id": f"chunk_{i}",
                    "doc_id": chunk_dict.get("metadata", {}).get("ticker", "unknown"),
                    "text": chunk_dict["text"],
                    "metadata": chunk_dict.get("metadata", {})
                })

        texts = [c["text"] for c in self.corpus_chunks]
        if texts:
            self.embeddings = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            
        Returns:
            List of retrieved chunks with scores
        """
        if not self.corpus_chunks or self.embeddings is None:
            return []

        query_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(query_vec, self.embeddings)[0]
        top_indices = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_indices:
            item = self.corpus_chunks[idx]
            results.append({
                "chunk_id": item["chunk_id"],
                "doc_id": item["doc_id"],
                "text": item["text"],
                "score": float(sims[idx]),
                "metadata": item.get("metadata", {})
            })
        return results

    @staticmethod
    def is_chunk_format(obj: Dict) -> bool:
        """Check if dict is in new chunk format (has 'text' key at top level)."""
        return "text" in obj and isinstance(obj.get("text"), str)