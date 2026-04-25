from __future__ import annotations

import re
from bs4 import BeautifulSoup
from typing import Dict, List


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\n+", "\n", text)
    return text


class FilingParser:
    """Parser for SEC filing documents with section detection."""
    
    # SEC 10-K/10-Q standard item patterns
    SECTION_PATTERNS = {
        "Business": r"Item\s+1(?:\.|–)\s+Business",
        "Risk Factors": r"Item\s+1A(?:\.|–)\s+Risk\s+Factors",
        "MD&A": r"Item\s+7(?:\.|–)\s+Management['']?s?\s+Discussion\s+and\s+Analysis",
        "Financial Statements": r"Item\s+8(?:\.|–)\s+Financial\s+Statements",
        "Controls": r"Item\s+9A(?:\.|–)\s+Controls\s+and\s+Procedures",
    }

    @staticmethod
    def html_to_text(html: str) -> str:
        """Convert HTML to clean text."""
        return clean_html(html)

    @staticmethod
    def split_sections(text: str) -> List[Dict[str, str]]:
        """Split filing text into major sections."""
        sections = []
        current_section = "Introduction"
        current_text = ""

        lines = text.split("\n")
        
        for line in lines:
            matched_section = False
            
            for section_name, pattern in FilingParser.SECTION_PATTERNS.items():
                if re.search(pattern, line, re.IGNORECASE):
                    if current_text.strip():
                        sections.append({
                            "section": current_section,
                            "text": current_text.strip()
                        })
                    current_section = section_name
                    current_text = line + "\n"
                    matched_section = True
                    break
            
            if not matched_section:
                current_text += line + "\n"
        
        if current_text.strip():
            sections.append({
                "section": current_section,
                "text": current_text.strip()
            })
        
        return sections