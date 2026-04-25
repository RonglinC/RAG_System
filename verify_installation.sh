#!/bin/bash
# Verification Checklist for AI SEC Filing Analyzer

echo "═══════════════════════════════════════════════════════════════════"
echo "   AI SEC Filing Analyzer - Installation Verification Checklist"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
GREEN="\\033[0;32m"
RED="\\033[0;31m"
YELLOW="\\033[1;33m"
NC="\\033[0m" # No Color

check_count=0
pass_count=0
fail_count=0

function check_file() {
    local file=$1
    local desc=$2
    check_count=$((check_count + 1))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $check_count. $desc: $file"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $check_count. $desc: $file NOT FOUND"
        fail_count=$((fail_count + 1))
    fi
}

function check_directory() {
    local dir=$1
    local desc=$2
    check_count=$((check_count + 1))
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $check_count. $desc: $dir"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $check_count. $desc: $dir NOT FOUND"
        fail_count=$((fail_count + 1))
    fi
}

function check_command() {
    local cmd=$1
    local desc=$2
    check_count=$((check_count + 1))
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $check_count. $desc: $cmd installed"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $check_count. $desc: $cmd NOT INSTALLED"
        fail_count=$((fail_count + 1))
    fi
}

echo "Part 1: Core Python Module Files"
echo "──────────────────────────────────────────────────────────────────"
check_file "sec/sec_client.py" "SEC Client"
check_file "sec/filing_service.py" "Filing Service"
check_file "sec/filing_parser.py" "Filing Parser"
check_file "rag/retriever.py" "TF-IDF Retriever"
check_file "rag/embedding_retriever.py" "Embedding Retriever"
check_file "rag/chunker.py" "Chunker"
check_file "rag/llm_client.py" "LLM Client"
check_file "rag/pipeline.py" "RAG Pipeline"
check_file "rag/prompt_builder.py" "Prompt Builder"
check_file "rag/financial_metrics.py" "Financial Metrics"
echo ""

echo "Part 2: Application Entry Points"
echo "──────────────────────────────────────────────────────────────────"
check_file "app/cli.py" "CLI Interface"
check_file "app/streamlit_ui.py" "Streamlit Web UI"
echo ""

echo "Part 3: Configuration Files"
echo "──────────────────────────────────────────────────────────────────"
check_file "requirement.txt" "Python Dependencies"
check_file ".env.example" "Environment Template"
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} $((++check_count)). Environment Configuration: .env"
    pass_count=$((pass_count + 1))
else
    echo -e "${YELLOW}⚠${NC} $((++check_count)). Environment Configuration: .env (use 'cp .env.example .env')"
    fail_count=$((fail_count + 1))
fi
echo ""

echo "Part 4: Documentation"
echo "──────────────────────────────────────────────────────────────────"
check_file "README.md" "User Guide"
check_file "QUICKSTART.md" "Quick Start"
check_file "ARCHITECTURE.md" "Architecture Guide"
check_file "IMPROVEMENTS.md" "Improvements List"
check_file "PROJECT_SUMMARY.md" "Project Summary"
echo ""

echo "Part 5: Directory Structure"
echo "──────────────────────────────────────────────────────────────────"
check_directory "rag" "RAG Module Directory"
check_directory "sec" "SEC Module Directory"
check_directory "app" "App Module Directory"
echo ""

echo "Part 6: Python Installation"
echo "──────────────────────────────────────────────────────────────────"
check_command "python3" "Python 3"
echo ""

echo "Part 7: Python Package Check"
echo "──────────────────────────────────────────────────────────────────"
python3 << 'EOF'
import sys
packages = [
    ('openai', 'OpenAI API'),
    ('dotenv', 'Python Dotenv'),
    ('sklearn', 'Scikit-Learn'),
    ('bs4', 'BeautifulSoup4'),
    ('streamlit', 'Streamlit'),
]

for pkg, name in packages:
    try:
        __import__(pkg)
        print(f"\033[0;32m✓\033[0m Package {name} installed")
    except ImportError:
        print(f"\033[0;31m✗\033[0m Package {name} NOT installed - run: pip install -r requirement.txt")
EOF
echo ""

echo "Part 8: Environment Variables"
echo "──────────────────────────────────────────────────────────────────"
if [ -f ".env" ]; then
    if grep -q "SEC_USER_AGENT" .env; then
        echo -e "${GREEN}✓${NC} SEC_USER_AGENT configured"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} SEC_USER_AGENT not in .env"
        fail_count=$((fail_count + 1))
    fi
    check_count=$((check_count + 1))
    
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "${GREEN}✓${NC} OPENAI_API_KEY configured"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} OPENAI_API_KEY not in .env"
        fail_count=$((fail_count + 1))
    fi
    check_count=$((check_count + 1))
else
    echo -e "${YELLOW}⚠${NC} .env file not found - create with: cp .env.example .env"
    fail_count=$((fail_count + 2))
    check_count=$((check_count + 2))
fi
echo ""

echo "Part 9: Functional Tests"
echo "──────────────────────────────────────────────────────────────────"

# Test imports
echo -n "Testing Python imports... "
python3 << 'EOF' > /dev/null 2>&1
try:
    from sec.sec_client import SECClient
    from sec.filing_service import FilingService
    from rag.retriever import SimpleRetriever
    from rag.embedding_retriever import EmbeddingRetriever
    from rag.llm_client import LLMClient
    from rag.pipeline import RAGPipeline
    from rag.financial_metrics import FinancialMetricsExtractor
    from app.cli import main
    print("OK")
except ImportError as e:
    print(f"FAILED: {e}")
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} All imports successful"
    pass_count=$((pass_count + 1))
else
    echo -e "${RED}✗${NC} Import test failed"
    fail_count=$((fail_count + 1))
fi
check_count=$((check_count + 1))
echo ""

echo "═══════════════════════════════════════════════════════════════════"
echo "SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo "Total Checks: $check_count"
echo -e "Passed: ${GREEN}$pass_count${NC}"
echo -e "Failed: ${RED}$fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! System is ready to use.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure .env with your credentials"
    echo "2. Run: streamlit run app/streamlit_ui.py"
    echo "   OR: python -m app.cli --ticker AAPL --task risk_summary"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix issues above.${NC}"
    echo ""
    if ! grep -q "OPENAI_API_KEY" .env 2>/dev/null; then
        echo "Quick fix:"
        echo "1. cp .env.example .env"
        echo "2. Edit .env with your API credentials"
    fi
    exit 1
fi
