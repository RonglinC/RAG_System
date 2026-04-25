"""
AI SEC Filing Analyzer - Streamlit Web UI

Interactive chatbot for analyzing SEC filings with RAG-powered question answering.

Run with: streamlit run app/streamlit_ui.py
"""

import streamlit as st
import os
from dotenv import load_dotenv

from sec.sec_client import SECClient
from sec.filing_service import FilingService
from rag.retriever import SimpleRetriever
from rag.embedding_retriever import EmbeddingRetriever
from rag.llm_client import LLMClient
from rag.pipeline import RAGPipeline
from rag.financial_metrics import FinancialMetricsExtractor


# Page configuration
st.set_page_config(
    page_title="AI SEC Filing Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .risk-high {
        color: #d62728;
        font-weight: bold;
    }
    .risk-medium {
        color: #ff7f0e;
        font-weight: bold;
    }
    .risk-low {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def load_environment():
    """Load environment variables."""
    load_dotenv()
    sec_user_agent = os.getenv("SEC_USER_AGENT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not sec_user_agent:
        st.error("❌ SEC_USER_AGENT not found in .env. Please configure it.")
        st.stop()
    
    if not openai_api_key:
        st.warning("⚠️ OPENAI_API_KEY not found. Some features may be limited.")
    
    return sec_user_agent


def initialize_session_state():
    """Initialize session state variables."""
    if "filing_data" not in st.session_state:
        st.session_state.filing_data = None
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def fetch_filing(ticker: str, form_type: str, sec_user_agent: str, use_embeddings: bool = False):
    """Fetch and prepare filing for analysis."""
    try:
        with st.spinner(f"📥 Fetching {form_type} filing for {ticker}..."):
            sec_client = SECClient(user_agent=sec_user_agent)
            filing_service = FilingService(sec_client=sec_client)
            
            filing_bundle = filing_service.build_chunks_for_latest_filing(
                ticker=ticker.upper(),
                form_type=form_type,
            )
        
        with st.spinner("🔍 Indexing chunks..."):
            # Choose retriever
            if use_embeddings:
                retriever = EmbeddingRetriever()
            else:
                retriever = SimpleRetriever()
            
            chunks_list = filing_bundle["chunks"]
            retriever.index(chunks_list)
        
        llm_client = LLMClient()
        pipeline = RAGPipeline(retriever=retriever, llm_client=llm_client)
        
        return {
            "filing_info": filing_bundle,
            "pipeline": pipeline,
            "success": True,
            "message": f"✅ Successfully loaded {len(chunks_list)} chunks"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error: {str(e)}"
        }


def main():
    """Main Streamlit app."""
    st.title("📊 AI SEC Filing Analyzer")
    st.markdown("Powered by RAG (Retrieval-Augmented Generation) and LLM")
    
    # Load environment
    sec_user_agent = load_environment()
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        ticker = st.text_input("Stock Ticker", value="AAPL", placeholder="e.g., AAPL, MSFT, TSLA").upper()
        form_type = st.selectbox("Filing Type", ["10-K", "10-Q"], index=0)
        use_embeddings = st.checkbox("Use Semantic Embeddings", value=False,
                                     help="Better quality but slower. Requires sentence-transformers.")
        retrieval_mode = st.radio("Analysis Mode", ["Custom Questions", "Predefined Tasks"])
        
        if st.button("🔄 Load Filing", use_container_width=True):
            result = fetch_filing(ticker, form_type, sec_user_agent, use_embeddings)
            
            if result["success"]:
                st.session_state.filing_data = result["filing_info"]
                st.session_state.pipeline = result["pipeline"]
                st.success(result["message"])
            else:
                st.error(result["message"])
    
    # Main content
    if st.session_state.filing_data is None:
        st.info("👈 Load a filing from the sidebar to begin analysis")
        return
    
    # Display filing info
    filing_info = st.session_state.filing_data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Company", filing_info.get("company_name", "Unknown")[:20])
    with col2:
        st.metric("Ticker", filing_info.get("ticker", ""))
    with col3:
        st.metric("Form", filing_info.get("form_type", ""))
    with col4:
        st.metric("Date", filing_info.get("filing_date", ""))
    
    st.divider()
    
    # Analysis interface
    if retrieval_mode == "Custom Questions":
        st.subheader("❓ Ask Questions About the Filing")
        
        question = st.text_area(
            "Your Question",
            placeholder="e.g., What are the main supply chain risks? How did revenue change year-over-year?",
            height=100
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            top_k = st.slider("Relevant Sections to Retrieve", 1, 10, 6)
        with col2:
            ask_button = st.button("📤 Ask", use_container_width=True)
        
        if ask_button and question:
            with st.spinner("🤔 Analyzing..."):
                result = st.session_state.pipeline.answer_question(question, top_k=top_k)
                
                # Display answer
                st.subheader("💡 Answer")
                st.write(result["response"])
                
                # Display sources
                with st.expander("📚 Retrieved Sources"):
                    for i, chunk in enumerate(result["retrieved_chunks"], 1):
                        st.markdown(f"**Source {i}** (Score: {chunk['score']:.2%})")
                        st.text(chunk["text"][:300] + "...")
                        st.divider()
    
    else:  # Predefined Tasks
        st.subheader("📋 Predefined Analysis Tasks")
        
        task_map = {
            "Business Summary": ("business_summary", "business overview products services strategy competition"),
            "Risk Analysis": ("risk_summary", "risk factors cybersecurity supply chain regulation competition macroeconomic"),
            "M&A Analysis": ("mdna_summary", "management discussion results of operations liquidity capital resources outlook"),
            "Financial Red Flags": ("financial_red_flags", "material weakness going concern liquidity debt impairment loss legal proceedings risk"),
        }
        
        selected_task = st.selectbox("Select Analysis", list(task_map.keys()))
        
        if st.button("🚀 Run Analysis", use_container_width=True):
            task_id, retrieval_query = task_map[selected_task]
            
            with st.spinner(f"⏳ Running {selected_task}..."):
                result = st.session_state.pipeline.run_task(
                    task=task_id,
                    company=filing_info.get("company_name", "Unknown"),
                    form_type=filing_info.get("form_type", ""),
                    retrieval_query=retrieval_query,
                    top_k=8,
                )
                
                st.markdown(result)


if __name__ == "__main__":
    main()
