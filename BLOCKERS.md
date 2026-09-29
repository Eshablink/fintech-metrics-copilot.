# Blockers

| ID | Task | Blocker | Why it blocks | Fallback used | Exact user steps to unblock | Status |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | Task 7 | Official RBI PDFs not downloaded yet in this environment | External web fetch is not available through current repo tooling | Continue with `docs/metrics_definitions.md` as RAG fallback corpus | Upload RBI Digital Lending Guidelines and Fair Practices Code PDFs into `docs/source_pdfs/` on this branch | Open |
| B-002 | Task 25 | Hosting account login not available via GitHub connector | Deployment to Streamlit/HF requires interactive login | Prepare deploy-ready repo artifacts and exact click-path instructions | Complete the documented hosting steps in this file once provided | Open |
