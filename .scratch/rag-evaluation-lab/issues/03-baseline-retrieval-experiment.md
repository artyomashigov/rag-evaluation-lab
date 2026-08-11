# 03 — Baseline retrieval experiment

**What to build:** Run the full benchmark through the real baseline retrieval configuration and let a visitor inspect both the aggregate hit rate and the evidence behind each question.

**Blocked by:** 02 — Validated policy benchmark

**Status:** ready-for-agent

- [ ] The baseline uses 700-token chunks, fixed overlap, top-3 retrieval, and no reranking.
- [ ] A fixed local embedding model and direct similarity search retrieve evidence without a vector database or network call at query time.
- [ ] Chunk metadata preserves document, section, and character location so expected-section hits remain auditable.
- [ ] Running all 30 questions produces saved question-level results and a retrieval hit-rate summary.
- [ ] Retrieval latency is recorded with a monotonic clock and clearly identified as benchmark-run latency.
- [ ] The Streamlit view shows baseline metrics and the retrieved evidence for a selected question.
- [ ] The evaluation-runner test verifies top-k behavior, expected-section hit calculation, metadata preservation, and non-negative timing.
