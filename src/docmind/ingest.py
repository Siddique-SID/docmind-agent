"""Load documents from disk and split them into overlapping word chunks."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    doc_id: str
    chunk_id: int
    text: str


def chunk_text(text: str, max_words: int = 120, overlap: int = 20) -> list[str]:
    if max_words <= overlap:
        raise ValueError("max_words must be greater than overlap")
    words = text.split()
    if not words:
        return []
    step = max_words - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + max_words]))
        if start + max_words >= len(words):
            break
    return chunks


def load_documents(folder) -> list[Chunk]:
    folder = Path(folder)
    paths = sorted(folder.glob("**/*.md")) + sorted(folder.glob("**/*.txt"))
    chunks: list[Chunk] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for i, piece in enumerate(chunk_text(text)):
            chunks.append(Chunk(doc_id=path.name, chunk_id=i, text=piece))
    return chunks
