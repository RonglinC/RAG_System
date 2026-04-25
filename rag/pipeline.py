from __future__ import annotations
from typing import List, Dict
from rag.prompt_builder import build_prompt
from rag.llm_client import LLMClient
from rag.retriever import SimpleRetriever


class RAGPipeline:
    def __init__(self, retriever: SimpleRetriever, llm_client: LLMClient):
        self.retriever = retriever
        self.llm_client = llm_client or LLMClient()

    def answer_question(self, question: str, top_k: int = 3) -> Dict:
        """Answer a question using retrieved context."""
        retrieved_chunks = self.retriever.retrieve(question, top_k=top_k)
        prompt = build_prompt(question, retrieved_chunks)
        response = self.llm_client.generate(prompt)

        return {
            "question": question,
            "retrieved_chunks": retrieved_chunks,
            "response": response
        }

    def run_task(
        self,
        task: str,
        company: str,
        form_type: str,
        retrieval_query: str,
        top_k: int = 8
    ) -> str:
        """
        Run a predefined analysis task.
        
        Args:
            task: Task type (e.g., 'risk_summary', 'business_summary')
            company: Company name
            form_type: Form type (e.g., '10-K')
            retrieval_query: Query to retrieve relevant chunks
            top_k: Number of top chunks to retrieve
            
        Returns:
            Formatted analysis result as string
        """
        retrieved_chunks = self.retriever.retrieve(retrieval_query, top_k=top_k)
        
        task_prompts = {
            "business_summary": self._build_business_summary_prompt,
            "risk_summary": self._build_risk_summary_prompt,
            "mdna_summary": self._build_mdna_summary_prompt,
            "financial_red_flags": self._build_financial_red_flags_prompt,
        }
        
        if task not in task_prompts:
            raise ValueError(f"Unknown task: {task}")
        
        prompt = task_prompts[task](company, form_type, retrieved_chunks)
        response = self.llm_client.generate(prompt)
        
        return self._format_task_result(task, company, form_type, retrieved_chunks, response)

    def _build_business_summary_prompt(self, company: str, form_type: str, chunks: List[Dict]) -> str:
        """Build prompt for business summary task."""
        context = "\n\n".join([f"[{c['doc_id']}]: {c['text']}" for c in chunks])
        return f"""Based on the following excerpts from {company}'s {form_type} filing, provide a comprehensive summary of:
1. Business Overview: Main products and services
2. Strategy: Key strategic initiatives 
3. Competition: Competitive landscape and advantages
4. Market Position: Market segments and customer base

Context from filing:
{context}

Provide a concise, well-structured analysis."""

    def _build_risk_summary_prompt(self, company: str, form_type: str, chunks: List[Dict]) -> str:
        """Build prompt for risk summary task."""
        context = "\n\n".join([f"[{c['doc_id']}]: {c['text']}" for c in chunks])
        return f"""Based on the following excerpts from {company}'s {form_type} filing, identify and summarize the main risks:
1. Operational Risks
2. Market and Competition Risks
3. Supply Chain and Cybersecurity Risks
4. Regulatory and Macroeconomic Risks
5. Financial Risks

Context from filing:
{context}

Organize risks by severity and likelihood. Be specific with examples from the filing."""

    def _build_mdna_summary_prompt(self, company: str, form_type: str, chunks: List[Dict]) -> str:
        """Build prompt for MD&A summary task."""
        context = "\n\n".join([f"[{c['doc_id']}]: {c['text']}" for c in chunks])
        return f"""Based on the MD&A section from {company}'s {form_type} filing, summarize:
1. Financial Results: Revenue and profitability trends
2. Operational Metrics: Key performance indicators
3. Liquidity and Capital Resources: Cash flow and financing
4. Future Outlook: Management guidance and expectations

Context from filing:
{context}

Focus on year-over-year comparisons and management's forward-looking statements."""

    def _build_financial_red_flags_prompt(self, company: str, form_type: str, chunks: List[Dict]) -> str:
        """Build prompt for financial red flags task."""
        context = "\n\n".join([f"[{c['doc_id']}]: {c['text']}" for c in chunks])
        return f"""Based on {company}'s {form_type} filing, identify financial red flags and concerns:
1. Material Weaknesses in Internal Controls
2. Going Concern Issues
3. Liquidity Problems or Cash Flow Issues
4. Debt and Leverage Concerns
5. Impairments, Restructuring, or One-time Charges
6. Pending Legal Proceedings

Context from filing:
{context}

Focus on items that could indicate financial distress or deteriorating business health."""

    def _format_task_result(self, task: str, company: str, form_type: str, chunks: List[Dict], response: str) -> str:
        """Format task result with metadata."""
        task_names = {
            "business_summary": "Business Summary",
            "risk_summary": "Risk Analysis",
            "mdna_summary": "MD&A Analysis",
            "financial_red_flags": "Financial Red Flags",
        }
        
        result = f"""
╔════════════════════════════════════════════════════════════════╗
║                    {task_names.get(task, task).upper()}                    ║
║         {company} - {form_type} Filing Analysis              ║
╚════════════════════════════════════════════════════════════════╝

{response}

────────────────────────────────────────────────────────────────
Sources Retrieved: {len(chunks)} sections from {form_type} filing
────────────────────────────────────────────────────────────────
"""
        return result