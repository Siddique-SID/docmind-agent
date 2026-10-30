import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest  # noqa: E402

from docmind.agent import answer  # noqa: E402
from docmind.ingest import chunk_text, load_documents  # noqa: E402
from docmind.retrieve import Retriever  # noqa: E402


def test_chunk_text_overlaps():
    words = " ".join(f"w{i}" for i in range(50))
    chunks = chunk_text(words, max_words=20, overlap=5)
    assert len(chunks) >= 3
    assert chunks[0].split()[-5:] == chunks[1].split()[:5]


def test_chunk_text_rejects_bad_params():
    with pytest.raises(ValueError):
        chunk_text("hello world", max_words=5, overlap=5)


def test_empty_text_gives_no_chunks():
    assert chunk_text("   ") == []


def test_retriever_finds_relevant_document():
    retriever = Retriever(load_documents(ROOT / "data" / "sample"))
    hits = retriever.search("parental leave weeks", k=1)
    assert hits and hits[0][0].doc_id == "leave_policy.md"


def test_answer_cites_source_when_offline(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    retriever = Retriever(load_documents(ROOT / "data" / "sample"))
    result = answer("What is the hotel cap abroad?", retriever)
    assert result["mode"] == "extractive"
    assert result["sources"][0]["doc"] == "expense_policy.md"


def test_answer_refuses_when_nothing_matches(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    retriever = Retriever(load_documents(ROOT / "data" / "sample"))
    result = answer("zebra spaceship quantum violin", retriever)
    assert result["mode"] == "none"
