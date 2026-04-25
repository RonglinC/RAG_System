from rag.retriever import SimpleRetriever
from rag.pipeline import RAGPipeline
from html_loader import load_knowledge_base
from rag.llm_client import LLMClient



def main():
    print("Loading financial reports...")
    docs = load_knowledge_base("./knowledge_base")
    
    retriever = SimpleRetriever(max_words=150, overlap=30)
    retriever.index(docs)
    pipeline=RAGPipeline(retriever=retriever, llm_client=LLMClient())
    print("Your Finance QA Bot read!")
    while True:
        question=input("\nAsk a question about the financial reports (or 'exit' to quit): ")
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        result=pipeline.answer_question(question)
        print("\nBot:", result["response"])
        print()
if __name__ == "__main__":
    main()