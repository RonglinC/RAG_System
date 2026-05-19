from __future__ import annotations

import os
from typing import Literal, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.analyzer import SECFilingAnalyzer, TASK_QUERY_MAP
from rag.retriever_factory import RetrieverType

load_dotenv()

app = FastAPI(
    title="SEC Filing RAG API",
    description="Analyze SEC 10-K/10-Q filings with retrieval-augmented generation",
    version="2.1.0",
)

# In-memory session per process (single-user / demo; use Redis for multi-tenant prod)
_session: Optional[SECFilingAnalyzer] = None


class LoadFilingRequest(BaseModel):
    ticker: str = Field(..., examples=["AAPL"])
    form_type: str = Field(default="10-K", pattern="^(10-K|10-Q)$")
    retriever: RetrieverType = "tfidf"
    use_cache: bool = True


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=6, ge=1, le=20)


class TaskRequest(BaseModel):
    task: Literal[
        "business_summary",
        "risk_summary",
        "mdna_summary",
        "financial_red_flags",
    ]
    top_k: int = Field(default=8, ge=1, le=20)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "sec_configured": bool(os.getenv("SEC_USER_AGENT")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "filing_loaded": _session is not None and _session.filing_bundle is not None,
    }


@app.post("/filings/load")
def load_filing(req: LoadFilingRequest):
    global _session
    try:
        _session = SECFilingAnalyzer(
            retriever_type=req.retriever,
            use_cache=req.use_cache,
        )
        bundle = _session.load_filing(req.ticker, req.form_type)
        return {
            "status": "loaded",
            "ticker": bundle["ticker"],
            "company_name": bundle["company_name"],
            "form_type": bundle["form_type"],
            "filing_date": bundle["filing_date"],
            "chunk_count": len(bundle["chunks"]),
            "filing_html_url": bundle["filing_html_url"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/analyze/ask")
def analyze_ask(req: AskRequest):
    if _session is None or _session.pipeline is None:
        raise HTTPException(status_code=400, detail="Load a filing first via POST /filings/load")
    try:
        result = _session.ask(req.question, top_k=req.top_k)
        return {
            "question": result["question"],
            "answer": result["response"],
            "sources": result["retrieved_chunks"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/analyze/task")
def analyze_task(req: TaskRequest):
    if req.task not in TASK_QUERY_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown task: {req.task}")
    if _session is None or _session.pipeline is None:
        raise HTTPException(status_code=400, detail="Load a filing first via POST /filings/load")
    try:
        text = _session.run_task(req.task, top_k=req.top_k)
        return {"task": req.task, "analysis": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/tasks")
def list_tasks():
    return {"tasks": list(TASK_QUERY_MAP.keys())}
