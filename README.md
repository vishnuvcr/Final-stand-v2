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
- Phase 2: in progress
- Phase 3: in progress
- Phase 4: in progress
- Phase 5: pending

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
