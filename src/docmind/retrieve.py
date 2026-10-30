"""Retrievers.

- TfidfRetriever: lexical, offline, no API key (default).
- EmbeddingRetriever: dense vectors from an embeddings API (OPENAI_API_KEY).
- HybridRetriever: reciprocal rank fusion of the two rankings.

Select one with DOCMIND_RETRIEVER=tfidf|embedding|hybrid (see make_retriever).
"""
import os
from collections.abc import Callable

import httpx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .ingest import Chunk

EmbedFn = Callable[[list[str]], np.ndarray]


def openai_embed(texts: list[str]) -> np.ndarray:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Set OPENAI_API_KEY to use the embedding or hybrid retriever.")
    model = os.getenv("DOCMIND_EMBED_MODEL", "text-embedding-3-small")
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model, "input": texts},
        timeout=60,
    )
    response.raise_for_status()
    rows = sorted(response.json()["data"], key=lambda row: row["index"])
    return np.array([row["embedding"] for row in rows], dtype=np.float32)


def _normalise(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(norms, 1e-12, None)


class TfidfRetriever:
    def __init__(self, chunks: list[Chunk]):
        if not chunks:
            raise ValueError("No chunks to index. Check the data folder.")
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([c.text for c in chunks])

    def search(self, query: str, k: int = 3) -> list[tuple[Chunk, float]]:
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        top = scores.argsort()[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top if scores[i] > 0]


class EmbeddingRetriever:
    def __init__(self, chunks: list[Chunk], embed: EmbedFn = openai_embed):
        if not chunks:
            raise ValueError("No chunks to index. Check the data folder.")
        self.chunks = chunks
        self.embed = embed
        self.matrix = _normalise(embed([c.text for c in chunks]))

    def search(self, query: str, k: int = 3) -> list[tuple[Chunk, float]]:
        q = _normalise(self.embed([query]))
        scores = (self.matrix @ q.T).ravel()
        top = scores.argsort()[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top]


class HybridRetriever:
    """Fuses TF-IDF and embedding rankings with reciprocal rank fusion (RRF)."""

    def __init__(self, chunks: list[Chunk], embed: EmbedFn = openai_embed, rrf_k: int = 60):
        self.chunks = chunks
        self.lexical = TfidfRetriever(chunks)
        self.dense = EmbeddingRetriever(chunks, embed)
        self.rrf_k = rrf_k

    def search(self, query: str, k: int = 3, depth: int = 20) -> list[tuple[Chunk, float]]:
        fused: dict[tuple[str, int], float] = {}
        by_key: dict[tuple[str, int], Chunk] = {}
        for ranking in (self.lexical.search(query, k=depth), self.dense.search(query, k=depth)):
            for rank, (chunk, _) in enumerate(ranking, start=1):
                key = (chunk.doc_id, chunk.chunk_id)
                by_key[key] = chunk
                fused[key] = fused.get(key, 0.0) + 1.0 / (self.rrf_k + rank)
        best = sorted(fused.items(), key=lambda item: item[1], reverse=True)[:k]
        return [(by_key[key], score) for key, score in best]


def make_retriever(chunks: list[Chunk], mode: str | None = None):
    mode = (mode or os.getenv("DOCMIND_RETRIEVER", "tfidf")).lower()
    if mode == "tfidf":
        return TfidfRetriever(chunks)
    if mode == "embedding":
        return EmbeddingRetriever(chunks)
    if mode == "hybrid":
        return HybridRetriever(chunks)
    raise ValueError(f"Unknown DOCMIND_RETRIEVER: {mode!r}")


# Backwards-compatible name used by earlier versions.
Retriever = TfidfRetriever
