"""
Retrieval evaluation on local knowledge_base HTML filings (offline, no SEC API).
Run: python evaluation_sec.py
"""

from __future__ import annotations

from pathlib import Path

from html_loader import load_knowledge_base
from rag.retriever import SimpleRetriever
from rag.retriever_factory import create_retriever

# Map filename hints to evaluation questions
EVAL_BY_FILE = {
    "amzn": [
        {
            "question": "revenue operating income financial results",
            "expected_substring": "revenue",
        },
    ],
    "nvda": [
        {
            "question": "risk factors competition technology",
            "expected_substring": "risk",
        },
    ],
}


def recall_at_k(retriever, eval_items, docs, k: int = 3) -> float:
    hits = 0
    for item in eval_items:
        results = retriever.retrieve(item["question"], top_k=k)
        combined = " ".join(r["text"].lower() for r in results)
        if item["expected_substring"].lower() in combined:
            hits += 1
    return hits / len(eval_items) if eval_items else 0.0


def chunks_from_docs(docs: dict) -> list:
    chunks = []
    for name, text in docs.items():
        chunks.append(
            {
                "text": text[:4000],
                "metadata": {"section": name, "ticker": name.split("-")[0].upper()},
            }
        )
    return chunks


def main():
    kb = Path("knowledge_base")
    if not kb.exists() or not list(kb.glob("*.html")):
        print("No knowledge_base HTML files found. Skipping evaluation.")
        return

    docs = load_knowledge_base(str(kb))
    chunks = chunks_from_docs(docs)

    eval_items = []
    for path in kb.glob("*.html"):
        key = path.stem.lower()
        for prefix, items in EVAL_BY_FILE.items():
            if prefix in key:
                eval_items.extend(items)

    if not eval_items:
        eval_items = [
            {"question": "financial statements revenue", "expected_substring": "revenue"},
            {"question": "risk factors uncertainty", "expected_substring": "risk"},
        ]

    for name in ["tfidf", "hybrid"]:
        print(f"\n=== {name.upper()} retriever ===")
        retriever = create_retriever("tfidf" if name == "tfidf" else "hybrid")
        retriever.index(chunks)
        score = recall_at_k(retriever, eval_items, docs, k=3)
        print(f"Recall@{3}: {score:.0%} ({len(eval_items)} questions)")


if __name__ == "__main__":
    main()
