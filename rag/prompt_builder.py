from __future__ import annotations
from typing import List, Dict


def _chunk_label(chunk: Dict, index: int) -> str:
    meta = chunk.get("metadata") or {}
    section = meta.get("section", "")
    ticker = meta.get("ticker", chunk.get("doc_id", f"chunk_{index}"))
    if section:
        return f"{ticker} | {section}"
    return str(ticker)


def build_prompt(question: str, retrieved_chunks: List[Dict]) -> str:
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        label = _chunk_label(chunk, i)
        context_blocks.append(f"[{label}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_blocks)
    prompt = f"""You are a financial SEC filing analyst.
Use only the excerpts below from the company's filing to answer the question.

Rules:
- Answer only using the provided context.
- If the answer is not in the context, say "I don't know."
- Cite sources using the bracket labels shown (e.g. [AAPL | Item 1A Risk Factors]).

Context:
{context}

Question:
{question}

Answer:"""
    return prompt.strip()
