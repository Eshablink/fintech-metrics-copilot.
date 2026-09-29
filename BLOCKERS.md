# Blockers

| ID | Task | Blocker | Why it blocks | Fallback used | Exact user steps to unblock | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | Task 7 | Official RBI PDFs not downloaded yet in this environment | External web fetch is not available through current repo tooling | Continue with `docs/metrics_definitions.md` as RAG fallback corpus | Upload RBI Digital Lending Guidelines and Fair Practices Code PDFs into `docs/source_pdfs/` on this branch | Open |
| B-002 | Task 25 | Hosting account login not available via GitHub connector | Deployment to Streamlit/HF requires interactive login | Prepare deploy-ready repo artifacts and exact click-path instructions | Complete the documented hosting steps in this file once provided | Open |
| B-003 | Task 24 | Workflow-file writes fail in this connector session | CI workflow cannot be added, so green CI evidence cannot be produced | Continue implementing code and tests locally in repo structure | Reconnect GitHub with workflow write scope, then add `.github/workflows/ci.yml` and rerun checks | Open |
| B-004 | Tasks requiring run evidence | No executable shell/test runner is available in this chat-only toolchain | Cannot run `pytest`, dbt, Docker build, or latency/cost evaluations from this environment | Continue preparing code/tests/config; defer measured outputs | Run the documented commands locally or in CI and commit generated evidence artifacts | Open |
