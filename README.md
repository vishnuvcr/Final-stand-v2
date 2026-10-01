# Final-stand-v2 — NIFTY weekly-option research

## Current status

Phases 1–6 are complete and closed. Phase 7 has frozen a new-information-set restart protocol; no additional tuning is permitted on the Phase 1–6 sample.

## Research objective
Test the user-specified weekly NIFTY direction strategy:
- Signal: prior weekly expiry-day after-market NIFTY spot close.
- Forecast: Monte Carlo for the upcoming weekly expiry.
- Bull: long 4th-OTM put, short 5th-OTM put, short 6th-OTM put.
- Bear: long 4th-OTM call, short 5th-OTM call, short 6th-OTM call.
- Entry: 4 DTE at 10:00 IST.
- Exit: expiry.

## Research phases
1. Data + specification
2. Monte Carlo signal model
3. Strategy backtest + execution costs
4. Statistical analysis + robustness
5. Manuscript + appendices
6. Direction engine extension
7. New-information-set restart protocol

See [RESEARCH_PLAN.md](RESEARCH_PLAN.md), [RESEARCH_LOG.md](RESEARCH_LOG.md), and [ERROR_LOG.md](ERROR_LOG.md).

## Status
- Repository bootstrap: complete
- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete (core statistics; alternative MC-window sensitivity remains pending)
- Phase 5: complete
- Phase 6: complete; no new directional model promoted
- Phase 7: 7.1 complete; 7.2 complete with documented source-coverage limitations; 7.3 frozen; fresh OOS not yet opened

## Current validated assumptions
- NIFTY weekly expiry: Tuesday; prior-trading-day rollback when Tuesday is a trading holiday.
- NIFTY option tick: ₹0.05 for index options.
- NIFTY lot-size regime: 25 historically, then 75 for new contracts introduced from Nov-2024, then 65 under the 2025 revision cycle.
- Paytm Money: current flat F&O brokerage proxy is ₹20 per executed order for the post-Jan-2025 pricing regime; statutory/exchange charges are additional.
- NSE equity-option transaction charge: ₹3,553 per crore of traded premium value per side from Mar 1, 2026.
- STT on sale of options: 0.15% of option premium from Apr 1, 2026; 0.10% before that in the tested period.

## Important data sources
- NSE derivatives reports/archive: https://www.nseindia.com/all-reports-derivatives
- Hugging Face NIFTY options dataset: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Hugging Face NIFTY options/other research dataset: https://huggingface.co/datasets/rissin/nse-options-intraday
- NIFTY spot intraday reference: https://github.com/technovusin/nifty50-historical-data

## Reproducibility
The backtest code and manifests will be committed. Large third-party raw datasets will be referenced by immutable file paths/checksums rather than copied wholesale into Git history.


## Final result
The primary backtest contains 150 available weekly observations and 150 executable trades from 2022-06-09 through 2026-05-19. Under the primary settlement + current-cost + 1-tick slippage scenario, cumulative normalized net P&L is ₹198,598.87, with 89.33% winning trades and profit factor 2.13. The Monte Carlo directional hit rate is 50.67% and AUC 0.5186, so the historical strategy result should not be interpreted as evidence of strong directional forecasting skill.

## Final research package
- [Final manuscript](FINAL_MANUSCRIPT.md)
- [Research plan](RESEARCH_PLAN.md)
- [Research log](RESEARCH_LOG.md)
- [Error log](ERROR_LOG.md)
- [Data manifest](DATA_MANIFEST.md)
- [Literature review](LITERATURE_REVIEW.md)
- [Cost model](COST_MODEL.md)
- [Monte Carlo signal table](research_artifacts/phase2/signal_table.csv)
- [Trade ledger](research_artifacts/phase3/trade_ledger.csv)
- [Equity curve](research_artifacts/phase4/equity_curve.csv)
- [Annual P&L](research_artifacts/phase4/yearly_pnl.csv)
- [Cumulative P&L chart](research_artifacts/phase4/cumulative_pnl.svg)
- [Annual P&L chart](research_artifacts/phase4/annual_pnl.svg)




