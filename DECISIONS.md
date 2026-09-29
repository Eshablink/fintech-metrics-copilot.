# Decisions

Use Eshablink/fintech-metrics-copilot. (trailing dot) and feat/fintech-copilot from main — GitHub inspection found this repository and the user approved using it.
Create SPEC.md, TASKS.md, DECISIONS.md and CLAUDE.md first, each with commit message docs: initialize copilot build plan — preserve the brief and continuation state before code.
Use fictional XYZ Finance and conspicuous SIMULATED labels — avoid representing synthetic lending data as customer or production evidence.
Use Python with Pandas, typed interfaces and pytest — match the requested stack and keep business logic testable.
Store seed, fixed as-of date, timezone, data paths, documents and business settings in config — reproducibility and business substitution must not require application rewrites.
Store currency as integer minor units and separate loan, weekly exposure, payment and reminder grains — prevent floating-point money errors and join-driven denominator inflation.
Use DuckDB with dbt-duckdb staging/marts — make the small demo portable while proving modeled and tested analytics.
Define metric expressions and semantics in one YAML registry — SQL generation, dashboards and definitions must not drift.
Validate and execute SQL in a read-only, external-access-disabled bounded worker — model prompts alone are not a security boundary.
Use a replaceable Gemini/Groq provider adapter with paid fallback disabled — support free-tier demonstration without provider lock-in or unauthorized spending.
Use page-preserving PDF extraction and Qdrant retrieval — required citations must resolve to actual configured files and pages.
Do not fabricate missing RBI/Fair Practices PDFs or infer their rules — document answers must be supported by supplied or verifiably ingested sources.
Use the exact missing-document refusal from SPEC.md — unsupported policy answers must be predictable and testable.
Start retrieval simple, then add hybrid fusion, reranking and metadata filters — measure each improvement against a fixed development set before held-out evaluation.
Use Streamlit for the three-tab recruiter demo and FastAPI for the guarded shared service — balance quick delivery with reusable backend interfaces.
Use prespecified randomized reminder assignment and intention-to-treat analysis — simulated experimental conclusions need coherent units, windows and complaint guardrails.
Keep evaluation sets and run artifacts versioned with per-case evidence — README results, ablations and failures must be auditable, never invented.
Treat refusal evidence as an explicit absence report, not a fabricated citation — missing material cannot support a positive claim.
Introduce only minimal validation CI early if required to execute tests; retain full Docker/CI hardening for task 24 — task completion requires real checks before the final phase.
Require owner deployment authorization and ask before paid infrastructure — no live demo URL exists until deployment and public smoke testing succeed.
Honor exact-path/branch/commit confirmation requirements of the GitHub connector — autonomous work does not override tool write safeguards.
Leave tasks unchecked until acceptance tests run successfully — committed source is not proof that code works.
Use `CREATE OR REPLACE` table loads inside an explicit DuckDB transaction for raw sources — idempotent reruns and rollback safety satisfy task-2 reproducibility checks.
Use DuckDB read-only connection tests as warehouse write guards — task-2 requires proof that reporting sessions cannot mutate loaded tables.
Create BLOCKERS.md and PROGRESS.md early — continuous autonomous execution needs persistent blocker and status tracking.
