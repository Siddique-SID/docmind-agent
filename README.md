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
PYTHONPATH=src pytest -q               # unit tests
python eval/run_eval.py                # retrieval evaluation
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

## Results
| Version | Retriever | Recall@3 | MRR | Notes |
|---|---|---|---|---|
| v0.1 | TF-IDF | - | - | Scaffold on 3 sample documents |
| v0.2 | TF-IDF (baseline) | 0.933 | 0.822 | 30 questions over 29 FastAPI docs (MIT). Misses: multi-parameter bodies, UUID/date types |

Questions are paraphrased from the documents rather than copied, so keyword overlap alone does not guarantee a hit. Corpus: FastAPI documentation, MIT licensed (see `data/fastapi_docs/LICENSE_FASTAPI`).

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
