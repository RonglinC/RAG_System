"""
AI SEC Filing Analyzer - Streamlit Web UI

Run from project root:
    streamlit run streamlit_app.py
Or:
    streamlit run app/streamlit_ui.py
"""

import sys
from pathlib import Path

# Streamlit adds `app/` to sys.path; put project root first so `app` and `rag` resolve.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import os

import streamlit as st
from dotenv import load_dotenv

from app.analyzer import SECFilingAnalyzer
from rag.financial_metrics import FinancialMetricsExtractor


st.set_page_config(
    page_title="AI SEC Filing Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-box { background-color: #f0f2f6; padding: 20px; border-radius: 8px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)


def load_environment():
    load_dotenv()
    sec_user_agent = os.getenv("SEC_USER_AGENT")
    if not sec_user_agent:
        st.error("SEC_USER_AGENT not found in .env. Please configure it.")
        st.stop()
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("OPENAI_API_KEY not found. LLM answers may use fallback mode.")
    return sec_user_agent


def initialize_session_state():
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def fetch_filing(ticker: str, form_type: str, retriever_type: str, use_cache: bool):
    try:
        with st.spinner(f"Fetching {form_type} filing for {ticker}..."):
            analyzer = SECFilingAnalyzer(
                retriever_type=retriever_type,
                use_cache=use_cache,
            )
            bundle = analyzer.load_filing(ticker.upper(), form_type)
        st.session_state.analyzer = analyzer
        return True, f"Loaded {len(bundle['chunks'])} chunks ({retriever_type})"
    except Exception as e:
        return False, str(e)


def main():
    st.title("AI SEC Filing Analyzer")
    st.caption("RAG over SEC 10-K / 10-Q filings")

    load_environment()
    initialize_session_state()

    with st.sidebar:
        st.header("Configuration")
        ticker = st.text_input("Stock Ticker", value="AAPL").upper()
        form_type = st.selectbox("Filing Type", ["10-K", "10-Q"])
        retriever_type = st.selectbox(
            "Retriever",
            ["tfidf", "embedding", "hybrid"],
            index=2,
            help="Hybrid combines TF-IDF + semantic embeddings (recommended).",
        )
        use_cache = st.checkbox("Use disk cache", value=True)
        analysis_mode = st.radio("Analysis Mode", ["Custom Questions", "Predefined Tasks"])

        if st.button("Load Filing", use_container_width=True):
            ok, msg = fetch_filing(ticker, form_type, retriever_type, use_cache)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

    analyzer: SECFilingAnalyzer | None = st.session_state.analyzer
    if analyzer is None or analyzer.filing_bundle is None:
        st.info("Load a filing from the sidebar to begin.")
        return

    filing = analyzer.filing_bundle
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Company", (filing.get("company_name") or "Unknown")[:24])
    c2.metric("Ticker", filing.get("ticker", ""))
    c3.metric("Form", filing.get("form_type", ""))
    c4.metric("Date", filing.get("filing_date", ""))

    st.divider()

    if analysis_mode == "Custom Questions":
        st.subheader("Ask Questions")
        question = st.text_area("Your Question", height=100)
        top_k = st.slider("Sections to retrieve", 1, 10, 6)

        if st.button("Ask", use_container_width=True) and question:
            with st.spinner("Analyzing..."):
                result = analyzer.ask(question, top_k=top_k)
                st.session_state.last_result = result
                st.subheader("Answer")
                st.write(result["response"])
                with st.expander("Retrieved Sources"):
                    for i, chunk in enumerate(result["retrieved_chunks"], 1):
                        section = chunk.get("metadata", {}).get("section", "")
                        st.markdown(f"**{i}.** {section} — score {chunk['score']:.2%}")
                        st.text(chunk["text"][:400] + "...")
    else:
        st.subheader("Predefined Tasks")
        labels = {
            "Business Summary": "business_summary",
            "Risk Analysis": "risk_summary",
            "MD&A Analysis": "mdna_summary",
            "Financial Red Flags": "financial_red_flags",
        }
        label = st.selectbox("Task", list(labels.keys()))
        if st.button("Run Analysis", use_container_width=True):
            with st.spinner("Running..."):
                text = analyzer.run_task(labels[label])
                st.session_state.last_result = {
                    "question": f"Task: {label}",
                    "response": text,
                    "retrieved_chunks": [],
                }
                st.markdown(text)

    st.divider()
    st.subheader("Export & Metrics")

    if st.session_state.last_result:
        col_a, col_b = st.columns(2)
        result = st.session_state.last_result
        with col_a:
            if st.download_button(
                "Download Markdown",
                analyzer.export_last_answer(result, "markdown"),
                file_name=f"{filing['ticker']}_analysis.md",
                mime="text/markdown",
            ):
                pass
        with col_b:
            if st.download_button(
                "Download JSON",
                analyzer.export_last_answer(result, "json"),
                file_name=f"{filing['ticker']}_analysis.json",
                mime="application/json",
            ):
                pass

    if st.checkbox("Show extracted metrics (sample from first chunk)"):
        chunks = filing.get("chunks") or []
        if chunks:
            sample = chunks[0]["text"][:8000]
            metrics = FinancialMetricsExtractor.extract_all_metrics(sample)
            if metrics:
                for m in metrics[:8]:
                    st.write(f"- **{m.name}**: {m.value} ({m.unit})")
            else:
                st.caption("No metrics matched in sample text.")


if __name__ == "__main__":
    main()
