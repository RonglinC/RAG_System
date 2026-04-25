from __future__ import annotations
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""
    text: str
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def simple_chunk(text: str, max_words: int = 40, overlap: int = 10) -> List[str]:
    """Simple chunking with sliding window."""
    if overlap >= max_words:
        raise ValueError("overlap must be smaller than max_words")

    words = text.split()
    chunks = []
    step = max_words - overlap
    i = 0

    while i < len(words):
        chunk_words = words[i:i + max_words]
        chunks.append(" ".join(chunk_words))
        i += step

    return chunks


class SlidingWindowChunker:
    """Advanced chunking with sliding window and metadata support."""
    
    def __init__(self, max_words: int = 220, overlap: int = 40):
        """
        Initialize chunker with window size and overlap.
        
        Args:
            max_words: Maximum words per chunk
            overlap: Number of overlapping words between chunks
        """
        self.max_words = max_words
        self.overlap = overlap
        
        if overlap >= max_words:
            raise ValueError("overlap must be smaller than max_words")

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Chunk]:
        """
        Chunk text into overlapping chunks with metadata.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of Chunk objects
        """
        words = text.split()
        chunks = []
        step = self.max_words - self.overlap
        i = 0

        while i < len(words):
            chunk_words = words[i:i + self.max_words]
            chunk_text = " ".join(chunk_words)
            
            chunk = Chunk(
                text=chunk_text,
                metadata=metadata.copy() if metadata else {}
            )
            chunks.append(chunk)
            i += step

        return chunks