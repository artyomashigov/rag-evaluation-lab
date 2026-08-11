# 09 — Recruiter-ready results dashboard

**What to build:** Turn the audited artifacts into a focused three-minute portfolio story that leads with findings and still lets technical reviewers inspect the evidence.

**Blocked by:** 08 — Audited hallucination results

**Status:** ready-for-agent

- [ ] The overview explains RAG evaluation in plain English and highlights the strongest measured finding and the baseline.
- [ ] The comparison view presents retrieval hit rate, unsupported-answer rate, latency, and estimated cost for all configurations with text summaries for its charts.
- [ ] The evidence explorer shows the selected question, expected section, retrieved chunks, ranking changes, answer, citations, and manual review.
- [ ] Controls use clear labels and allow a visitor to compare configurations without understanding internal model code.
- [ ] Methodology and limitations state that conclusions apply to this synthetic corpus, benchmark, and selected models.
- [ ] Missing or malformed saved results produce a useful message instead of a stack trace or blank page.
- [ ] The dashboard runs entirely from saved artifacts and makes no model or paid network calls.
