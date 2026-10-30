"""Answer questions from retrieved context. Uses Claude if ANTHROPIC_API_KEY is set,
otherwise falls back to returning the best matching passage (works offline)."""
import os

from .retrieve import Retriever

SYSTEM_PROMPT = (
    "Answer only from the provided context. Cite sources in the form [doc#chunk]. "
    "If the context does not contain the answer, say you cannot find it."
)


def answer(question: str, retriever: Retriever, k: int = 3) -> dict:
    hits = retriever.search(question, k=k)
    sources = [{"doc": c.doc_id, "chunk": c.chunk_id, "score": round(s, 3)} for c, s in hits]
    if not hits:
        return {"answer": "I could not find this in the documents.", "sources": [], "mode": "none"}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        return {**_llm_answer(question, hits, api_key), "sources": sources}

    best_chunk, _ = hits[0]
    return {
        "answer": best_chunk.text,
        "sources": sources,
        "mode": "extractive",
    }


def _llm_answer(question: str, hits, api_key: str) -> dict:
    import anthropic

    context = "\n\n".join(f"[{c.doc_id}#{c.chunk_id}] {c.text}" for c, _ in hits)
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=os.getenv("DOCMIND_MODEL", "claude-haiku-5-5"),
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}],
    )
    return {"answer": message.content[0].text, "mode": "llm"}
