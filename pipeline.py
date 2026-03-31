from prompt_builder import build_prompt
from llm_client import LLMClient
from retriever import SimpleRetriever


class RAGPipeline:
    def __init__(self, retriever: SimpleRetriever, llm_client: LLMClient):
        self.retriever = retriever
        self.llm_client = llm_client or LLMClient()

    def answer_question(self, question: str, k: int = 3) -> str:
        retrieved_chunks = self.retriever.retrieve(question, top_k=k)
        prompt = build_prompt(question, retrieved_chunks)
        response = self.llm_client.generate(prompt)

        return {
            "question": question,
            "retrieved_chunks": retrieved_chunks,
            "response": response
        }