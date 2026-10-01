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

| 6.7 | Phase 6 | complete | 2026-10-01 | Successful GitHub Actions run completed counterfactual Bull/Bear repricing for all 150 expiries and the full GBM/Student-t/HMM/logistic/boosted/hybrid walk-forward ladder. Robustness report shows no model passes the economic promotion gate. |

| 6.1-6.6 | Phase 6 | complete | 2026-10-01 | Executed counterfactual Bull/Bear pricing, Student-t MC, 2-state HMM regime probability, logistic regression, boosted-tree, hybrid ensemble, fixed abstention rule, and expanding walk-forward evaluation. Full results are in research_artifacts/phase6/. |


| 7.1 | Phase 7 | complete | 2026-10-01 | Frozen a new-information-set restart protocol. Closed the Phase 1–6 sample at 2026-05-19; defined a fresh boundary at 2026-05-20, a minimum 26-week fresh OOS requirement, locked feature groups, timestamp lineage, cost/slippage controls, and preregistered promotion gates. No fresh performance selection was performed. |

## Phase 7 source audit

- NSE provides historical India VIX data and describes India VIX as an option-implied near-term volatility measure.
- NSE option-chain data exposes IV, bid/ask, volume and open interest fields.
- NSE publishes FII/FPI and DII activity reports.
- NSE provides historical index data, market-report archives and corporate-action/filing data.
- RBI documents its reference-rate archive for USD/INR.

These sources support the feasibility of the locked information set; source availability does not imply that every historical field will be available with a verifiable publication timestamp.


| 7.2 | Phase 7 | in progress | 2026-10-01 | Restarted data acquisition using a new information set. Global cross-market series (S&P 500, Nasdaq, Cboe VIX, USDINR, Brent, gold) were acquired for the full development history plus the fresh boundary. A non-evaluative artifact reports 97 fresh daily rows and explicitly records that performance evaluation/model selection were not run. NSE India VIX and signal-date NIFTY option EOD acquisition were then added using the NSE historical-data interfaces/packages. |

## Phase 7 literature/source additions

- NSE documents India VIX as a near-term volatility measure calculated from NIFTY option bid-ask information and provides historical search access.
- NSE's historical-report system exposes advances/declines, historical India VIX, contract-wise F&O data and corporate-action/report archives.
- NSE's option-chain interface exposes IV, volume, open interest and option-contract fields.
- Recent NIFTY research specifically motivates option-implied ATM/skew/term-structure variables: Patra (2025) reports predictive information in ATM and skew-based OTM features; Potharla & Sen (2026) study volatility-smile asymmetry, maturity and volatility-regime interactions; Sajjan (2026) studies India VIX/weekly VRP and regime dependence.

| 7.2 | Phase 7 | complete-with-limitations | 2026-10-01 | End-to-end non-evaluative data pipeline completed. HF option subset acquired at immutable dataset revision; option surface produced 155 signal-date rows with explicit missing-date/tenor errors; India VIX produced 350 rows; FII/DII archive produced 62 source dates; breadth/corporate-action public acquisition produced no usable rows and remains excluded rather than imputed. No performance evaluation or model selection ran. |
| 7.3 | Phase 7 | complete | 2026-10-01 | Frozen P7.3-v1 model/analysis specification: regularized logistic primary model, fixed 0.55/0.45 thresholds, fixed diagnostic models, training-window preprocessing, walk-forward rules, cost/slippage sensitivities, and all economic promotion gates. Fresh outcomes remain unopened. |

| 7.3a | Phase 7 | control-file audit/fix | 2026-10-01 | Reconciled the stale data-layer status artifact to complete-with-source-coverage-limitations and restored the missing P7.3-v1 model-spec artifact referenced by README. No research data, fresh outcomes, model parameters, thresholds or promotion criteria were changed. |
