from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List


def format_chunk_citation(chunk: Dict, index: int) -> str:
    """Human-readable citation line for one retrieved chunk."""
    meta = chunk.get("metadata") or {}
    section = meta.get("section", "Unknown section")
    ticker = meta.get("ticker", chunk.get("doc_id", ""))
    filing_date = meta.get("filing_date", "")
    score = chunk.get("score", 0.0)
    preview = (chunk.get("text") or "")[:200].replace("\n", " ")
    return (
        f"[{index}] {ticker} | {section} | {filing_date} | "
        f"score={score:.3f} | {preview}..."
    )


def export_citations_markdown(
    question: str,
    answer: str,
    chunks: List[Dict],
    filing_info: Dict[str, Any] | None = None,
) -> str:
    """Export Q&A and sources as Markdown."""
    lines = [
        "# SEC Filing Analysis Export",
        "",
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_",
        "",
    ]
    if filing_info:
        lines.extend([
            "## Filing",
            f"- **Company:** {filing_info.get('company_name', 'N/A')}",
            f"- **Ticker:** {filing_info.get('ticker', 'N/A')}",
            f"- **Form:** {filing_info.get('form_type', 'N/A')}",
            f"- **Date:** {filing_info.get('filing_date', 'N/A')}",
            f"- **Source:** {filing_info.get('filing_html_url', 'N/A')}",
            "",
        ])
    lines.extend(["## Question", question, "", "## Answer", answer, "", "## Sources"])
    for i, chunk in enumerate(chunks, 1):
        lines.append(f"### Source {i}")
        lines.append(format_chunk_citation(chunk, i))
        lines.append("")
        lines.append("```")
        lines.append((chunk.get("text") or "")[:1500])
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def export_citations_json(
    question: str,
    answer: str,
    chunks: List[Dict],
    filing_info: Dict[str, Any] | None = None,
) -> str:
    """Export Q&A and sources as JSON."""
    payload = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "filing": filing_info or {},
        "question": question,
        "answer": answer,
        "sources": [
            {
                "index": i,
                "chunk_id": c.get("chunk_id"),
                "score": c.get("score"),
                "metadata": c.get("metadata", {}),
                "text": c.get("text"),
            }
            for i, c in enumerate(chunks, 1)
        ],
    }
    return json.dumps(payload, indent=2)
