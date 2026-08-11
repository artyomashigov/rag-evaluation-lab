# 05 — Top-k comparison

**What to build:** Add a controlled top-3 versus top-5 experiment so a visitor can see whether retrieving more evidence improves coverage and what it costs in latency and context size.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** ready-for-agent

- [ ] The top-3 and top-5 configurations share chunk size, overlap, embedding model, and reranking setting.
- [ ] Saved metadata makes it obvious that top-k is the only changed variable.
- [ ] Every question records the configured number of ranked results unless the corpus contains fewer candidates.
- [ ] The dashboard compares retrieval hit rate, evidence count, and retrieval latency for top-3 and top-5.
- [ ] A plain-English note explains the observed trade-off without treating more retrieved text as automatically better.
- [ ] The evaluation-runner test verifies the result limit and aggregate hit calculation for both settings.
