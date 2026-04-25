from rag.retriever import SimpleRetriever
from rag.pipeline import RAGPipeline
from rag.llm_client import LLMClient

from sec.filing_loader import FilingLoader


loader = FilingLoader(user_agent="Your Name your@email.com")

docs = loader.load_latest_filing("AAPL", "10-K")

retriever = SimpleRetriever(max_words=40, overlap=10)

retriever.index(docs)

pipeline = RAGPipeline(retriever, LLMClient())

result = pipeline.answer_question(
    "What are the main supply chain risks?"
)

print(result["response"])