## Phase 6 status
Phase 6 Direction Engine v2 has been executed with counterfactual Bull/Bear option pricing and expanding walk-forward validation. See [PHASE6_PLAN.md](PHASE6_PLAN.md), [Phase 6 results](research_artifacts/phase6/summary.md), [predictions](research_artifacts/phase6/walk_forward_predictions.csv), and [counterfactual P&L](research_artifacts/phase6/counterfactual_pnl.csv).


## Phase 6 final status
Phase 6 Direction Engine v2 is complete. The full counterfactual Bull/Bear option-pricing engine and walk-forward GBM, Student-t, HMM, logistic, boosted-tree and hybrid models were executed successfully on GitHub Actions. In the 90-observation out-of-sample window, the original-direction control produced ₹166,402.21 net P&L, 87.78% wins, PF 2.41 and max drawdown -₹27,288.66. No Phase-6 directional model produced a robust drawdown improvement, so no new model is promoted.

See [PHASE6_PLAN.md](PHASE6_PLAN.md), [robustness and promotion](research_artifacts/phase6/ROBUSTNESS_AND_PROMOTION.md), [Phase 6 results](research_artifacts/phase6/summary.md), [counterfactual P&L](research_artifacts/phase6/counterfactual_pnl.csv), and [final manuscript](FINAL_MANUSCRIPT.md).


## Phase 7 — restart gate

Phase 7 explicitly prevents another model-tuning cycle on the same historical sample. The development sample is closed at **2026-05-19**. Any future restart must use a genuinely new information set—option-implied skew/IV term structure, India VIX, FII/FPI and DII flows, breadth, global cross-market signals, USDINR, crude, gold, regime/volatility information, and timestamped news/corporate-action features—and a fresh untouched period.

A final promotion decision requires at least **26 eligible fresh weekly observations** and the preregistered economic gates. Until then, no fresh-period performance is treated as a promotion result.

See [PHASE7_PLAN.md](PHASE7_PLAN.md), [RESTART_PROTOCOL.md](RESTART_PROTOCOL.md), [Phase 7 feature dictionary](research_artifacts/phase7/FEATURE_DICTIONARY.md), and [Phase 7 workflow](.github/workflows/phase7-new-information-set.yml).

### External source hierarchy checked for Phase 7
- NSE India VIX historical data: https://www.nseindia.com/reports-indices-historical-vix
- NSE option chain / IV: https://www.nseindia.com/option-chain
- NSE FII/FPI and DII reports: https://www.nseindia.com/reports/fii-dii
- NSE historical index data: https://www.nseindia.com/reports-indices-historical-index-data
- NSE corporate actions: https://www.nseindia.com/companies-listing/corporate-filings-actions
- NSE historical market reports / breadth: https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives
- RBI USD/INR reference-rate archive: https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx


## Phase 7 data-layer audit
- Option surface: 155 signal-date rows from the locked Hugging Face NIFTY option archive; missing 2W/1M observations are recorded rather than imputed.
- India VIX: 350 daily observations from NSE historical data.
- FII/DII: 62 source dates from the reproducible public archive; no extrapolation beyond available dates.
- Breadth/corporate actions: no parseable rows from the current public acquisition path; excluded from the primary model and retained as a documented limitation.
- Fresh boundary: 2026-05-20; 19 eligible fresh weekly observations are currently available, below the preregistered 26-week minimum. The 26th weekly observation is expected on 2026-11-17 if weekly eligibility remains continuous.
- No fresh-period performance evaluation or model selection has been run.

See [PHASE7_MODEL_SPEC.md](PHASE7_MODEL_SPEC.md) for the frozen P7.3-v1 specification. A 2026-10-01 control-file audit reconciled the status artifact and restored this referenced specification; no research result was changed.
