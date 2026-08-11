# 05 — Top-k comparison

**What to build:** Add a controlled top-3 versus top-5 experiment so a visitor can see whether retrieving more evidence improves coverage and what it costs in latency and context size.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** resolved

- [x] The top-3 and top-5 configurations share chunk size, overlap, embedding model, and reranking setting.
- [x] Saved metadata makes it obvious that top-k is the only changed variable.
- [x] Every question records the configured number of ranked results unless the corpus contains fewer candidates.
- [x] The dashboard compares retrieval hit rate, evidence count, and retrieval latency for top-3 and top-5.
- [x] A plain-English note explains the observed trade-off without treating more retrieved text as automatically better.
- [x] The evaluation-runner test verifies the result limit and aggregate hit calculation for both settings.

## Answer

`python run_demo.py` now saves a controlled top-5 variant beside the top-3 baseline. On the recorded run, top-5 increased retrieval hit rate from 95.83% to 100% while returning two additional evidence chunks per question.
