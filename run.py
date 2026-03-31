from retriever import SimpleRetriever
from pipeline import RAGPipeline
from dotenv import load_dotenv
from chunker import simple_chunk




def main():
    load_dotenv()
    docs={
        "doc1": "RAG stands for Retrieval-Augmented Generation. It combines retrieval with generation.",
        "doc2": "A retriever finds relevant context. An LLM then generates the final answer.",
        "doc3": "Chunking splits long documents into smaller pieces for retrieval.",
    }
    chunks=[]
    for doc_id, text in docs.items():
        for i, chunk in enumerate(simple_chunk(text, max_words=20)):
            chunks.append({
                "doc_id": doc_id,
                "chunk_id": f"{doc_id}_chunk{i}",
                "text": chunk
            })
    retriever=SimpleRetriever(chunks)
    pipeline=RAGPipeline(retriever)
    question="What is RAG and how does it work?"
    result=pipeline.answer_question(question)
    print("\nFinal Result:")
    print(result)

if __name__ == "__main__":
    main()