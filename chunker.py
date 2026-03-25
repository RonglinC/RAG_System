from typing import List


def simple_chunk(text: str, max_words: int = 40, overlap: int = 10) -> List[str]:
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