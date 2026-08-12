# 08 — Audited hallucination results

**What to build:** Complete and manually review the five-configuration benchmark so unsupported-answer and abstention rates are transparent, reproducible portfolio evidence.

**Blocked by:** 04 — Chunk-size comparison; 05 — Top-k comparison; 06 — Reranking comparison; 07 — Safe answer generation

**Status:** resolved

- [x] All 30 questions have saved retrieval and answer results for the baseline and four one-variable variants.
- [x] Every generated answer is manually labeled as supported, unsupported, or a correct abstention, with an optional reviewer note.
- [x] Unsupported labels identify a material claim not backed by cited retrieved text or an answer given for an unanswerable question.
- [x] No answer included in aggregate hallucination or abstention metrics is missing its review label.
- [x] Summary results report retrieval hit rate, unsupported-answer rate, correct-abstention rate, stage latency, token usage, and estimated cost for all five configurations.
- [x] The dashboard lets a visitor filter question-level evidence by configuration and review label.
- [x] Saved public artifacts contain no API keys, confidential data, or provider request headers.

## Answer

Generated all 150 answers locally with Qwen 2.5 3B through Ollama at $0 API cost, manually reviewed each answer, saved auditable labels and notes, calculated comparison metrics, and added dashboard filters for configuration and review label.
