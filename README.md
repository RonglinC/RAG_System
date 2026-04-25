# AI SEC Filing Analyzer 📊

A production-ready **Retrieval-Augmented Generation (RAG)** system for analyzing SEC filings (10-K, 10-Q). Ask questions about company financials, risks, and operations—get answers backed by official documents.

## Features

✨ **Key Capabilities**
- 📥 Automatically download SEC filings from EDGAR
- 🔍 Semantic search with TF-IDF or embeddings  
- 🤖 LLM-powered analysis with source citations
- 📊 Extract financial metrics (revenue, debt, ratios)
- 🚨 Identify financial red flags automatically
- 💬 Interactive chat interface (Streamlit)
- ⚡ CLI for automation and scripting
- 🧪 Fallback mode if LLM API unavailable

## Quick Start

### 1. Install Dependencies

```bash
# Clone or download the project
cd RAG_System

# Install required packages
pip install -r requirement.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required variables:**
```
SEC_USER_AGENT="Your Name your@email.com"  # For SEC API compliance
OPENAI_API_KEY="sk-..."                    # From platform.openai.com
OPENAI_MODEL="gpt-3.5-turbo"              # or gpt-4
```

### 3. Run the Application

#### Option A: Interactive Web UI (Recommended for beginners)
```bash
streamlit run app/streamlit_ui.py
# Opens at http://localhost:8501
```

#### Option B: Command Line
```bash
# Analyze AAPL 10-K with risk analysis
python -m app.cli --ticker AAPL --form 10-K --mode task --task risk_summary

# Ask a custom question
python -m app.cli --ticker MSFT --form 10-Q --mode ask \
  --question "What are the main supply chain risks?"
```

#### Option C: Python Script
```python
from sec.sec_client import SECClient
from sec.filing_service import FilingService
from rag.retriever import SimpleRetriever
from rag.llm_client import LLMClient
from rag.pipeline import RAGPipeline
import os
from dotenv import load_dotenv

load_dotenv()
sec_user_agent = os.getenv("SEC_USER_AGENT")

# Load filing
sec_client = SECClient(user_agent=sec_user_agent)
filing_service = FilingService(sec_client=sec_client)
filing = filing_service.build_chunks_for_latest_filing("AAPL", "10-K")

# Search and answer
retriever = SimpleRetriever()
retriever.index(filing["chunks"])

pipeline = RAGPipeline(retriever, LLMClient())
result = pipeline.answer_question("What are the main risks?", top_k=6)

print(result["response"])
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ SEC EDGAR API                                               │
│ (Financial filings: 10-K, 10-Q)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ SEC CLIENT & FILING SERVICE                                 │
│ • Ticker → CIK lookup                                       │
│ • Download HTML filings                                     │
│ • Extract text & parse sections                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ CHUNKING & INDEXING                                         │
│ • Sliding window: 220 words/chunk, 40-word overlap          │
│ • Section-aware metadata (Risk, MD&A, etc.)                │
│ • TF-IDF or Semantic Embeddings                             │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴────────────┐
         ▼                        ▼
┌──────────────────┐      ┌──────────────────┐
│ RETRIEVER (TF-IDF)      │ RETRIEVER (SBERT)│
│ Fast, simple     │      │ Better semantic  │
└──────┬───────────┘      └────────┬─────────┘
       │                          │
       └──────────────┬───────────┘
                      ▼
        ┌─────────────────────────────┐
        │ TOP-K RELEVANT CHUNKS       │
        │ (with similarity scores)     │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ PROMPT BUILDER               │
        │ • Context from chunks        │
        │ • Instruction for analysis   │
        │ • Financial domain prompt    │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ LLM (GPT-3.5/4 or Custom)    │
        │ Generates analysis            │
        │ with fallback mode            │
        └──────────┬───────────────────┘
                   │
                   ▼
        ┌──────────────────────────────┐
        │ RESPONSE                      │
        │ • Analysis text              │
        │ • Source citations            │
        │ • Structured insights         │
        └──────────────────────────────┘
```

---

## Use Cases

### Financial Analysis
```bash
# Comprehensive risk assessment
python -m app.cli --ticker AAPL --task risk_summary

# Business overview
python -m app.cli --ticker MSFT --task business_summary

# Management discussion analysis
python -m app.cli --ticker TSLA --task mdna_summary

# Red flags detection
python -m app.cli --ticker GM --task financial_red_flags
```

### Custom Questions
```bash
python -m app.cli --ticker AAPL --mode ask \
  --question "What percentage of revenue comes from services vs products?"

python -m app.cli --ticker META --mode ask \
  --question "How much debt does the company have due in the next 12 months?"

python -m app.cli --ticker NVDA --mode ask \
  --question "What are the dependencies on Taiwan for manufacturing?"
```

### Automated Monitoring
```bash
# Batch monitor multiple companies
for ticker in AAPL MSFT GOOGL AMZN NVDA; do
  python -m app.cli --ticker $ticker --task financial_red_flags >> risks.txt
done
```

---

## Configuration Options

### Retrieverselection

**Fast (TF-IDF):**
```python
from rag.retriever import SimpleRetriever
retriever = SimpleRetriever(max_words=40, overlap=10)
```

**Better Quality (Embeddings):**
```python
from rag.embedding_retriever import EmbeddingRetriever
retriever = EmbeddingRetriever(model_name="all-MiniLM-L6-v2")
```

### Chunking Parameters

```python
from rag.chunker import SlidingWindowChunker

