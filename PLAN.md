# Two-Week Delivery Plan

**Goal:** a public, deployed, measured document Q&A agent with a clean GitHub history.
**Time budget:** 2 weeks. Scope is fixed. Anything not on this list goes to the roadmap.

## Definition of done
- [ ] Live demo link in the README
- [ ] CI green on `main` (tests + evaluation gate)
- [ ] Results table with at least two configurations compared
- [ ] Architecture diagram and "trade-offs" section in the README
- [ ] 60-second demo video or GIF at the top of the README
- [ ] Tagged release `v1.0.0` with release notes

## Week 1: working system and baseline

| Day | Milestone | Output |
|---|---|---|
| 1 | Scaffold, tests, eval, CI (done) | v0.1 pushed |
| 2 | Replace sample data with a real corpus (20–50 public documents) | `data/` populated, ingestion verified |
| 3 | Write 50 labelled questions, including paraphrased ones | `eval/questions.jsonl` expanded |
| 4 | Embedding retriever (sentence-transformers or Voyage/OpenAI) | `retrieve.py` supports both |
| 5 | Hybrid search (BM25 + vector) and baseline metrics | Results table row v0.2 |

Week 1 exit check: baseline numbers committed, CI green.

## Week 2: improve, deploy, present

| Day | Milestone | Output |
|---|---|---|
| 6 | Reranking step and before/after evaluation | Results table row v0.3 |
| 7 | LLM answer mode with faithfulness check on 30 answers | `agent.py` tested with a fixed prompt |
| 8 | MCP server exposing `search_docs` (optional if time is tight) | `mcp/` folder with README |
| 9 | Deploy (Render, Railway or Fly.io free tier) and add the live link | Demo URL in README |
| 10 | Demo GIF, architecture diagram, write-up of trade-offs | README complete |
| 11 | Release `v1.0.0`, clean history, pinned dependencies | Tag and release notes |
| 12 | Buffer day. Fix anything broken. Do not add features. | Final CI green |

## Scope cuts if you fall behind (in this order)
1. Drop the MCP server.
2. Drop reranking; keep hybrid search.
3. Use a smaller corpus.
Never cut: evaluation, CI gate, README results table, live demo.

## GitHub workflow

**Branches:** `main` is always green. Work happens on `feat/<short-name>` branches.

**Issues:** one issue per milestone row above, labelled `week-1` or `week-2`. Close each issue with a link to its merged PR.

**Pull requests:** every change goes through a PR, even solo. Each PR body contains:
- What changed
- Eval numbers before and after (paste from `eval/results.json`)
- Screenshot or output if the change is user-visible

**Commit style:** short imperative messages, e.g. `add hybrid retriever`, `fix chunk overlap bug`.

**Project board:** three columns (Todo, Doing, Done) with the milestone issues.

**Releases:** tag `v0.x` at the end of each milestone, `v1.0.0` at the end of week 2.

**Daily rhythm:**
1. Start: pull `main`, pick one milestone, open an issue or branch.
2. Middle: commit small, run `pytest` and `python eval/run_eval.py` before pushing.
3. End: open the PR, update the results table, merge if CI is green.

## First-push commands
```bash
cd docmind-agent
git init -b main
git add .
git commit -m "v0.1: scaffold with retrieval, API, eval gate and CI"
gh repo create docmind-agent --public --source=. --push
git tag v0.1.0 && git push --tags
```
(Requires the GitHub CLI `gh`. Without it, create an empty repo on github.com and run `git remote add origin <url>` then `git push -u origin main`.)
