# Quick Start Guide - Get Running in 5 Minutes

## Prerequisites
- Python 3.8+
- OpenAI API key (get one at https://platform.openai.com)
- SEC user agent string (your name + email for SEC API compliance)

---

## Step 1: Install Packages (2 minutes)

```bash
cd RAG_System
pip install -r requirement.txt
```

**What gets installed:**
- `openai` - LLM API
- `sentence-transformers` - Semantic embeddings
- `scikit-learn` - TF-IDF retrieval
- `beautifulsoup4` & `lxml` - HTML parsing
- `streamlit` - Web UI
- Plus other dependencies

---

## Step 2: Configure Environment (1 minute)

Copy the template:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
# .env file
SEC_USER_AGENT="John Doe john@example.com"
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-3.5-turbo"
```

**Where to get these:**
- `SEC_USER_AGENT`: Use your name + email (for SEC API politeness)
- `OPENAI_API_KEY`: https://platform.openai.com/api-keys
- `OPENAI_MODEL`: `gpt-3.5-turbo` (fast), `gpt-4` (better)

---

## Step 3: Run (Choose One) - 1 minute

### Option A: Web Interface (Easiest) 🌐
```bash
streamlit run app/streamlit_ui.py
```
Opens http://localhost:8501 in your browser

**What you can do:**
- Load any SEC filing by ticker
- Ask questions in a chat interface
- Run predefined analysis tasks
- View sources and metrics

### Option B: Command Line 💻
```bash
# Risk analysis
python -m app.cli --ticker AAPL --task risk_summary

# Custom question
python -m app.cli --ticker MSFT --mode ask \
  --question "What are the main risks?"

# Business overview
python -m app.cli --ticker TSLA --task business_summary
```

### Option C: Python Script 🐍
```python
from sec.sec_client import SECClient
from sec.filing_service import FilingService
from rag.retriever import SimpleRetriever
from rag.llm_client import LLMClient
from rag.pipeline import RAGPipeline
import os
from dotenv import load_dotenv

load_dotenv()

# 1. Fetch filing
sec_client = SECClient(user_agent=os.getenv("SEC_USER_AGENT"))
filing_service = FilingService(sec_client=sec_client)
filing = filing_service.build_chunks_for_latest_filing("AAPL", "10-K")

# 2. Index chunks
retriever = SimpleRetriever()
retriever.index(filing["chunks"])

# 3. Answer questions
pipeline = RAGPipeline(retriever, LLMClient())
result = pipeline.answer_question("What are the main risks?", top_k=6)

print(result["response"])
```

---

## Step 4: Test It Works ✅

Try this simple test:
```bash
python -m app.cli --ticker AAPL --form 10-K --task risk_summary
```

**Expected output:**
```
================================================================================
Company: Apple Inc. (AAPL)
Form: 10-K
Filing Date: 2025-10-31
Source: https://www.sec.gov/...
================================================================================

╔════════════════════════════════════════════════════════════════╗
║                    RISK ANALYSIS                    ║
║         Apple Inc. - 10-K Filing Analysis              ║
╚════════════════════════════════════════════════════════════════╝

[LLM-generated risk analysis...]
────────────────────────────────────────────────────────────────
Sources Retrieved: 8 sections from 10-K filing
────────────────────────────────────────────────────────────────
```

---

## Try More Examples

```bash
# Microsoft financial red flags
python -m app.cli --ticker MSFT --task financial_red_flags

# Tesla custom question
python -m app.cli --ticker TSLA --mode ask \
  --question "How much revenue comes from battery sales?"

# Google MD&A analysis
python -m app.cli --ticker GOOGL --task mdna_summary

# Nvidia business summary
python -m app.cli --ticker NVDA --task business_summary
```

---

## Troubleshooting

### 1. "Please set SEC_USER_AGENT in .env"
```bash
# Make sure .env file exists and has SEC_USER_AGENT set
cat .env
```

### 2. "Cannot reach the OpenAI API"
- Check your API key is correct
- Verify API key has credits (https://platform.openai.com/account/usage)
- If using different provider, update `OPENAI_BASE_URL`

### 3. "ModuleNotFoundError: No module named 'rag'"
```bash
# Make sure you're in the right directory
cd /path/to/RAG_System

# And run with -m (module)
python -m app.cli --ticker AAPL
```

### 4. "No recent 10-K filing found for TICKER"
- Some companies don't have public 10-K filings
- Try a major company: AAPL, MSFT, GOOGL
- Check SEC EDGAR: https://www.sec.gov/

---

## Upgrade to Better Retrieval

By default uses TF-IDF (fast). For better accuracy, use embeddings:

```bash
# In Streamlit UI: check "Use Semantic Embeddings"

# Or in Python:
from rag.embedding_retriever import EmbeddingRetriever

retriever = EmbeddingRetriever()  # Instead of SimpleRetriever()
```

**Trade-off:**
- TF-IDF: Fast (100ms), good enough
- Embeddings: Slower (500ms), better answers (15-30% improvement)

---

## Next Steps

1. **Read full README.md** for detailed documentation
2. **Read ARCHITECTURE.md** for advanced topics
3. **Read IMPROVEMENTS.md** to understand what was fixed
4. **Explore the code** in `rag/` and `sec/` folders
5. **Customize prompts** in `rag/pipeline.py` for your use case

---

## Common Use Cases

### Financial Analyst
```bash
# Batch analyze multiple companies
for ticker in AAPL MSFT GOOGL AMZN; do
  python -m app.cli --ticker $ticker --task risk_summary
done
```

### Investor Due Diligence
```bash
pythonchosen -m app.cli --ticker $TICKER --form 10-K --task financial_red_flags
```

### Research
```bash
python -m app.cli --ticker $TICKER --mode ask \
  --question "What is the company's strategy in [specific area]?"
```

### Monitoring
```bash
# Check for new red flags continuously
watch -n 86400 'python -m app.cli --ticker AAPL --task financial_red_flags'
```

---

## Performance Tips

**Fast mode (for testing):**
```bash
python -m app.cli --ticker AAPL --task risk_summary
# Uses TF-IDF, returns in ~2-3 seconds
```

**Best quality (for analysis):**
```python
retriever = EmbeddingRetriever()
# Takes longer but 15-30% better answers
```

---

## What This System Does

1. ✅ Downloads latest company filings from SEC
2. ✅ Parses HTML and extracts text
3. ✅ Chunks text intelligently with overlap
4. ✅ Indexes chunks for fast retrieval
5. ✅ Answers questions by combining:
   - Semantic search (find relevant context)
   - LLM reasoning (generate answer from context)
6. ✅ Returns answers with source citations

---

## Architecture (Simple View)

```
Question
   ↓
What SEC documents have this info?
   ↓ (Retrieve)
Top 6 relevant chunks
   ↓
Combine chunks + question
   ↓ (LLM)
Answer
```

---

## File Breakdown

| File | Purpose |
|------|---------|
| `app/cli.py` | Command-line interface |
| `app/streamlit_ui.py` | Web interface |
| `sec/sec_client.py` | Downloads filings |
| `rag/retriever.py` | Finds relevant chunks |
| `rag/llm_client.py` | Calls LLM API |
| `rag/pipeline.py` | Orchestrates everything |

---

## Support

- 🐛 Check IMPROVEMENTS.md for fixes to common issues
- 📖 Read ARCHITECTURE.md for technical deep dives
- 💬 See README.md for full documentation
- 🔗 SEC EDGAR API: https://www.sec.gov/

---

**You're ready! Start exploring: `streamlit run app/streamlit_ui.py` 🚀**
