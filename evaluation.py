from rag.retriever import SimpleRetriever


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

eval_data = [
    {
        "question": "What is the return policy for electronics?",
        "expected_doc": "doc1.txt",
    },
    {
        "question": "What is the shipping policy?",
        "expected_doc": "doc2.txt",
    },
    {
        "question": "What warranty do Acme electronics have?",
        "expected_doc": "doc3.txt",
    },
]


def recall_at_k(eval_data, retriever, k=1):
    hits = 0

    for item in eval_data:
        results = retriever.retrieve(item["question"], top_k=k)
        returned_docs = [r["doc_id"] for r in results]

        if item["expected_doc"] in returned_docs:
            hits += 1

        print(f"Question: {item['question']}")
        print(f"Expected: {item['expected_doc']}")
        print(f"Returned: {returned_docs}")
        print()

    return hits / len(eval_data)


def main():
    retriever = SimpleRetriever(max_words=40, overlap=10)
    retriever.index(docs)

    for k in [1, 2, 3]:
        score = recall_at_k(eval_data, retriever, k=k)
        print(f"Recall@{k}: {score:.2f}")
        print("-" * 40)


if __name__ == "__main__":
    main()