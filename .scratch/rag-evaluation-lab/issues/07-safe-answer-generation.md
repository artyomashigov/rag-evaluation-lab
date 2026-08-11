# 07 — Safe answer generation

**What to build:** Generate grounded, cited answers locally without creating accidental spending, and preserve completed paid work if a later request fails.

**Blocked by:** 03 — Baseline retrieval experiment

**Status:** ready-for-agent

- [ ] The fixed answer model receives only the selected question and retrieved evidence and is instructed to cite source sections or abstain.
- [ ] Model calls are refused unless the local runner receives an explicit paid-call permission.
- [ ] Each completed question is checkpointed with its answer, citations, token counts, model identifier, and stage timings.
- [ ] An interrupted run resumes from completed questions instead of paying to regenerate them.
- [ ] Estimated cost uses recorded token counts and a dated price snapshot that remains visible in the result metadata.
- [ ] The Streamlit evidence view can display a saved answer, citations, abstention, latency, and estimated cost without an API key.
- [ ] Deterministic automated tests cover paid-call refusal, cited-answer result shape, checkpoint preservation, and resume behavior without contacting a model provider.
