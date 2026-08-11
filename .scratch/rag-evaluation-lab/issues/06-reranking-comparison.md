# 06 — Reranking comparison

**What to build:** Add one local reranking step and show whether its changed ordering improves retrieval enough to justify its extra latency.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** resolved

- [x] The reranking configuration shares the baseline chunk size, overlap, top-k, and embedding model.
- [x] Reranking starts from a fixed larger candidate pool and retains only the configured top-k results.
- [x] Question-level results record original rank, reranked position, final evidence, and expected-section hit status.
- [x] Reranking latency is recorded separately from initial retrieval latency.
- [x] The dashboard compares reranking off versus on for hit rate and latency and exposes changed rankings.
- [x] A plain-English note explains whether the measured improvement justifies the added step on this benchmark.
- [x] The evaluation-runner test proves reranking can change order without changing the requested result count.

## Answer

The local cross-encoder reranks a fixed pool of 10 candidates before retaining the top three. On the saved offline run, hit rate increased from 95.83% to 100%, 27 of 30 question rankings changed, and reranking added 20.2 ms per question on average.
