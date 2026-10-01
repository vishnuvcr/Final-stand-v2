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
- Strike mapping: default interpretation of OTM4/OTM5/OTM6 = 4th/5th/6th listed strike away from the ATM strike on the relevant side, using the signal-day spot to determine ATM; sensitivity will test mapping based on entry-day spot.
- Position: 1 long OTM4 and 1 short OTM5 and 1 short OTM6 of the relevant option type.
- Exit: expiry settlement. For market-price backtest, use the last available option price before market close if exact expiry settlement cannot be reconstructed; report which convention was used.
- Costs: include brokerage/fees/slippage using a documented Paytm Money proxy assumption, and run a zero-cost control.

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

## Non-negotiable research controls
- No look-ahead: signal uses only data available at prior expiry-day close; entry uses only data at 10:00 or earlier; exit uses only expiry information.
- Preserve raw/source manifests and checksums.
- Log every error and correction.
- Update README and phase status after each completed step.
- Separate each phase into its own Git branch.


## Proposed Phase 6 — Direction Engine v2 (not yet executed)

### Objective
Improve the directional filter specifically to reduce large losing weeks and drawdown while preserving the existing option payoff buffer. Directional accuracy alone is not the optimization target; the primary target is improvement in net option-strategy P&L, left-tail loss frequency, maximum drawdown, and conditional win rate under strict out-of-sample testing.

### Phase 6 research ladder
1. **Monte Carlo calibration upgrades**
   - Replace fixed-normal GBM with empirical/bootstrap and Student-t innovations.
   - Test GARCH/EGARCH/GJR-GARCH conditional volatility.
   - Test regime-conditioned drift and volatility.
   - Test jump/tail-mixture distributions.
   - Compare 63/252/504-day calibration windows.
2. **Regime models**
   - Two- and three-state HMM/HSMM regimes.
   - Candidate states: bullish/trending, bearish/trending, neutral/high-volatility.
   - Use regime probabilities as features/conditioning variables rather than deterministic labels.
3. **Supervised directional models**
   - Regularized logistic regression baseline.
   - Shallow XGBoost/LightGBM gradient boosting.
   - Limited feature count and depth to control overfitting.
   - No deep neural network in the first pass.
4. **Hybrid probability engine**
   - Combine calibrated ML probability with regime-conditioned Monte Carlo probability.
   - Produce P(NIFTY expiry > signal spot), P(expiry below lower-tail threshold), median, 5th/25th/75th/95th percentiles.
5. **Trade-aware decision layer**
   - Test confidence thresholds and a no-trade/neutral state.
   - For the Bull structure, explicitly model left-tail probability; for the Bear structure, model right-tail probability.
   - Test predicting structure-level positive P&L directly as a secondary target.
6. **Feature families**
   - NIFTY momentum/trend/realized-volatility features.
   - India VIX level/change/term or implied-realized features where available.
   - Options IV/skew/open-interest/put-call information.
   - FII/DII flows.
   - Global equity/VIX/USDINR/crude/gold/cross-market variables.
   - Breadth/sector-relative features and expiry/calendar variables.
7. **Validation**
   - Anchored walk-forward / purged time-series validation.
   - Embargo at least equal to the forecast horizon when labels overlap.
   - Parameters locked before each out-of-sample block.
   - Evaluate statistical metrics and the actual 3-leg strategy net of costs.
8. **Baselines and controls**
   - Always-Bull and Always-Bear.
   - Random direction with the observed Bull/Bear class balance.
   - Existing 252-day GBM Monte Carlo.
   - Regime-only model.
   - ML-only model.
   - Hybrid model.
9. **Promotion gates**
   - No model is promoted on hit rate alone.
   - Require improvement in out-of-sample drawdown/loss-tail metrics and net P&L without unacceptable deterioration in trade frequency or costs.
   - Require performance across multiple chronological and volatility regimes.

### Phase 6 exit criterion
A direction engine is promoted only if it improves the existing strategy's out-of-sample risk profile versus the current GBM benchmark and randomized/class-balance controls. Otherwise retain the simpler signal.

### Important methodological principle
Monte Carlo remains useful as the **distribution engine**, but it should not be expected to create predictive information by itself. Predictive information should come from conditioning variables/modeling; Monte Carlo then converts those forecasts into a terminal distribution and tail-risk estimate.
