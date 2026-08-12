# 10 — Document and publish the free demo

**What to build:** Make the finished lab reproducible and publicly viewable as a secret-free portfolio project that costs nothing when visitors explore it.

**Blocked by:** 09 — Recruiter-ready results dashboard

**Status:** resolved

- [x] The README explains the problem, controlled methodology, architecture, setup, benchmark command, results, limitations, and cost protection in plain English.
- [x] A fresh local checkout can install dependencies, run automated checks, and open the cached dashboard using the documented steps.
- [x] Dashboard controls are keyboard usable, charts have text summaries, contrast is readable, and desktop plus narrow layouts remain usable.
- [x] Deployment configuration contains no API keys and does not require a model provider account at runtime.
- [x] The public deployment loads the committed benchmark artifacts and works without visitor authentication or paid calls.
- [x] The README links to the public demo and includes enough screenshots or result examples to remain useful if hosting is temporarily unavailable.
- [x] A final smoke check confirms the public app shows the overview, comparisons, and evidence explorer without exposing secrets.

## Comments

Published the secret-free saved-results dashboard at https://rag-evaluation-lab.streamlit.app/. Anonymous session bootstrap completed with HTTP 200, the deployed app requires only Streamlit, and automated interaction checks cover the overview, comparison, and evidence explorer using the committed artifacts.

## Answer

Documented the experiment and its limitations, split lightweight hosting from optional benchmark dependencies, added CI and fallback result examples, published the free public dashboard, and verified anonymous access without model credentials or paid calls.
