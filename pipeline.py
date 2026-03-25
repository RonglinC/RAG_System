from retriever import SimpleRetriever
from prompt_builder import build_prompt


def mock_llm_response(prompt: str, question: str) -> str:
    question_lower = question.lower()

    if "return" in question_lower and "electronics" in question_lower:
        return (
            "You can return items within 30 days with a receipt. "
            "For electronics, the window is 15 days. [doc1.txt]"
        )

    if "shipping" in question_lower:
        return (
            "Orders are processed within 2 business days. "
            "Standard shipping takes 5-7 business days. [doc2.txt]"
        )

    if "warranty" in question_lower:
        return (
            "Acme electronics have a 1 year limited warranty covering "
            "manufacturing defects. [doc3.txt]"
        )

    return "I don't know. [no_source]"


class RAGPipeline:
    def __init__(self, retriever: SimpleRetriever):
        self.retriever = retriever

    def answer_question(self, question: str, k: int = 3) -> str:
        retrieved_chunks = self.retriever.retrieve(question, top_k=k)

        print("Retrieved Chunks:")
        for r in retrieved_chunks:
            print(f"- {r['chunk_id']} (score: {r['score']:.4f}) [{r['doc_id']}]")
            print(f"  {r['text']}")

        prompt = build_prompt(question, retrieved_chunks)

        print("\nConstructed Prompt:")
        print(prompt)

        response = mock_llm_response(prompt, question)

        print("\nLLM Response:")
        print(response)

        return response