from __future__ import annotations

import os
from typing import Any, Dict, Literal, Optional

from dotenv import load_dotenv

from rag.citations import export_citations_json, export_citations_markdown
from rag.llm_client import LLMClient
from rag.pipeline import RAGPipeline
from rag.retriever_factory import RetrieverType, create_retriever
from sec.filing_cache import FilingCache
from sec.filing_service import FilingService
from sec.sec_client import SECClient

TASK_QUERY_MAP = {
    "business_summary": "business overview products services strategy competition",
    "risk_summary": "risk factors cybersecurity supply chain regulation competition macroeconomic",
    "mdna_summary": "management discussion results of operations liquidity capital resources outlook",
    "financial_red_flags": "material weakness going concern liquidity debt impairment loss legal proceedings risk",
}


class SECFilingAnalyzer:
    """High-level orchestrator for loading filings and running RAG analysis."""

    def __init__(
        self,
        sec_user_agent: str | None = None,
        retriever_type: RetrieverType = "tfidf",
        use_cache: bool = True,
        cache_dir: str = ".cache/filings",
        llm_client: LLMClient | None = None,
    ) -> None:
        load_dotenv()
        self.sec_user_agent = sec_user_agent or os.getenv("SEC_USER_AGENT")
        if not self.sec_user_agent:
            raise ValueError("SEC_USER_AGENT is required (set in .env or pass to constructor)")

        self.cache = FilingCache(cache_dir=cache_dir, enabled=use_cache)
        self.sec_client = SECClient(user_agent=self.sec_user_agent)
        self.filing_service = FilingService(
            sec_client=self.sec_client,
            cache=self.cache,
        )
        self.retriever_type = retriever_type
        self.llm_client = llm_client or LLMClient()
        self.filing_bundle: Optional[Dict[str, Any]] = None
        self.pipeline: Optional[RAGPipeline] = None

    def load_filing(self, ticker: str, form_type: str = "10-K") -> Dict[str, Any]:
        """Download (or load from cache), chunk, and index a filing."""
        self.filing_bundle = self.filing_service.build_chunks_for_latest_filing(
            ticker=ticker.upper(),
            form_type=form_type,
        )
        retriever = create_retriever(self.retriever_type)
        retriever.index(self.filing_bundle["chunks"])
        self.pipeline = RAGPipeline(retriever=retriever, llm_client=self.llm_client)
        return self.filing_bundle

    def ask(self, question: str, top_k: int = 6) -> Dict[str, Any]:
        if not self.pipeline:
            raise RuntimeError("Call load_filing() before ask()")
        return self.pipeline.answer_question(question, top_k=top_k)

    def run_task(self, task: str, top_k: int = 8) -> str:
        if not self.pipeline or not self.filing_bundle:
            raise RuntimeError("Call load_filing() before run_task()")
        if task not in TASK_QUERY_MAP:
            raise ValueError(f"Unknown task: {task}")
        return self.pipeline.run_task(
            task=task,
            company=self.filing_bundle["company_name"],
            form_type=self.filing_bundle["form_type"],
            retrieval_query=TASK_QUERY_MAP[task],
            top_k=top_k,
        )

    def export_last_answer(
        self,
        result: Dict[str, Any],
        fmt: Literal["markdown", "json"] = "markdown",
    ) -> str:
        question = result.get("question", "")
        answer = result.get("response", "")
        chunks = result.get("retrieved_chunks", [])
        if fmt == "json":
            return export_citations_json(question, answer, chunks, self.filing_bundle)
        return export_citations_markdown(question, answer, chunks, self.filing_bundle)
