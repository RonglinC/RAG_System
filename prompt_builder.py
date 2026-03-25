from typing import List, Dict
import textwrap


PROMPT_TEMPLATE = textwrap.dedent("""
You are a helpful support assistant for a Corp.
Answer the user's question using ONLY the context below.
If the answer is not contained in the context, say "Sorry, I don't know".
Cite the source(s) after your answer in square brackets [].

Context:
{context}

User question:
{question}

Answer:
""")


def build_prompt(question: str, retrieved_chunks: List[Dict]) -> str:
    context_text = "\n\n".join(
        [f"{c['text']} [{c['doc_id']}]" for c in retrieved_chunks]
    )
    return PROMPT_TEMPLATE.format(context=context_text, question=question)