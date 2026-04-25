from __future__ import annotations
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class FinancialMetric:
    """Represents an extracted financial metric."""
    name: str
    value: float
    unit: str  # "millions", "billions", "percentage", "ratio", "count"
    year: Optional[int] = None
    source_section: Optional[str] = None
    note: Optional[str] = None


class FinancialMetricsExtractor:
    """
    Extract key financial metrics from SEC filings.
    
    Supports:
    - Revenue and profitability metrics
    - Balance sheet items (assets, liabilities, equity)
    - Cash flow metrics
    - Ratios and growth rates
    - Headcount and operational metrics
    """
    
    # Patterns for key financial metrics (case-insensitive)
    PATTERNS = {
        # Revenue and Income
        "revenue": r"(?:total\s+)?revenues?(?:\s+from)?(?:\s+operations)?[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "gross_profit": r"gross\s+profit(?:\(loss\))?[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "operating_income": r"operating\s+(?:income|earnings|loss)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "net_income": r"(?:net\s+)?(?:income|loss)(?:\s+from\s+operations)?[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "eps": r"(?:diluted\s+)?earnings?\s+per\s+share[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        
        # Cash Flow
        "operating_cash_flow": r"cash\s+(?:flows?\s+)?from\s+(?:operating|operations)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "free_cash_flow": r"free\s+cash\s+flow[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "capex": r"(?:capital\s+)?(?:expenditures?|spending)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        
        # Balance Sheet
        "total_assets": r"total\s+assets[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "current_assets": r"current\s+assets[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "total_liabilities": r"total\s+liabilities?[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "current_liabilities": r"current\s+liabilities[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "stockholders_equity": r"(?:stockholders?|shareholders?)[\s-]?equit(?:y|ies)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "total_debt": r"total\s+debt[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "cash_and_equivalents": r"cash(?:\s+and\s+)?(?:equivalents|investments)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        
        # Working Capital
        "account_receivable": r"(?:accounts?\s+)?(?:receivable|AR)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "inventory": r"inventor(?:y|ies)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        "accounts_payable": r"(?:accounts?\s+)?(?:payable|AP)[:\s=-]*\$?[\d,]+(?:\.\d+)?",
        
        # Operational
        "headcount": r"(?:total\s+)?(?:employees?|headcount)[:\s=-]*[\d,]+(?:\s+(?:as of)?)?",
        "stores": r"(?:company-operated\s+)?stores?(?:\s+worldwide)?[:\s=-]*[\d,]+",
    }
    
    # Multiplier keywords
    MULTIPLIERS = {
        "thousand": 1e3,
        "thousand dollars": 1e3,
        "thousands": 1e3,
        "million": 1e6,
        "millions": 1e6,
        "million dollars": 1e6,
        "billion": 1e9,
        "billions": 1e9,
        "billion dollars": 1e9,
    }

    @classmethod
    def extract_all_metrics(cls, text: str, section: str = "General") -> List[FinancialMetric]:
        """
        Extract all financial metrics from text.
        
        Args:
            text: Text to extract from
            section: Section source (e.g., "Item 8 Financial Statements")
            
        Returns:
            List of extracted metrics
        """
        metrics = []
        
        for metric_name, pattern in cls.PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = cls._parse_financial_value(match.group())
                if value is not None:
                    metric = FinancialMetric(
                        name=metric_name,
                        value=value["amount"],
                        unit=value["unit"],
                        source_section=section
                    )
                    metrics.append(metric)
        
        return metrics

    @classmethod
    def extract_growth_rates(cls, current_value: float, previous_value: float) -> Dict:
        """Calculate growth metrics."""
        if previous_value == 0:
            return {"growth_rate": None, "growth_pct": None}
        
        growth = current_value - previous_value
        growth_pct = (growth / abs(previous_value)) * 100
        
        return {
            "growth_rate": growth,
            "growth_pct": growth_pct,
            "yoy_change": f"{growth_pct:+.1f}%"
        }

    @classmethod
    def calculate_ratios(cls, net_income: float, revenue: float, total_assets: float, 
                        stockholders_equity: float) -> Dict[str, float]:
        """Calculate common financial ratios."""
        ratios = {}
        
        if revenue > 0:
            ratios["net_profit_margin"] = (net_income / revenue) * 100
            ratios["roe"] = (net_income / stockholders_equity) * 100 if stockholders_equity > 0 else None
            ratios["roa"] = (net_income / total_assets) * 100 if total_assets > 0 else None
        
        return {k: v for k, v in ratios.items() if v is not None}

    @staticmethod
    def _parse_financial_value(text: str) -> Optional[Dict]:
        """Parse a financial value from text."""
        # Remove common prefixes
        clean_text = re.sub(r"^[^$\d]*", "", text)
        
        # Extract number
        number_match = re.search(r"\$?([\d,]+(?:\.\d+)?)", clean_text)
        if not number_match:
            return None
        
        amount_str = number_match.group(1).replace(",", "")
        try:
            amount = float(amount_str)
        except ValueError:
            return None
        
        # Detect multiplier
        unit = "units"
        remaining_text = clean_text[number_match.end():].lower()
        
        for key, multiplier in FinancialMetricsExtractor.MULTIPLIERS.items():
            if key in remaining_text:
                amount *= multiplier
                unit = "millions" if multiplier == 1e6 else ("billions" if multiplier == 1e9 else "thousands")
                break
        
        # Detect if percentage
        if "%" in remaining_text or "percent" in remaining_text:
            unit = "percentage"
        
        return {"amount": amount, "unit": unit}


class LoanMetricsAnalyzer:
    """Analyze debt and loan-related metrics."""
    
    @staticmethod
    def extract_debt_structure(text: str) -> Dict:
        """Extract debt composition and terms."""
        debt_items = {
            "short_term_debt": re.search(r"short\s+term\s+(?:debt|borrowings)[:\s=-]*\$?[\d,]+(?:\.\d+)?", text),
            "long_term_debt": re.search(r"long\s+term\s+debt[:\s=-]*\$?[\d,]+(?:\.\d+)?", text),
            "convertible_debt": re.search(r"convertible.*?debt[:\s=-]*\$?[\d,]+(?:\.\d+)?", text),
        }
        return {k: v.group() if v else None for k, v in debt_items.items()}


class CashFlowAnalyzer:
    """Analyze cash flow patterns and trends."""
    
    @staticmethod
    def assess_cash_position(operating_cf: float, capex: float, debt_payments: float) -> Dict:
        """Assess overall cash flow health."""
        free_cf = operating_cf - capex
        debt_coverage = free_cf / debt_payments if debt_payments > 0 else float('inf')
        
        return {
            "free_cash_flow": free_cf,
            "debt_coverage_ratio": debt_coverage,
            "sustainability": (
                "Strong" if debt_coverage > 2 
                else "Adequate" if debt_coverage > 1 
                else "Concerning"
            ),
            "capex_intensity": (capex / operating_cf * 100) if operating_cf > 0 else None
        }
