# Research Log

| Step | Phase | Status | Date | Notes |
|---|---|---|---|---|
| 0.1 | Bootstrap | complete | 2026-10-01 | Repository was empty; initialized research control files. |
| 1.1 | Phase 1 | complete | 2026-10-01 | User strategy specification captured. Public data-source scan started; primary public NIFTY 1-min option dataset identified. |
| 1.2 | Phase 1 | complete | 2026-10-01 | PR-triggered smoke test succeeded on GitHub Actions. Dataset schema, timestamp timezone, option fields, and spot source were validated. |
| 2.1 | Phase 2 | started | 2026-10-01 | Implemented cached Hugging Face data access and 50,000-path GBM Monte Carlo signal generation with 252-session calibration. |
| 2.2 | Phase 2 | complete | 2026-10-01 | First Actions execution stopped on a syntax error before data download. Fixed report generation; successful run produced 150 signals. |
| 3.1 | Phase 3 | started | 2026-10-01 | Implemented 3-leg OTM strategy backtest, 10:00 entry quote rule, expiry intrinsic settlement, market-exit diagnostic, Paytm/exchange cost model, 1/2-tick and zero-cost sensitivities. |
| 3.2 | Phase 3 | complete | 2026-10-01 | Optimized option data access to filtered Parquet reads; backtest completed with 150/150 valid trades and committed ledger. |
| 4.1 | Phase 4 | error/fix | 2026-10-01 | First statistics run failed on an invalid SciPy AUC import; fixed with a NumPy-only AUC implementation and logged E0006. |
| 4.2 | Phase 4 | error/fix | 2026-10-01 | Second statistics run failed because the workflow did not install huggingface_hub required by data_access. Added the dependency and logged E0007. |
| 4.3 | Phase 4 | error/fix | 2026-10-01 | Third statistics run lacked the NIFTY index file in cache. Added index-only cache hydration and logged E0008. |
| 4.4 | Phase 4 | error/fix | 2026-10-01 | Fourth statistics run produced an empty MC-window sensitivity table because signal timestamps were not normalized to date keys. Fixed and logged E0009. |
| 4.5 | Phase 4 | complete | 2026-10-01 | Independently verified core statistics from committed phase-2/phase-3 artifacts: bootstrap mean CI ₹347–₹2,172, 89.33% trade win rate, PF 2.13, chronological and expiry-regime stability, cost/exit sensitivities. Alternative MC-window sensitivity remains unfinalized. |
| 5.1 | Phase 5 | complete | 2026-10-01 | Final structured manuscript, charts, derived tables, artifact manifest, and manual validation workflow committed. |

## Conversation record
### 2026-10-01 — User request
Test a NIFTY weekly options strategy where a Monte Carlo forecast is generated after the previous expiry close, then a directional three-leg OTM4/OTM5/OTM6 structure is entered at 4 DTE 10:00 and exited at expiry.

| 6.1 | Phase 6 | partial | 2026-10-01 | Added executable direction-engine workflow, conditional heavy-tail MC artifact analysis, and agreement-filter sensitivity. Full Actions execution was blocked by connector limitations; no counterfactual P&L was invented. See research_artifacts/phase6/partial_results.json. |
| 6.2-6.4 | Phase 6 | blocked | 2026-10-01 | HMM/supervised/hybrid ladder and true Bull-vs-Bear counterfactual option repricing require a runnable Actions execution path; implementation is present but was not claimed as executed. |
| 6.5-6.6 | Phase 6 | pending | 2026-10-01 | Manuscript/README should report Phase 6 as partial until the counterfactual runner executes successfully. |
| 6.1-6.6 | Phase 6 | complete | 2026-10-01 | Executed counterfactual Bull/Bear pricing, Student-t MC, 2-state HMM regime probability, logistic regression, boosted-tree, hybrid ensemble, fixed abstention rule, and expanding walk-forward evaluation. Full results are in research_artifacts/phase6/. |
