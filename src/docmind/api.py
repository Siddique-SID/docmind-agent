"""FastAPI service: GET /health and POST /ask."""
import os

from fastapi import FastAPI
from pydantic import BaseModel

from .agent import answer
from .ingest import load_documents
from .retrieve import make_retriever

DATA_DIR = os.getenv("DOCMIND_DATA", "data/sample")
retriever = make_retriever(load_documents(DATA_DIR))
app = FastAPI(title="DocMind Agent", version="0.1.0")


class Query(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok", "chunks": len(retriever.chunks)}


@app.post("/ask")
def ask(query: Query):
    return answer(query.question, retriever)
