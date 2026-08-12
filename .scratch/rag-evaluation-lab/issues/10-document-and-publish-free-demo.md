# 10 — Document and publish the free demo

**What to build:** Make the finished lab reproducible and publicly viewable as a secret-free portfolio project that costs nothing when visitors explore it.

**Blocked by:** 09 — Recruiter-ready results dashboard

**Status:** ready-for-human

- [x] The README explains the problem, controlled methodology, architecture, setup, benchmark command, results, limitations, and cost protection in plain English.
- [x] A fresh local checkout can install dependencies, run automated checks, and open the cached dashboard using the documented steps.
- [ ] Dashboard controls are keyboard usable, charts have text summaries, contrast is readable, and desktop plus narrow layouts remain usable.
- [x] Deployment configuration contains no API keys and does not require a model provider account at runtime.
- [ ] The public deployment loads the committed benchmark artifacts and works without visitor authentication or paid calls.
- [ ] The README links to the public demo and includes enough screenshots or result examples to remain useful if hosting is temporarily unavailable.
- [ ] A final smoke check confirms the public app shows the overview, comparisons, and evidence explorer without exposing secrets.

## Comments

Implementation, checks, dependency split, CI, and fallback result examples are complete. Publishing remains a human step because Streamlit Community Cloud requires account authentication and GitHub authorization; the final public URL cannot be verified until that deployment is created and made public.
