# Final-stand-v2 — NIFTY weekly-option research

## Current status

Research initialized. Phase 1 (data and specification) is complete; Phase 2 (Monte Carlo signal) is next.

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

See [RESEARCH_PLAN.md](RESEARCH_PLAN.md), [RESEARCH_LOG.md](RESEARCH_LOG.md), and [ERROR_LOG.md](ERROR_LOG.md).

## Status
- Repository bootstrap: complete
- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete (core statistics; alternative MC-window sensitivity remains pending)
- Phase 5: complete

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


## Phase 6 status — partial / execution blocked
Phase 6 Direction Engine v2 has been implemented and partially evaluated from committed artifacts. A heavy-tail conditional-MC proxy did not improve directional hit rate (50.00% versus 50.67% for the existing GBM). An agreement/confidence filter did not robustly reduce the observed drawdown. The full HMM + supervised ML + hybrid + counterfactual Bull/Bear option-pricing ladder is **not claimed complete** because the available GitHub connector did not expose a workflow dispatch/run operation and did not return an executable Actions result. See [PHASE6_PLAN.md](PHASE6_PLAN.md), [Phase 6 partial results](research_artifacts/phase6/summary.md), [Phase 6 JSON results](research_artifacts/phase6/partial_results.json), and [ERROR_LOG.md](ERROR_LOG.md).
