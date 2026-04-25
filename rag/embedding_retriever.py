from __future__ import annotations
from typing import List, Dict, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from rag.chunker import simple_chunk


class EmbeddingRetriever:
    """
    Semantic retriever using embedding models (SBERT).
    
    This provides better semantic understanding than TF-IDF and captures
    meaning beyond lexical overlap. Great for financial analysis where
    synonyms and conceptual similarity matter.
    
    Models available:
    - 'all-MiniLM-L6-v2': Fast, balanced (default)
    - 'all-mpnet-base-v2': Slower, better quality
    - 'paraphrase-multilingual-MiniLM-L12-v2': Multilingual
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", max_words: int = 40, overlap: int = 10):
        """
        Initialize embedding retriever.
        
        Args:
            model_name: Sentence transformer model name
            max_words: Max words per chunk
            overlap: Overlap between chunks
        """
        self.model_name = model_name
        self.max_words = max_words
        self.overlap = overlap
        self.corpus_chunks = []
        self.embeddings = None
        
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"✓ Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")

    def index(self, docs: Union[Dict[str, str], List[Dict]]) -> None:
        """Index documents or chunks."""
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

        # Encode all chunks
        print(f"Encoding {len(self.corpus_chunks)} chunks...")
        texts = [c["text"] for c in self.corpus_chunks]
        self.embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        print(f"✓ Indexed {len(self.corpus_chunks)} chunks")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most semantically similar chunks.
        
        Args:
            query: Query string
            top_k: Number of top results
            
        Returns:
            List of retrieved chunks with similarity scores
        """
        if not self.corpus_chunks or self.embeddings is None:
            return []

        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]
        
        # Compute similarities
        sims = cosine_similarity([query_embedding], self.embeddings)[0]
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
        """Check if dict is in new chunk format."""
        return "text" in obj and isinstance(obj.get("text"), str)
