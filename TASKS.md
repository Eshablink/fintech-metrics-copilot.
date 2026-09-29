# Build checklist

Read SPEC.md first. Work on the first unchecked task. A checkbox means its done-when test actually passed, not merely that files exist. Save run evidence and commit after each completed task. No build tasks have passed yet.

## Thin demo: tasks 1–8
| Status | Task | Done when... |
| --- | --- | --- |
| [ ] | 1. Scaffold typed Python package, config, fixed-seed synthetic loan/cohort/payment/reminder data, .env.example and generator tests. | Two runs with identical config yield identical output hashes; pytest validates schema, IDs, foreign keys, monetary bounds and SIMULATED provenance, and lint/type checks pass. |
| [ ] | 2. Load synthetic data idempotently into DuckDB. | Repeated loads preserve counts; SQL reconciles source amounts and foreign keys, and rollback/read-only tests pass. |
| [ ] | 3. Build dbt-duckdb staging and collection marts. | dbt build passes unique, not-null, relationship, bucket-boundary and reconciliation tests without payment fan-out. |
| [ ] | 4. Define metric semantics once in YAML and implement metric/date resolution. | Tested recovery-rate numerator, denominator, zero-denominator behavior, DPD edges and last-week dates agree with independent fixture calculations. |
| [ ] | 5. Add swappable Gemini/Groq wrapper and guarded text-to-SQL. | Supported fixture questions execute correctly and show SQL; unsafe SQL, external reads, timeouts and malformed responses are rejected by tests. |
| [ ] | 6. Implement PDF ingestion, basic Qdrant RAG and SQL/RAG/mixed router. | Configured PDF claims resolve to real file/page evidence; unsupported questions return the exact refusal and routing fixtures pass. |
| [ ] | 7. Build the Streamlit interface and clickable examples. | Ask the Copilot, Dashboard and Experiment & Evaluation tabs run; simulated-data banner and evidence are visible; missing credentials/documents fail safely. |
| [ ] | 8. Deploy the thin demo publicly with baseline limits. | An actual unauthenticated smoke test at the recorded live URL passes examples, evidence display, banner and graceful missing-source handling without paid fallback. |

## Depth: tasks 9–16
| Status | Task | Done when... |
| --- | --- | --- |
| [ ] | 9. Specify and generate randomized morning/evening reminder experiment. | Config records unit, allocation, outcomes, window, minimum detectable effect assumptions and guardrail; no borrower crosses arms and randomization checks pass. |
| [ ] | 10. Estimate reminder uplift and significance. | Tested intention-to-treat estimates, confidence intervals and significance reproduce saved seeded-run results with defined denominators and no causal claims about real customers. |
| [ ] | 11. Analyze segments and complaints guardrail. | Saved analysis covers prespecified segments, multiplicity/exploratory caveats and guardrail uncertainty, including sparse and empty strata tests. |
| [ ] | 12. Publish experiment business memo and UI. | Memo and experiment tab reproduce actual outputs, limitations, complaint trade-offs and an evidence-backed simulated recommendation. |
| [ ] | 13. Add hybrid sparse/dense retrieval. | Fusion tests pass and a saved development-set comparison measures basic versus hybrid retrieval using identical corpus versions. |
| [ ] | 14. Add reranking. | Reranking is configurable, deterministic where applicable, bounded by timeout and evaluated against the same development set with latency recorded. |
| [ ] | 15. Add document metadata filters and version-aware citations. | File/type/version/page filters isolate intended documents; filename, page and checksum survive indexing, reranking and response generation. |
| [ ] | 16. Deliver reproducible EDA notebook and refresh deployment. | Notebook executes from clean generated data with reconciled plots and missingness/outlier/leakage discussion; tasks 9–15 are deployed and smoke-tested. |

## Proof: tasks 17–25
| Status | Task | Done when... |
| --- | --- | --- |
| [ ] | 17. Author versioned evaluation set with at least 100 questions. | A validator confirms SQL, RAG, mixed and unanswerable coverage, reference SQL/results or file/page labels, unique IDs and separated development/held-out cases. |
| [ ] | 18. Build quantitative SQL and routing evaluation. | Saved real runs report execution/result accuracy and routing accuracy with per-case outcomes, failure denominators and reproducible run metadata. |
| [ ] | 19. Evaluate retrieval, grounding and refusals. | Real runs report recall@k, faithfulness under a stated rubric and correct-refusal rates with citation checks, sample counts and grader limitations. |
| [ ] | 20. Instrument and evaluate latency and cost. | Real runs save end-to-end and stage timings, token usage and provider-priced or explicitly unavailable cost; budget accounting passes concurrency tests. |
| [ ] | 21. Run controlled ablations. | Saved tables compare basic/hybrid/reranked retrieval and routing alternatives on identical held-out inputs with quality, latency and cost, never invented values. |
| [ ] | 22. Write failure analysis. | Every documented failure links to an actual run/case with cause, impact, attempted fix or remaining limitation, and regression coverage where fixed. |
| [ ] | 23. Expose FastAPI with limits, spending cap and cached examples. | API contract, input validation, shared limits, concurrency, fail-closed cap, cache provenance and secret-redaction tests pass; public clients cannot bypass enforcement. |
| [ ] | 24. Add production CI and Docker deployment. | GitHub Actions passes lint, typing, pytest, dbt and smoke checks; a clean Docker build starts the documented services and reproduces fixture results. |
| [ ] | 25. Finish recruiter README and verified public release. | README has SIMULATED disclaimer, actual screenshot/live button, architecture diagram, run-backed results and business-swap guide; all tasks pass and final public smoke test succeeds. |

## Execution notes
Step 0 is a documentation initialization, not completion of task 1. Basic validation automation may be introduced with task 1 so tests can run before the full task-24 deployment pipeline. No shell, deployment session or successful CI run has been established in this chat. Do not infer test success from a successful Git commit.

Task 1 is next: use a configurable fixed seed and as-of date, integer minor units, borrower/loan IDs, weekly cohort exposures, payments and reminder events; avoid PII and keep source records separate from derived dbt metrics. Task-1 writes beyond Step 0 require connector approval of exact paths and commit messages. Mark tasks only after run evidence exists.
