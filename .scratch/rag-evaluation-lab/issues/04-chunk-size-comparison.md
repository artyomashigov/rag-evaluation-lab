# 04 — Chunk-size comparison

**What to build:** Add controlled small- and large-chunk experiments so a visitor can see how chunk size changes retrieval quality while every other setting remains fixed.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** resolved

- [x] The experiment runs 15-, 30-, and 60-token configurations with the same overlap, top-k, embedding model, and reranking setting.
- [x] Saved metadata makes it obvious that chunk size is the only changed variable.
- [x] Question-level results retain evidence and expected-section hit status for every chunk-size configuration.
- [x] The dashboard compares hit rate, chunk count, and retrieval latency across the three configurations.
- [x] A plain-English note explains the observed trade-off without claiming it applies to every corpus.
- [x] The evaluation-runner test verifies that chunk size changes the chunks while preserving stable source-section metadata.

## Answer

`python run_demo.py` now saves 15-, 30-, and 60-token runs. The dashboard compares their 45, 21, and 15 chunks, recorded latency, and identical 95.83% retrieval hit rate.
