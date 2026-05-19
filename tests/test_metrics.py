from rag.financial_metrics import FinancialMetricsExtractor


def test_revenue_extraction():
    text = "Total revenues: $50.2 billion for fiscal 2024."
    metrics = FinancialMetricsExtractor.extract_all_metrics(text)
    names = [m.name for m in metrics]
    assert "revenue" in names


def test_calculate_ratios():
    ratios = FinancialMetricsExtractor.calculate_ratios(
        net_income=1e9,
        revenue=50e9,
        total_assets=100e9,
        stockholders_equity=50e9,
    )
    assert "net_profit_margin" in ratios
    assert ratios["net_profit_margin"] == 2.0
