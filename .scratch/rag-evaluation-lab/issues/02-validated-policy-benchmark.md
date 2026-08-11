# 02 — Validated policy benchmark

**What to build:** Replace the tiny example with the complete synthetic policy corpus and benchmark, and make their quality visible before any model experiment is trusted.

**Blocked by:** 01 — Baseline tracer bullet

**Status:** resolved

- [x] The corpus contains four to six clearly fictional employee-policy documents with stable document and section identifiers.
- [x] The benchmark contains exactly 30 questions covering direct answers, paraphrases, similar-policy distinctions, and at least six unanswerable cases.
- [x] Every question records its answerability, expected section, reference answer or expected abstention, and a short reviewer note.
- [x] Validation rejects duplicate identifiers, missing expected sections, and incomplete question metadata with a useful message.
- [x] The Streamlit view summarizes the corpus and benchmark counts so a visitor can verify what will be evaluated.
- [x] Automated checks cover one valid benchmark and representative invalid metadata.

## Answer

Added five clearly synthetic policy documents, 15 stable sections, and 30 labeled questions. The evaluation runner now validates identifiers and question semantics, preserves benchmark metadata in saved results, and exposes dataset counts in Streamlit.
