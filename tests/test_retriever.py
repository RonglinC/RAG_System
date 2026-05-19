from rag.retriever import SimpleRetriever
from rag.retriever_factory import create_retriever


SAMPLE_CHUNKS = [
    {
        "text": "Risk factors include supply chain disruption and cybersecurity incidents.",
        "metadata": {"section": "Item 1A Risk Factors", "ticker": "TEST"},
    },
    {
        "text": "Revenue increased 12% year over year driven by cloud services growth.",
        "metadata": {"section": "Item 7 MD&A", "ticker": "TEST"},
    },
    {
        "text": "Total assets were $400 billion with cash and equivalents of $50 billion.",
        "metadata": {"section": "Item 8 Financial Statements", "ticker": "TEST"},
    },
]


def test_tfidf_retrieves_risk_chunk():
    retriever = SimpleRetriever()
    retriever.index(SAMPLE_CHUNKS)
    hits = retriever.retrieve("cybersecurity supply chain risks", top_k=1)
    assert len(hits) == 1
    assert "Risk" in hits[0]["metadata"].get("section", "")


def test_hybrid_retriever_factory():
    pytest = __import__("pytest")
    pytest.importorskip("sentence_transformers")
    retriever = create_retriever("hybrid")
    retriever.index(SAMPLE_CHUNKS)
    hits = retriever.retrieve("revenue growth cloud", top_k=2)
    assert len(hits) >= 1
    assert any(
        "Revenue" in h["text"] or "MD&A" in h.get("metadata", {}).get("section", "")
        for h in hits
    )


def test_create_retriever_invalid():
    try:
        create_retriever("unknown")
        assert False, "expected ValueError"
    except ValueError:
        pass
