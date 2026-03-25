from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from chunker import simple_chunk


class SimpleRetriever:
    def __init__(self, max_words: int = 40, overlap: int = 10):
        self.max_words = max_words
        self.overlap = overlap
        self.corpus_chunks = []
        self.vectorizer = TfidfVectorizer()
        self.embeddings = None

    def index(self, docs: Dict[str, str]) -> None:
        self.corpus_chunks = []

        for doc_id, text in docs.items():
            chunks = simple_chunk(text, max_words=self.max_words, overlap=self.overlap)
            for i, chunk in enumerate(chunks):
                self.corpus_chunks.append({
                    "chunk_id": f"{doc_id}_chunk{i}",
                    "doc_id": doc_id,
                    "text": chunk,
                })

        texts = [c["text"] for c in self.corpus_chunks]
        self.embeddings = self.vectorizer.fit_transform(texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
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
            })
        return results