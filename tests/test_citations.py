from rag.citations import export_citations_markdown, format_chunk_citation


def test_format_chunk_citation():
    chunk = {
        "text": "Sample risk disclosure text.",
        "score": 0.87,
        "metadata": {"section": "Item 1A", "ticker": "AAPL", "filing_date": "2024-10-01"},
    }
    line = format_chunk_citation(chunk, 1)
    assert "AAPL" in line
    assert "Item 1A" in line


def test_export_markdown():
    md = export_citations_markdown(
        "What are the risks?",
        "Cyber risk is material.",
        [{"text": "risk text", "score": 0.9, "metadata": {"ticker": "AAPL"}}],
        {"ticker": "AAPL", "form_type": "10-K"},
    )
    assert "## Question" in md
    assert "## Answer" in md
