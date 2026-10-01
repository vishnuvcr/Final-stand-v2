# Final-stand-v2 — NIFTY weekly-option research

## Current status

Research initialized. Phase 1 (data and specification) is in progress.

A main-branch Actions runner now executes phase branches on pull requests and manual runs.

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
- Phase 1: in progress
- Phase 2: pending
- Phase 3: pending
- Phase 4: pending
- Phase 5: pending

## Important data sources
- NSE derivatives reports/archive: https://www.nseindia.com/all-reports-derivatives
- Hugging Face NIFTY options dataset: https://huggingface.co/datasets/thetrademarkk/india-index-options-1m
- Hugging Face NIFTY options/other research dataset: https://huggingface.co/datasets/rissin/nse-options-intraday
- NIFTY spot intraday reference: https://github.com/technovusin/nifty50-historical-data

## Reproducibility
The backtest code and manifests will be committed. Large third-party raw datasets will be referenced by immutable file paths/checksums rather than copied wholesale into Git history.


## Research completion status
The complete research package is on [phase-5-manuscript](https://github.com/vishnuvcr/Final-stand-v2/tree/phase-5-manuscript) and is proposed for merge in [PR #3](https://github.com/vishnuvcr/Final-stand-v2/pull/3).

Primary test result:
- 150 available weekly observations, 150 executable trades (2022-06-09 through 2026-05-19).
- Primary normalized net P&L: ₹198,598.87.
- Win rate: 89.33%.
- Profit factor: 2.13.
- Maximum drawdown: -₹35,661.65.
- Monte Carlo directional hit rate: 50.67%.
- Monte Carlo AUC: 0.5186.
- Alternative 63/504-session Monte Carlo-window sensitivity remains explicitly open and is not used in the conclusion.

The final manuscript and complete research package are maintained on the phase-5 branch until PR #3 conflicts with the current main-branch history are reconciled.


## Next proposed research phase
**Phase 6 — Direction Engine v2 (not yet executed):** improve the signal using conditional heavy-tailed/regime-aware Monte Carlo, HMM/HSMM regime detection, and shallow supervised models with strict walk-forward validation. The optimization target is the downstream option strategy's loss-tail/drawdown and net P&L, not direction accuracy in isolation.
