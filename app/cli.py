from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv

from sec.sec_client import SECClient
from sec.filing_service import FilingService
from rag.retriever import SimpleRetriever
from rag.llm_client import LLMClient
from rag.pipeline import RAGPipeline


TASK_QUERY_MAP = {
    "business_summary": "business overview products services strategy competition",
    "risk_summary": "risk factors cybersecurity supply chain regulation competition macroeconomic",
    "mdna_summary": "management discussion results of operations liquidity capital resources outlook",
    "financial_red_flags": "material weakness going concern liquidity debt impairment loss legal proceedings risk",
}


def parse_args():
    parser = argparse.ArgumentParser(description="SEC Filing Analyzer")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--form", default="10-K", choices=["10-K", "10-Q"], help="Filing form type")
    parser.add_argument(
        "--mode",
        default="task",
        choices=["task", "ask"],
        help="Run predefined task or free-form question",
    )
    parser.add_argument(
        "--task",
        default="risk_summary",
        choices=list(TASK_QUERY_MAP.keys()),
        help="Predefined analysis task",
    )
    parser.add_argument("--question", default=None, help="Question for ask mode")
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    sec_user_agent = os.getenv("SEC_USER_AGENT")
    if not sec_user_agent:
        raise ValueError("Please set SEC_USER_AGENT in .env")

    sec_client = SECClient(user_agent=sec_user_agent)
    filing_service = FilingService(sec_client=sec_client)

    filing_bundle = filing_service.build_chunks_for_latest_filing(
        ticker=args.ticker,
        form_type=args.form,
    )

    retriever = SimpleRetriever()
    retriever.index(filing_bundle["chunks"])

    llm_client = LLMClient()
    pipeline = RAGPipeline(retriever=retriever, llm_client=llm_client)

    if args.mode == "ask":
        if not args.question:
            raise ValueError("--question is required when --mode ask")
        result = pipeline.answer_question(args.question, top_k=6)
    else:
        retrieval_query = TASK_QUERY_MAP[args.task]
        result = pipeline.run_task(
            task=args.task,
            company=filing_bundle["company_name"],
            form_type=filing_bundle["form_type"],
            retrieval_query=retrieval_query,
            top_k=8,
        )

    print("\n" + "=" * 80)
    print(f"Company: {filing_bundle['company_name']} ({filing_bundle['ticker']})")
    print(f"Form: {filing_bundle['form_type']}")
    print(f"Filing Date: {filing_bundle['filing_date']}")
    print(f"Source: {filing_bundle['filing_html_url']}")
    print("=" * 80)
    print(result)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()