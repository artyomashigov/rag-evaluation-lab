# 06 — Reranking comparison

**What to build:** Add one local reranking step and show whether its changed ordering improves retrieval enough to justify its extra latency.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** ready-for-agent

- [ ] The reranking configuration shares the baseline chunk size, overlap, top-k, and embedding model.
- [ ] Reranking starts from a fixed larger candidate pool and retains only the configured top-k results.
- [ ] Question-level results record original rank, reranked position, final evidence, and expected-section hit status.
- [ ] Reranking latency is recorded separately from initial retrieval latency.
- [ ] The dashboard compares reranking off versus on for hit rate and latency and exposes changed rankings.
- [ ] A plain-English note explains whether the measured improvement justifies the added step on this benchmark.
- [ ] The evaluation-runner test proves reranking can change order without changing the requested result count.
