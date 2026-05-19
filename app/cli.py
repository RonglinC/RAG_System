from __future__ import annotations

import argparse
import os

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

from app.analyzer import SECFilingAnalyzer, TASK_QUERY_MAP


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
    parser.add_argument(
        "--retriever",
        default="tfidf",
        choices=["tfidf", "embedding", "hybrid"],
        help="Retrieval strategy",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable filing disk cache",
    )
    parser.add_argument(
        "--export",
        choices=["markdown", "json"],
        default=None,
        help="Write citations export to stdout file path suffix (use with ask mode)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    analyzer = SECFilingAnalyzer(
        retriever_type=args.retriever,
        use_cache=not args.no_cache,
    )
    filing_bundle = analyzer.load_filing(args.ticker, args.form)

    if args.mode == "ask":
        if not args.question:
            raise ValueError("--question is required when --mode ask")
        result = analyzer.ask(args.question, top_k=6)
        output = result["response"]
        if args.export:
            export = analyzer.export_last_answer(result, fmt=args.export)
            ext = "md" if args.export == "markdown" else "json"
            out_path = f"{args.ticker}_{args.form}_answer.{ext}"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(export)
            print(f"\nExported citations to {out_path}")
    else:
        output = analyzer.run_task(args.task, top_k=8)

    print("\n" + "=" * 80)
    print(f"Company: {filing_bundle['company_name']} ({filing_bundle['ticker']})")
    print(f"Form: {filing_bundle['form_type']}")
    print(f"Filing Date: {filing_bundle['filing_date']}")
    print(f"Source: {filing_bundle['filing_html_url']}")
    print(f"Retriever: {args.retriever} | Cache: {not args.no_cache}")
    print("=" * 80)
    print(output)
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
