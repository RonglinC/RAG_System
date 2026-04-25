from __future__ import annotations

from typing import List, Dict
from sec.sec_client import SECClient
from sec.filing_parser import FilingParser
from rag.chunker import SlidingWindowChunker


class FilingService:
    def __init__(self, sec_client: SECClient, max_words: int = 220, overlap: int = 40) -> None:
        self.sec_client = sec_client
        self.chunker = SlidingWindowChunker(max_words=max_words, overlap=overlap)

    def build_chunks_for_latest_filing(self, ticker: str, form_type: str = "10-K") -> Dict:
        company_info = self.sec_client.ticker_to_cik(ticker)
        submissions = self.sec_client.get_submissions(company_info["cik"])
        filing = self.sec_client.find_latest_filing(submissions, form_type=form_type)

        if not filing:
            raise ValueError(f"No recent {form_type} filing found for {ticker}")

        # Use company name from ticker lookup if available
        if company_info.get("company_name"):
            filing["company_name"] = company_info["company_name"]

        html = self.sec_client.download_filing_html(filing["filing_html_url"])
        text = FilingParser.html_to_text(html)
        sections = FilingParser.split_sections(text)

        all_chunks: List[Dict] = []
        for section in sections:
            metadata = {
                "ticker": ticker.upper(),
                "company_name": filing["company_name"],
                "cik": company_info["cik"],
                "cik": filing["cik"],
                "form_type": filing["form_type"],
                "filing_date": filing["filing_date"],
                "accession_no": filing["accession_no"],
                "section": section["section"],
                "filing_html_url": filing["filing_html_url"],
            }

            chunks = self.chunker.chunk_text(section["text"], metadata=metadata)
            for c in chunks:
                all_chunks.append(
                    {
                        "text": c.text,
                        "metadata": c.metadata,
                    }
                )

        return {
            "company_name": filing["company_name"],
            "ticker": ticker.upper(),
            "form_type": filing["form_type"],
            "filing_date": filing["filing_date"],
            "filing_html_url": filing["filing_html_url"],
            "chunks": all_chunks,
        }