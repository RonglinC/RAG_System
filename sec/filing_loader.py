from __future__ import annotations

from sec.sec_client import SECClient
from sec.filing_parser import clean_html


class FilingLoader:

    TICKER_TO_CIK = {
        "AAPL": "0000320193",
        "MSFT": "0000789019",
        "TSLA": "0001318605"
    }

    def __init__(self, user_agent: str):
        self.sec = SECClient(user_agent)

    def load_latest_filing(self, ticker: str, form: str = "10-K"):

        cik = self.TICKER_TO_CIK[ticker]

        filing_info = self.sec.get_latest_filing(cik, form)

        html = self.sec.download_filing(filing_info["url"])

        text = clean_html(html)

        doc_id = f"{ticker}_{form}_{filing_info['filing_date']}"

        docs = {
            doc_id: text
        }

        return docs