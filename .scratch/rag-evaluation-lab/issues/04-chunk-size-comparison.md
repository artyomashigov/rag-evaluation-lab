# 04 — Chunk-size comparison

**What to build:** Add controlled small- and large-chunk experiments so a visitor can see how chunk size changes retrieval quality while every other setting remains fixed.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** ready-for-agent

- [ ] The experiment runs 300-, 700-, and 1,200-token configurations with the same overlap, top-k, embedding model, and reranking setting.
- [ ] Saved metadata makes it obvious that chunk size is the only changed variable.
- [ ] Question-level results retain evidence and expected-section hit status for every chunk-size configuration.
- [ ] The dashboard compares hit rate, chunk count, and retrieval latency across the three configurations.
- [ ] A plain-English note explains the observed trade-off without claiming it applies to every corpus.
- [ ] The evaluation-runner test verifies that chunk size changes the chunks while preserving stable source-section metadata.
