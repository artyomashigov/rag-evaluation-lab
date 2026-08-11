# 02 — Validated policy benchmark

**What to build:** Replace the tiny example with the complete synthetic policy corpus and benchmark, and make their quality visible before any model experiment is trusted.

**Blocked by:** 01 — Baseline tracer bullet

**Status:** ready-for-agent

- [ ] The corpus contains four to six clearly fictional employee-policy documents with stable document and section identifiers.
- [ ] The benchmark contains exactly 30 questions covering direct answers, paraphrases, similar-policy distinctions, and at least six unanswerable cases.
- [ ] Every question records its answerability, expected section, reference answer or expected abstention, and a short reviewer note.
- [ ] Validation rejects duplicate identifiers, missing expected sections, and incomplete question metadata with a useful message.
- [ ] The Streamlit view summarizes the corpus and benchmark counts so a visitor can verify what will be evaluated.
- [ ] Automated checks cover one valid benchmark and representative invalid metadata.
