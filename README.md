# DocMind Agent

A document question-answering service with retrieval, source citations, and an automated evaluation gate.

Ask a question about a set of documents and get an answer with the source chunks it came from. Without an API key it runs fully offline using extractive retrieval. With `ANTHROPIC_API_KEY` set, it generates grounded answers with Claude and cites `[doc#chunk]`.

## Why it is built this way
- **Measured, not guessed.** `eval/run_eval.py` reports recall@3 and MRR on a labelled question set. CI fails if retrieval quality drops below the threshold.
- **Runs offline.** The default retriever is TF-IDF, so the project works with no paid services. Embeddings and hybrid search are the next milestone.
- **Honest answers.** The LLM is instructed to answer only from context and to say when the answer is missing.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/fetch_corpus.py         # download the pinned FastAPI docs (evaluation corpus)
PYTHONPATH=src pytest -q               # unit tests
PYTHONPATH=src python eval/run_eval.py # retrieval evaluation
PYTHONPATH=src uvicorn docmind.api:app --reload
```
Then open http://127.0.0.1:8000/docs and try `POST /ask` with `{"question": "How many days of paid leave do I get?"}`.

Docker:
```bash
docker build -t docmind-agent . && docker run -p 8000:8000 docmind-agent
```

## Architecture
```
data/*.md ──► ingest (chunk) ──► retrieve (TF-IDF) ──► agent ──► answer + sources
                                                        │
                                        Claude (if key set) / extractive (offline)
eval/questions.jsonl ──► run_eval.py ──► recall@k, MRR ──► CI gate
```

## Retrievers
Choose the retrieval method with the `DOCMIND_RETRIEVER` environment variable:

| Mode | Needs | Description |
|---|---|---|
| `tfidf` (default) | nothing | Lexical TF-IDF retrieval, fully offline |
| `embedding` | `OPENAI_API_KEY` | Dense embeddings (`text-embedding-3-small` by default) |
| `hybrid` | `OPENAI_API_KEY` | Reciprocal rank fusion of TF-IDF and embedding rankings |

```bash
DOCMIND_RETRIEVER=hybrid OPENAI_API_KEY=... PYTHONPATH=src python eval/run_eval.py
```

## Results
| Version | Retriever | Recall@3 | MRR | Notes |
|---|---|---|---|---|
| v0.1 | TF-IDF | - | - | Scaffold on 3 sample documents |
| v0.4 | Embedding | pending | pending | Run with `DOCMIND_RETRIEVER=embedding` and an API key |
| v0.4 | Hybrid | pending | pending | Run with `DOCMIND_RETRIEVER=hybrid` and an API key |
| v0.2 | TF-IDF (baseline) | 0.933 | 0.789 | 30 questions over 29 FastAPI docs pinned to commit `79cab5b` (MIT). Misses: multi-parameter bodies, UUID/date types |

Questions are paraphrased from the documents rather than copied, so keyword overlap alone does not guarantee a hit. Corpus: FastAPI documentation, MIT licensed, downloaded by `scripts/fetch_corpus.py` at a pinned commit so numbers are reproducible.

## Roadmap
- [ ] Embedding retriever and hybrid (BM25 + vector) search
- [ ] Reranking step with before/after metrics
- [ ] Answer-level evaluation (correctness and faithfulness)
- [ ] MCP server exposing `search_docs` as a tool
- [ ] Cost and latency tracking per query
- [ ] Deployed demo link

## Project layout
```
src/docmind/   core package (ingest, retrieve, agent, api)
eval/          labelled questions and evaluation script
data/sample/   example documents (fictional company policies)
tests/         unit tests
.github/       CI workflow
```

## License
MIT
