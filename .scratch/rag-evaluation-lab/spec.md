# RAG Evaluation Lab

Status: ready-for-agent

## Problem Statement

The portfolio owner wants to demonstrate that they can evaluate a retrieval-augmented generation (RAG) system, not merely assemble a document chatbot. They need a small, understandable project that shows how chunk size, top-k retrieval, and reranking affect retrieval quality, unsupported answers, latency, and cost. The project must be credible to AI-engineering hiring managers, understandable to analysts, safe to demonstrate with synthetic data, and free for public visitors to use.

## Solution

Build a RAG Evaluation Lab over a small synthetic employee-policy corpus. A repeatable local benchmark will run the same 30 questions through five controlled RAG configurations. One setting changes at a time so the effect of chunk size, top-k, or reranking remains interpretable.

The benchmark will save question-level evidence and summary metrics. A read-only Streamlit dashboard will load those saved results, let visitors compare configurations, and show why individual questions succeeded or failed. The public app will make no paid model calls. A recruiter can therefore inspect the experiment at no cost, while a developer can rerun it locally with their own model key.

## User Stories

1. As a portfolio visitor, I want a plain-English project overview, so that I understand the problem without prior RAG expertise.
2. As a hiring manager, I want to see a controlled experiment, so that I can trust that the comparisons are meaningful.
3. As a hiring manager, I want to see the baseline configuration, so that every variation has a clear reference point.
4. As a portfolio visitor, I want to compare smaller and larger chunks with other settings held constant, so that I can understand the chunk-size trade-off.
5. As a portfolio visitor, I want to compare top-3 and top-5 retrieval with other settings held constant, so that I can understand the top-k trade-off.
6. As a portfolio visitor, I want to compare retrieval with and without reranking, so that I can see whether the extra step improves results.
7. As a portfolio visitor, I want a concise metrics table for every configuration, so that I can compare results quickly.
8. As a portfolio visitor, I want charts for retrieval hit rate, unsupported-answer rate, latency, and estimated cost, so that important differences are visible.
9. As a portfolio visitor, I want short plain-English findings beside the charts, so that I do not have to infer every conclusion myself.
10. As a technical reviewer, I want to inspect the question-level results behind each aggregate metric, so that I can verify the claims.
11. As a technical reviewer, I want to see the retrieved text and its source section, so that I can diagnose retrieval failures.
12. As a technical reviewer, I want to see the generated answer and its citations, so that I can judge whether the answer is grounded in the evidence.
13. As a technical reviewer, I want answerable and deliberately unanswerable questions in the benchmark, so that the system's willingness to invent answers is tested.
14. As a technical reviewer, I want every question to identify its expected source section, so that retrieval success has an objective definition.
15. As a technical reviewer, I want every answer review to be visible, so that the unsupported-answer metric is auditable.
16. As the portfolio owner, I want synthetic policy documents, so that I avoid confidential data and can control the ground truth.
17. As the portfolio owner, I want stable section identifiers in the documents, so that expected evidence remains comparable across chunk sizes.
18. As the portfolio owner, I want one command to run the benchmark, so that results can be reproduced without operating the dashboard.
19. As the portfolio owner, I want benchmark results saved as ordinary data files, so that the public dashboard does not need a database or model credentials.
20. As the portfolio owner, I want model and pricing metadata saved with each benchmark run, so that cost estimates remain explainable when prices change later.
21. As the portfolio owner, I want retrieval, reranking, and generation latency measured separately, so that the slow step is identifiable.
22. As the portfolio owner, I want token counts retained, so that cost calculations can be checked independently.
23. As the portfolio owner, I want the benchmark to continue recording completed questions if a later model call fails, so that a temporary failure does not discard paid work.
24. As the portfolio owner, I want an obvious warning before a benchmark makes paid calls, so that I do not spend money accidentally.
25. As the portfolio owner, I want the dashboard to work without an API key, so that hosting it cannot create an open-ended bill.
26. As the portfolio owner, I want setup and reproduction instructions in the README, so that reviewers can run the project locally.
27. As the portfolio owner, I want the README to explain experimental limitations, so that the project presents honest evidence rather than overstated claims.
28. As an analyst, I want the exported question-level and summary results in tabular form, so that I can inspect them with familiar analysis tools.
29. As a keyboard user, I want all dashboard controls and result views to remain usable without a mouse, so that the public demo meets basic accessibility expectations.
30. As a portfolio visitor, I want a useful empty/error message if saved results are unavailable, so that a deployment problem is understandable rather than appearing as a broken screen.

## Implementation Decisions