chunker = SlidingWindowChunker(
    max_words=220,      # Chunk size
    overlap=40          # Overlap between chunks
)
```

### LLM Configuration

```python
from rag.llm_client import LLMClient

client = LLMClient(
    model="gpt-4",      # Model choice
    temperature=0.2,    # Lower = more deterministic
    max_tokens=500      # Response length
)
```

---

## Improvements Made (v2)

✅ **bugs Fixed**
- Fixed import errors (FilingParser, SlidingWindowChunker)
- Fixed missing SEC client methods
- Fixed RAGPipeline missing run_task method
- Fixed typo in requirements (oepnai → openai)

✅ **Architecture Enhancements**
- Added section-aware metadata to chunks
- Implemented semantic embedding retriever
- Built financial metrics extraction system
- Created Streamlit web interface

✅ **New Capabilities**
- Financial metrics extraction (revenue, debt, ratios)
- Red flag detection framework
- Predefined analysis tasks
- Embedding-based retrieval for better semantics

---

## Project Structure

```
RAG_System/
├── app/
│   ├── cli.py                    # Command-line interface
│   ├── analyzer.py               # Analysis orchestration
│   └── streamlit_ui.py          # Web interface (new)
├── rag/
│   ├── chunker.py               # Text chunking with metadata
│   ├── retriever.py             # TF-IDF retriever
│   ├── embedding_retriever.py   # SBERT retriever (new)
│   ├── llm_client.py            # LLM integration with fallback
│   ├── pipeline.py              # RAG pipeline orchestration
│   ├── prompt_builder.py        # Prompt construction
│   └── financial_metrics.py     # Financial metrics extraction (new)
├── sec/
│   ├── sec_client.py            # SEC API client (enhanced)
│   ├── filing_service.py        # Filing processing pipeline
│   ├── filing_parser.py         # HTML parsing & section detection
│   ├── filing_loader.py         # Legacy filing loader
│   └── ticker_to_click.py       # Ticker lookup utility
├── problem_requirements.txt       # Dependencies
├── .env.example                 # Environment template
├── ARCHITECTURE.md              # Detailed architecture guide (new)
└── README.md                    # This file
```

---

## Supported Companies

Pre-cached CIK lookups for common companies:
- Apple (AAPL)
- Microsoft (MSFT)  
- Tesla (TSLA)
- Google (GOOGL)
- Meta (META)
- NVIDIA (NVDA)
- Amazon (AMZN)

Other companies pulled automatically from SEC database.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'rag'"
**Solution:** Run from project root and install dependencies
```bash
cd /path/to/RAG_System
pip install -r requirement.txt
python -m app.cli --ticker AAPL
```

### "Please set SEC_USER_AGENT in .env"
**Solution:** Create `.env` file with SEC user agent
```bash
cp .env.example .env
# Edit .env with your SEC_USER_AGENT
```

### "Cannot reach the OpenAI API"
**Solution 1:** Check your API key
```bash
echo $OPENAI_API_KEY  # Should print your key
```

**Solution 2:** Use fallback mode (returns generic message)
```python
# Fallback mode activates automatically on auth failure
# Allows testing without valid API key
```

### "No recent 10-K filing found for TICKER"
**Solution:** Check if company has public filings
```bash
# Verify on SEC EDGAR: https://www.sec.gov/cgi-bin/browse-edgar
```

---

## Performance Tips

1. **Use embeddings for better quality** (slower but more accurate)
   ```bash
   streamlit run app/streamlit_ui.py  # Check "Use Semantic Embeddings"
   ```

2. **Cache filings locally** (avoid re-downloading)
   ```python
   # Filings cached after first download
   ```

3. **Adjust chunk size** based on task
   - Small chunks (40 words): Fast, good for specific facts
   - Large chunks (220 words): Context-rich, better for analysis

4. **Use GPT-4** for complex financial analysis
   ```
   OPENAI_MODEL=gpt-4
   ```

---

## Advanced Features

### Financial Metrics Extraction
```python
from rag.financial_metrics import FinancialMetricsExtractor

metrics = FinancialMetricsExtractor.extract_all_metrics(
    text,
    section="Item 8 Financial Statements"
)

# Calculates automatically:
# - Revenue, net income, EPS
# - Debt, cash, working capital
# - Ratios (ROE, ROA, margins)
```

### Custom LLM Providers
```python
from rag.llm_client import LLMClient

# Use Claude Opus
client = LLMClient(
    model="claude-3-opus-20240229",
    base_url="https://api.anthropic.com/v1"
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

---

## Next Steps

1. 🎯 **Use the Streamlit UI** for interactive exploration
2. 📚 **Read ARCHITECTURE.md** for deep technical details
3. 🧪 **Experiment with different retrievers** (TF-IDF vs Embeddings)
4. 🚀 **Deploy as API** using FastAPI (see ARCHITECTURE.md)
5. 📊 **Add visualizations** for financial metrics

---

## Contributing

Suggestions for improvement:
- [ ] Support for other document types (earnings transcripts, proxy statements)
- [ ] Multi-year comparative analysis
- [ ] Peer group comparison
- [ ] Automated portfolio risk aggregation
- [ ] Fine-tuned financial domain LLM

---

## License

[Add your license]

## Support

- 📖 See [ARCHITECTURE.md](ARCHITECTURE.md) for advanced topics
- 🐛 Report issues on GitHub
- 💬 Discussions welcome

---

## Acknowledgments

- SEC EDGAR API for data access
- Sentence Transformers for semantic embeddings
- OpenAI for LLM capabilities
- Streamlit for web UI framework

---

**Happy analyzing! 📊**
