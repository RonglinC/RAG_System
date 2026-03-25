from typing import List, Dict
import numpy as np
import textwrap
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# example (short docs)
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

# Chunking function
def simple_chunk(text:str,max_words:int=40,overlap:int=10)->List[str]:
    #split text into chuncks
    if overlap >= max_words:
        raise ValueError("Overlap must be less than max_words")
    words = text.split()
    chunks = []
    i = 0
    step=max_words - overlap
    while i <len(words):
        chunk_words = words[i:i+max_words]
        chunks.append(" ".join(chunk_words))
        i += step
    return chunks

# Build chunks with metadata
# a list of dicts with the chunk
corpus_chunks=[]
for doc_id, text in docs.items():
    chunks=simple_chunk(text,max_words=40,overlap=10)
    for i ,c in enumerate(chunks):
        corpus_chunks.append({
            "id":f"{doc_id}_chunk{i}",
            "text":c,
            "doc_id":doc_id
        })
# Create TF-IDF vectorizer and fit on chunks
texts=[c["text"] for c in corpus_chunks]
#fit the vectorizer on all chunk texts 
# convert each chunk into a vector of numbers represent word importance
vectorizer = TfidfVectorizer().fit(texts)
# Transform all chunks into vectors
embeddings=vectorizer.fit_transform(texts)

# Retrieve (cosine similarity)
def retrieve(query:str,top_k:int=3)->List[Dict]:
    #return top-k chunks with the same vectorizer
    query_vec=vectorizer.transform([query])
    # computes cosine similarity between the query and all chunk vectors 
    sims=cosine_similarity(query_vec,embeddings)[0]
    # indices of top-k most similar chunks 
    top_indices=np.argsort(sims)[::-1][:top_k]
    # returns the top-k chunks with their scores and metadata
    results=[]
    for idx in top_indices:
        results.append({
            "chunk_id":corpus_chunks[idx]["id"],
            "doc_id":corpus_chunks[idx]["doc_id"],
            "text":corpus_chunks[idx]["text"],
            "score":float(sims[idx])
        })
    return results

#prompt construction 
PROMPT_TEMPLATE = textwrap.dedent("""
You are a helpful support assistant for Acme Corp. Answer the user's question using ONLY the context below.
If the answer is not contained in the context, say "I don't know".
Cite the source(s) after your answer in square brackets [].

Context:
{context}

User question:
{question}

Answer:
""")
def build_prompt(question:str,retrieved_chunks:List[Dict])->str:
    #Join chunks with their source metadata
    context_text="\n\n".join([f"{c['text']} [{c['doc_id']}]" for c in retrieved_chunks])
    return PROMPT_TEMPLATE.format(context=context_text,question=question)

def mock_llm_response(prompt:str)->str:
    """
    This is a placeholder. Replace this with your LLM call (OpenAI, local model, etc.)
    For the demo we return a simple canned answer if the word 'return' is in context.
    """
    if "return" in prompt.lower():
        return "You can return items within 30 days with a receipt. For electronics, the window is 15 days. [doc1.txt]"
    return "I don't know. [no_source]"

def answer_question(question:str,k:int=3)->str:
    retrieved_chunks=retrieve(question,top_k=k)
    print("Retrieved Chunks:")
    for r in retrieved_chunks:
        print(f"- {r['chunk_id']} (score: {r['score']:.4f}): {r['text']} [{r['doc_id']}]")
        print(f"{r['text']} [{r['doc_id']}]")
    prompt=build_prompt(question,retrieved_chunks)
    print("\nConstructed Prompt:")
    print(prompt)
    response=mock_llm_response(prompt)
    print("\nLLM Response:")
    print(response)
    return response

if __name__ == "__main__":
    question="What is Acme's return policy for electronics?"
    answer_question(question)
