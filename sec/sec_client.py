from __future__ import annotations

import requests
from typing import Dict, List, Optional


class SECClient:

    BASE_URL = "https://data.sec.gov"
    FAMILIAR_TICKERS = {
        "AAPL": "0000320193",
        "MSFT": "0000789019",
        "TSLA": "0001318605",
        "GOOGL": "0001652044",
        "META": "0001326801",
        "NVDA": "0001045810",
        "AMZN": "0001018724",
    }

    def __init__(self, user_agent: str):
        self.headers = {
            "User-Agent": user_agent
        }

    def ticker_to_cik(self, ticker: str) -> Dict[str, str]:
        """Convert ticker to CIK using SEC company tickers endpoint."""
        ticker = ticker.upper()
        
        if ticker in self.FAMILIAR_TICKERS:
            cik = self.FAMILIAR_TICKERS[ticker]
            return {"ticker": ticker, "cik": cik, "company_name": ""}
        
        try:
            url = f"{self.BASE_URL}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            for entry in data.values():
                if entry.get("ticker", "").upper() == ticker:
                    cik = str(entry["cik_str"]).zfill(10)
                    company_name = entry.get("title", "")
                    return {
                        "ticker": ticker,
                        "cik": cik,
                        "company_name": company_name
                    }
            
            raise ValueError(f"Ticker {ticker} not found in SEC database")
        except Exception as e:
            raise ValueError(f"Error looking up ticker {ticker}: {e}")

    def get_submissions(self, cik: str) -> Dict:
        """Get company submissions (alias for get_company_submissions)."""
        return self.get_company_submissions(cik)

    def get_company_submissions(self, cik: str) -> Dict:
        cik = str(cik).zfill(10)
        url = f"{self.BASE_URL}/submissions/CIK{cik}.json"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def find_latest_filing(self, submissions: Dict, form_type: str = "10-K") -> Optional[Dict]:
        """Find latest filing of specified form type from submissions."""
        recent = submissions["filings"]["recent"]
        
        forms = recent.get("form", [])
        accession_numbers = recent.get("accessionNumber", [])
        filing_dates = recent.get("filingDate", [])
        
        for i, form in enumerate(forms):
            if form == form_type:
                accession = accession_numbers[i]
                filing_date = filing_dates[i]
                cik = str(submissions.get("cik_str", "0")).zfill(10)
                cik_num = str(int(cik))  # Remove leading zeros for URL
                
                primary_doc = recent.get("primaryDocument", [""])[i]
                
                # Build proper filing URL
                filing_html_url = (
                    f"https://www.sec.gov/cgi-bin/viewer?"
                    f"action=view&cik={cik_num}&accession_number={accession}&xbrl_type=v"
                )
                
                return {
                    "company_name": "Unknown",  # Will be overridden by filing_service
                    "cik": cik,
                    "cik_num": cik_num,
                    "ticker": "UNKNOWN",  # Will be overridden by filing_service
                    "form_type": form_type,
                    "filing_date": filing_date,
                    "accession_no": accession,
                    "filing_html_url": filing_html_url,
                }
        
        return None

    def get_latest_filing(self, cik: str, form_type: str = "10-K") -> Dict:
        submissions = self.get_company_submissions(cik)
        recent = submissions["filings"]["recent"]
        forms = recent["form"]
        accession_numbers = recent["accessionNumber"]
        primary_docs = recent["primaryDocument"]
        filing_dates = recent["filingDate"]

        for i, form in enumerate(forms):
            if form == form_type:
                accession = accession_numbers[i]
                doc = primary_docs[i]
                cik_no_zero = str(int(cik))
                url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zero}/{accession.replace('-', '')}/{doc}"

                return {
                    "filing_date": filing_dates[i],
                    "accession": accession,
                    "url": url
                }

        raise ValueError(f"No {form_type} filing found")

    def download_filing(self, url: str) -> str:
        """Download filing HTML from URL."""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def download_filing_html(self, filing_url: str) -> str:
        """Download filing HTML (alias for download_filing)."""
        return self.download_filing(filing_url)