- Use Python and Streamlit. Python supports the local NLP models, while Streamlit provides a small dashboard without building a separate frontend and backend.
- Keep one public testing seam: the evaluation runner accepts a benchmark and one RAG configuration, then returns a structured evaluation result. Tests and local benchmark execution use the same interface.
- Treat the evaluation runner as the deep module. It owns chunking, embedding, retrieval, optional reranking, answer generation, metric inputs, timing, and result assembly. Callers do not coordinate those steps themselves.
- Keep the Streamlit module thin. It reads saved evaluation results, filters them, and renders tables, charts, evidence, and explanatory text. It does not run models.
- Use four to six fictional employee-policy documents with stable document and section identifiers. Suggested subjects are paid time off, remote work, expenses, benefits, and payroll.
- Use 30 predefined benchmark questions. Include direct-answer questions, questions whose wording differs from the source, questions requiring distinction between similar policies, and at least six questions that the documents cannot answer.
- Give each benchmark question an identifier, text, answerability label, expected source section, reference answer or expected abstention, and short reviewer note.
- Compare exactly five configurations in version one: a 700-token/top-3/no-reranking baseline; 300-token and 1,200-token chunk variants; a top-5 variant; and a reranking-on variant. Each variant changes one baseline setting.
- Keep chunk overlap fixed for every configuration. It is recorded as experiment metadata but is not another variable in version one.
- Fix one local embedding model, one local cross-encoder reranker, and one answer model for the complete benchmark. Model comparison is excluded because it would obscure the three selected variables.
- Use direct Python plus the installed numerical operations supplied with the embedding stack for similarity search. A vector database is unnecessary for this small fixed corpus and would add setup without improving the experiment.
- When reranking is enabled, retrieve a fixed larger candidate pool, reorder it with the cross-encoder, and then retain the configured top-k results. Record both the initial and final rankings for inspection.
- Preserve document identifier, section identifier, and character offsets on every chunk. Retrieval is a hit when at least one returned chunk contains the question's expected section identifier.
- Generate answers only from the retrieved text and require source-section citations. For unanswerable questions, the desired behavior is an explicit statement that the supplied documents do not contain the answer.
- Define an unsupported answer as an answer that states a material fact not supported by its cited retrieved text, or answers an unanswerable question instead of abstaining. Define hallucination rate as unsupported answers divided by all generated answers.
- Use manual review labels for unsupported answers in version one. Thirty questions across five configurations produces 150 reviews: small enough to audit and more honest than presenting a weak automatic judge as ground truth.
- Store the review label, optional reviewer note, cited sections, and retrieved evidence beside each generated answer so every hallucination classification can be inspected.
- Report retrieval hit rate, unsupported-answer rate, correct-abstention rate, average retrieval latency, average reranking latency, average generation latency, average total latency, token usage, and estimated generation cost per configuration.
- Measure latency using a monotonic clock around each stage. Saved latency describes the recorded benchmark environment; the dashboard must not imply it is current hosting latency.
- Calculate cost from recorded input/output token counts and a dated per-token price snapshot supplied in benchmark configuration. Keep counts and rates visible so estimates remain auditable.
- Save question-level results and configuration summaries as simple JSON and/or CSV artifacts. No database is required.
- Save each completed question result immediately or checkpoint frequently enough that a failed remote call can resume without repeating completed paid calls.
- Require an explicit local flag to permit model calls. Without it, benchmark execution must not contact a paid model.
- Ship precomputed benchmark artifacts with the project. The public deployment reads only these artifacts and requires no secrets.
- Present the dashboard in three views: an overview with conclusions, a configuration comparison, and a question/evidence explorer. More pages are unnecessary for version one.
- Include a short methodology and limitations section. It must state that results apply to this synthetic corpus, question set, and selected models rather than to every RAG system.
- Use accessible Streamlit labels, visible focus behavior supplied by native controls, readable contrast, and text summaries for charts.
- Keep framework use minimal. Do not introduce LangChain, LlamaIndex, a vector database, a hosted backend, or a custom frontend for version one.

## Testing Decisions

- A good automated test exercises externally visible behavior through the evaluation runner interface. It should remain valid if chunking, retrieval, or result assembly is internally reorganized.
- Test the evaluation runner with a tiny deterministic benchmark containing two short documents and both answerable and unanswerable questions.
- Supply deterministic test adapters for external model behavior so automated tests require no network, downloaded model, API key, or paid call. These adapters are internal test support, not additional public interfaces.
- Verify that changing chunk size changes produced chunks while preserving their source-section metadata.
- Verify that top-k limits the returned evidence and that retrieval hit rate is calculated from expected section identifiers.
- Verify that enabling reranking can change result order while still returning the configured number of results.
- Verify that supported, unsupported, and correct-abstention labels aggregate into the documented rates.
- Verify that token counts, non-negative stage timings, pricing metadata, and estimated cost appear in the structured result.
- Verify that a failure on one question preserves earlier completed results and can be resumed without regenerating them.
- Verify that paid model calls are refused unless explicitly enabled.
- Do not test private helper functions or exact similarity scores. Those checks would couple tests to implementation details instead of project behavior.
- There is no existing test prior art in the repository. Add one small automated test module centered on the evaluation runner seam and use manual browser checks for the thin Streamlit presentation.
- Manually verify the public dashboard at desktop and narrow widths, keyboard navigation, chart text summaries, missing-results behavior, and absence of required secrets.

## Out of Scope

- Arbitrary document uploads or chat-with-your-own-document behavior
- A general-purpose production RAG platform
- Public or multi-user live model calls
- Authentication, user accounts, or saved visitor sessions
- A hosted database, vector database, or separate backend
- Multiple embedding models, rerankers, or answer models
- Full-grid hyperparameter search or automatic optimization
- Automatic LLM-as-judge scoring
- Streaming answers or conversational memory
- Production monitoring, distributed execution, or large-corpus performance
- Custom frontend development
- A separate portfolio website

## Further Notes

- The intended portfolio message is: “I built an evaluation harness to understand why RAG answers fail.”
- Default assumptions replace the unfinished interview: the primary audience is AI-engineering hiring managers; the dataset is synthetic; the public operating budget is zero; development model spend should remain at or below $5; and the first publishable version should fit roughly two weekends.
- The baseline and four one-variable variants are deliberately smaller than a full parameter grid. A full grid can be added only if the initial findings show interactions worth investigating.
- The public demo should lead with findings, not controls. A visitor should understand the strongest result within three minutes.
- After this spec, use `to-tickets` to split the work into small, blocking-aware implementation tickets.
