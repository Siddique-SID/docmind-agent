"""Retrieval evaluation: recall@K and MRR over eval/questions.jsonl.
Exits non-zero if recall falls below THRESHOLD, so CI fails on regressions."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from docmind.ingest import load_documents  # noqa: E402
from docmind.retrieve import Retriever  # noqa: E402

K = 3
THRESHOLD = 0.8


def main() -> int:
    lines = (ROOT / "eval" / "questions.jsonl").read_text(encoding="utf-8").splitlines()
    questions = [json.loads(line) for line in lines if line.strip()]
    retriever = Retriever(load_documents(ROOT / "data" / "fastapi_docs"))

    hits, reciprocal_rank_sum = 0, 0.0
    misses = []
    for q in questions:
        ranked_docs = []
        for chunk, _ in retriever.search(q["question"], k=K):
            if chunk.doc_id not in ranked_docs:
                ranked_docs.append(chunk.doc_id)
        if q["expected_doc"] in ranked_docs:
            hits += 1
            reciprocal_rank_sum += 1 / (ranked_docs.index(q["expected_doc"]) + 1)
        else:
            misses.append(q["question"])

    recall = hits / len(questions)
    report = {
        "questions": len(questions),
        f"recall@{K}": round(recall, 3),
        "mrr": round(reciprocal_rank_sum / len(questions), 3),
        "threshold": THRESHOLD,
        "misses": misses,
    }
    (ROOT / "eval" / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if recall >= THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
