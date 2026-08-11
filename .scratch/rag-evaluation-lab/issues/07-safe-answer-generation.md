# 07 — Safe answer generation

**What to build:** Generate grounded, cited answers locally without creating accidental spending, and preserve completed paid work if a later request fails.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** resolved

- [x] The fixed answer model receives only the selected question and retrieved evidence and is instructed to cite source sections or abstain.
- [x] Model calls are refused unless the local runner receives an explicit paid-call permission.
- [x] Each completed question is checkpointed with its answer, citations, token counts, model identifier, and stage timings.
- [x] An interrupted run resumes from completed questions instead of paying to regenerate them.
- [x] Estimated cost uses recorded token counts and a dated price snapshot that remains visible in the result metadata.
- [x] The Streamlit evidence view can display a saved answer, citations, abstention, latency, and estimated cost without an API key.
- [x] Deterministic automated tests cover paid-call refusal, cited-answer result shape, checkpoint preservation, and resume behavior without contacting a model provider.

## Answer

Answer generation uses gated GPT-5.6 Luna calls with structured cited-or-abstained output, atomic per-question checkpoints, resume support, token accounting, and a 2026-08-11 price snapshot. Free runs remain offline and write zero generation cost; `--allow-paid-calls` writes separate answered artifacts so paid work cannot be erased by a later free run.
