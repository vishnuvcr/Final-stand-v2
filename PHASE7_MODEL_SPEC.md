# Phase 7.3 — Preregistered model and analysis specification

**Status:** frozen before any fresh-period performance evaluation.

## Information actually eligible for the primary model

### Included
1. NIFTY/global market state:
   - NIFTY returns and 5/20/60-session realized volatility.
   - S&P 500, Nasdaq, Cboe VIX, USDINR, Brent and gold prior-session returns/levels.
   - Trend, drawdown, volatility-ratio and cross-asset state variables already defined in the Phase 7 feature dictionary.
2. India VIX:
   - level, change, 20-session z-score and 60-session z-score.
3. NIFTY option surface:
   - ATM IV where available.
   - fixed-moneyness put/call skew and curvature where available.
   - OI/volume concentration and PCR proxies.
   - 1W/2W/1M term-slope variables only where the corresponding contracts are actually observable.
   - source: immutable revision of `thetrademarkk/india-index-options-1m`.
4. FII/DII:
   - net flows, rolling 5-session sums and 20-session z-scores where source coverage exists.

### Excluded from primary model
- Market breadth: current public acquisition path produced zero parseable daily PR rows.
- Corporate-action rows: current public acquisition path produced zero usable rows with verifiable timing.
- Free-form news/sentiment: no historical publication-time-safe, reproducible source was established before this freeze.
- Any option-surface feature requiring unavailable historical intraday observations.

These exclusions are not retroactive feature selection. They are fixed source-coverage decisions made before fresh OOS evaluation.

## Missing-data policy
- Never forward-fill across unavailable source dates.
- Retain explicit missingness indicators for each feature group.
- For supervised models, numeric imputation uses training-window medians only.
- A feature with zero variance or zero observed values in the current training window is excluded automatically by the frozen preprocessing rule.
- Fresh-period values are transformed only using parameters fit on data available before that signal.

## Primary model
Regularized logistic regression predicting the probability that NIFTY's next weekly expiry return is positive.

Fixed preprocessing:
- training-window median imputation;
- missingness indicators;
- standardization using training-window mean/SD;
- no PCA;
- no random shuffling.

Fixed hyperparameter:
- L2 penalty C = 1.0.

Decision rule:
- Bull if predicted P(up) >= 0.55.
- Bear if predicted P(up) <= 0.45.
- Otherwise no trade.

The 0.55/0.45 thresholds are locked before fresh OOS and are not optimized on the fresh period.

## Secondary diagnostic models
Run only as preregistered diagnostics, not as a post-hoc selection ladder:
1. Shallow gradient-boosted trees with a fixed maximum depth of 2, 100 estimators, learning rate 0.05, minimum leaf size 10.
2. A simple option-implied-only logistic model using the option-surface/India-VIX group.

No hyperparameter search is permitted.

## Controls
- Frozen Phase-6 original-direction counterfactual control.
- No-trade control.
- Simple NIFTY-return sign baseline where computable without future information.

## Walk-forward protocol
- Development history through 2026-05-19 only for model fitting and preprocessing.
- Expanding training window.
- Minimum 60 completed historical weekly observations before supervised prediction.
- One prediction per eligible fresh weekly signal.
- No fresh outcome is read until the candidate/model specification is frozen.
- Final economic promotion requires >=26 eligible fresh weeks.

## Primary economic endpoint
Weekly downstream three-leg option-strategy net P&L after:
- Paytm Money brokerage proxy;
- NSE/exchange/statutory charges using effective dates;
- GST;
- adverse slippage of 0/1/2 ticks in sensitivity analysis.

## Primary promotion gates
All must pass:
- >=26 eligible fresh weeks.
- Positive mean net weekly P&L.
- 95% bootstrap CI for mean weekly P&L excludes zero.
- Profit factor >1.20.
- Max drawdown not worse than Phase-6 original-direction control by >10%.
- Worst trade not worse by >15%.
- Loss frequency increase <=10 percentage points.
- Economic improvement must be visible in option P&L, not merely classification metrics.
- Robustness to preregistered cost/slippage sensitivities.
- No post-hoc fresh-holdout selection.

## Statistical tests
- Percentile bootstrap CI for mean weekly net P&L; 10,000 resamples.
- Paired bootstrap of weekly P&L difference versus the frozen Phase-6 control.
- Profit factor, max drawdown, worst trade and loss frequency.
- Brier score and AUC as secondary diagnostics.
- Chronological first-half/second-half and cost/slippage sensitivity.
- If serial dependence is detected, report a block-bootstrap sensitivity; this does not replace the preregistered primary bootstrap.

## Fresh-OOS opening rule
Do not execute Phase 7.4 until the fresh boundary contains at least 26 eligible weekly observations. Until then, the fresh period remains untouched and no performance output is used for model choice.

**Protocol version:** P7.3-v1
**Frozen date:** 2026-10-01
