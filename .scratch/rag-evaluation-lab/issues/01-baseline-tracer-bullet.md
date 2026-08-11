# 01 — Baseline tracer bullet

**What to build:** Make one tiny policy question travel through the evaluation runner, become a saved result, and appear in a minimal Streamlit view. This establishes the complete path and the single testing seam before the experiment grows.

**Blocked by:** None — can start immediately

**Status:** resolved

- [x] A tiny deterministic benchmark containing one policy section and one answerable question runs without network access or paid services.
- [x] The evaluation runner returns a structured result containing the question, expected section, retrieved evidence, and whether retrieval hit the expected section.
- [x] The result can be saved, loaded again, and displayed in a minimal Streamlit view.
- [x] One automated test exercises the complete behavior through the evaluation runner interface.
- [x] The project has only the dependencies and local run instructions needed for this slice.

## Answer

Implemented an offline lexical retrieval tracer with a saved JSON result, minimal Streamlit evidence view, one evaluation-runner test, and local run instructions. Real embeddings remain intentionally deferred to ticket 03.
