# 09 — Recruiter-ready results dashboard

**What to build:** Turn the audited artifacts into a focused three-minute portfolio story that leads with findings and still lets technical reviewers inspect the evidence.

**Blocked by:** 08 — Audited hallucination results

**Status:** resolved

- [x] The overview explains RAG evaluation in plain English and highlights the strongest measured finding and the baseline.
- [x] The comparison view presents retrieval hit rate, unsupported-answer rate, latency, and estimated cost for all configurations with text summaries for its charts.
- [x] The evidence explorer shows the selected question, expected section, retrieved chunks, ranking changes, answer, citations, and manual review.
- [x] Controls use clear labels and allow a visitor to compare configurations without understanding internal model code.
- [x] Methodology and limitations state that conclusions apply to this synthetic corpus, benchmark, and selected models.
- [x] Missing or malformed saved results produce a useful message instead of a stack trace or blank page.
- [x] The dashboard runs entirely from saved artifacts and makes no model or paid network calls.

## Answer

Reworked the saved-results dashboard into a three-part portfolio story: a plain-English findings overview, an accessible configuration comparison with chart summaries, and a question-level evidence explorer. Added validation so missing or malformed artifacts show recovery guidance, while the app remains fully offline.
