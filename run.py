from retriever import SimpleRetriever
from pipeline import RAGPipeline
from dotenv import load_dotenv
from html_loader import load_knowledge_base
from llm_client import LLMClient



def main():
    load_dotenv()
    print("Loading financial reports...")
    docs = load_knowledge_base("./knowledge_base")
    
    retriever = SimpleRetriever(max_words=150, overlap=30)
    retriever.index(docs)
    llm_client=LLMClient()
    pipeline=RAGPipeline(retriever, llm_client)
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