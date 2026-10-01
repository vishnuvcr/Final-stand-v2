# Research Plan

## Research questions
1. Does a Monte Carlo forecast generated from information available after the prior weekly expiry predict the sign of NIFTY's move into the next weekly expiry better than chance?
2. Conditional on that signal, does the specified 1:-1:-1 OTM4/OTM5/OTM6 option structure produce positive risk-adjusted returns?
3. How sensitive are results to the Monte Carlo calibration window/model, option strike mapping, transaction costs, slippage, and expiry-day regime changes?
4. Do results survive out-of-sample testing and statistical controls for repeated weekly observations?

## Primary specification
- Universe: NIFTY index weekly options.
- Signal timestamp: prior weekly expiry-day market close; use the last observed NIFTY spot close of that trading day.
- Forecast horizon: upcoming weekly expiry.
- Baseline Monte Carlo: geometric Brownian motion using information available only through the signal close; primary directional rule is median simulated terminal price > signal spot => Bull, else Bear.
- Primary calibration window: rolling 252 trading sessions, with sensitivity to 63 and 504 sessions.
- Simulations: 50,000 paths per signal, fixed random seed for reproducibility.
- Entry timestamp: 10:00 IST on the trading day corresponding to 4 trading days before expiry.
- Strike mapping: primary interpretation of OTM4/OTM5/OTM6 = 4th/5th/6th strike-grid positions OTM from the ATM strike determined from NIFTY spot at entry (10:00 IST); sensitivity will use the signal-day spot. A trade is valid only if all three exact strikes are present.
- Position: 1 long OTM4 and 1 short OTM5 and 1 short OTM6 of the relevant option type.
- Primary exit: expiry intrinsic value from NIFTY expiry close; diagnostic exit: last option print by 15:30 when no more than 30 minutes stale, otherwise intrinsic fallback. Report both. This treats expiry settlement and an actionable expiry-day close separately.
- Costs: baseline current Paytm Money ₹20 per executed F&O order; 6 orders per 3-leg round trip when legs are executed separately; NSE equity-option transaction charge ₹3,553/crore premium each side from 1-Mar-2026; STT on option sales 0.15% of premium from 1-Apr-2026; 18% GST on broker/exchange service charges; one-tick ₹0.05 adverse slippage per option execution as the minimum liquidity proxy. Run zero-cost and 2-tick sensitivity controls. Historical STT/lot-size changes are handled by effective-date tables where applicable.

## Phase 2 implementation note
The primary OTM definition is based on the 10:00 IST entry spot because moneyness is a property of the option position at entry. The Monte Carlo signal uses only information through the prior expiry close.

## Phase 4 analysis specification
Primary statistical outputs: bootstrap 95% CI for mean P&L, two-sided binomial test for win rate, one-sample t-test for mean P&L, lag-1 P&L autocorrelation, 70/30 chronological split, Thursday-vs-Tuesday expiry-regime split, Monte Carlo calibration-window sensitivity (63/252/504 sessions), Brier score and AUC, cost/exit sensitivity, and annual P&L tables/charts. These are robustness diagnostics, not parameter selection.

## Phase gates
### Phase 1 — Data and specification
Tasks: verify expiry calendars, collect/cache required data manifests, validate timestamps, define strike mapping and cost model, create test fixtures.
Exit criterion: reproducible dataset manifest and a data-quality report.

### Phase 2 — Monte Carlo signal
Tasks: implement leakage-safe calibration, simulate paths, generate weekly Bull/Bear signals, measure directional hit rate and calibration.
Exit criterion: signal table and tests pass.

### Phase 3 — Backtest
Tasks: locate entry/exit option prices, calculate leg-level P&L, aggregate net P&L/equity curve, apply transaction costs/slippage, record failed/missing trades.
Exit criterion: complete trade ledger and performance report.

### Phase 4 — Statistical analysis + robustness
Tasks: CAGR/Sharpe/Sortino/drawdown/profit factor/win rate, bootstrap confidence intervals, regime splits, model/parameter sensitivity, out-of-sample split, comparison to always-bull/always-bear and signal-only baselines.
Exit criterion: robustness report with no hidden parameter tuning on the test set.

### Phase 5 — Manuscript
Tasks: figures, tables, methods, results, discussion, strengths/limitations, conclusion, future work, appendix, reproducibility notes.
Exit criterion: complete structured manuscript and final research status.

## Final phase status
Phase 5 is complete. Phase 4 core statistics are complete; the 63/504-session Monte Carlo calibration-window sensitivity remains explicitly open as a reproducibility extension and is not used in the primary conclusion.

## Non-negotiable research controls
- No look-ahead: signal uses only data available at prior expiry-day close; entry uses only data at 10:00 or earlier; exit uses only expiry information.
- Preserve raw/source manifests and checksums.
- Log every error and correction.
- Update README and phase status after each completed step.
- Separate each phase into its own Git branch.


## Phase 7 — New-information-set restart

Phase 7 is a separate branch and a hard anti-overfitting gate. The Phase 1–6 development sample is closed at 2026-05-19. A future restart must introduce a new information set and use a fresh untouched period beginning 2026-05-20.

Required new information groups: option-implied skew/IV term structure, India VIX, FII/FPI and DII flows, breadth, global cross-market variables, USDINR, crude, gold, regime/volatility state, and timestamped news/corporate-action events.

A minimum of 26 eligible fresh weekly observations is required before promotion. Promotion gates are preregistered in PHASE7_PLAN.md and are based on costed downstream option P&L and risk, not directional accuracy alone.

See [PHASE7_PLAN.md](PHASE7_PLAN.md) and [RESTART_PROTOCOL.md](RESTART_PROTOCOL.md).
