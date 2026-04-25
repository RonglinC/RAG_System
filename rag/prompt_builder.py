from __future__ import annotations
from typing import List, Dict

def build_prompt(question,retrieved_chunks):
    context_blocks=[]
    for chunk in retrieved_chunks:
        context_blocks.append(
            f"{chunk['doc_id']} [source: {chunk['text']}]"
        )
    context="\n\n".join(context_blocks)
    prompt=f"""
    You are financial report assistant.
    Use the following company financial report excerpts to answer the questions.
    Rules:
    - only answer using the provided context
    - if the answer is not in the context, say "I don't know"
    - cite the source(s) after your answer in square brackets []
    Context:
    {context}
    Question:
    {question}
    Answer:
    """
    return prompt.strip()
