# 08 — Audited hallucination results

**What to build:** Complete and manually review the five-configuration benchmark so unsupported-answer and abstention rates are transparent, reproducible portfolio evidence.

**Blocked by:** 04 — Chunk-size comparison; 05 — Top-k comparison; 06 — Reranking comparison; 07 — Safe answer generation

**Status:** ready-for-agent

- [ ] All 30 questions have saved retrieval and answer results for the baseline and four one-variable variants.
- [ ] Every generated answer is manually labeled as supported, unsupported, or a correct abstention, with an optional reviewer note.
- [ ] Unsupported labels identify a material claim not backed by cited retrieved text or an answer given for an unanswerable question.
- [ ] No answer included in aggregate hallucination or abstention metrics is missing its review label.
- [ ] Summary results report retrieval hit rate, unsupported-answer rate, correct-abstention rate, stage latency, token usage, and estimated cost for all five configurations.
- [ ] The dashboard lets a visitor filter question-level evidence by configuration and review label.
- [ ] Saved public artifacts contain no API keys, confidential data, or provider request headers.
