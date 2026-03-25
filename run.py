from retriever import SimpleRetriever
from pipeline import RAGPipeline


docs = {
    "doc1.txt": (
        "Acme Corp's return policy: you may return items within 30 days with receipt. "
        "Electronic goods have a 15 day return window."
    ),
    "doc2.txt": (
        "Shipping: Orders are processed within 2 business days. "
        "Standard shipping takes 5-7 business days."
    ),
    "doc3.txt": (
        "Warranty: Acme electronics have a 1 year limited warranty "
        "covering manufacturing defects."
    )
}


def main():
    retriever = SimpleRetriever(max_words=40, overlap=10)
    retriever.index(docs)

    pipeline = RAGPipeline(retriever)

    question = "What is the shipping policy?"
    pipeline.answer_question(question, k=3)


if __name__ == "__main__":
    main()