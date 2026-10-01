# Phase 7.3 — Frozen Model and Analysis Specification (P7.3-v1)

## Status
Frozen on 2026-10-01 before any fresh-holdout outcome was inspected.

## Purpose
Evaluate whether the new information set provides incremental downstream economic value without reopening the Phase 1–6 development sample.

## Data boundary
- Development: through 2026-05-19.
- Fresh untouched period: from 2026-05-20.
- Fresh outcomes must not be used for feature, threshold, model, or hyperparameter selection.
- Final economic promotion requires at least 26 eligible fresh weekly observations.

## Primary information set
1. NIFTY and global returns/realized-volatility state: NIFTY, S&P 500, Nasdaq, Cboe VIX, USDINR, Brent, gold.
2. India VIX: level, change, rolling z-scores.
3. NIFTY option surface: observable ATM IV, fixed-moneyness skew/curvature, PCR OI/volume, OI/volume concentration, and observable IV term-structure slopes.
4. FII/DII: net flow, rolling sums and z-scores, strictly aligned to information available before the signal.
5. Regime/volatility transformations derived only from prior observations.

### Explicitly excluded from P7.3-v1 primary model
- Market breadth: current reproducible public acquisition produced no parseable daily rows.
- Corporate-action rows: no usable publication/timing-provenanced historical rows were established before freeze.
- Free-form news/sentiment: no historical publication-time-safe reproducible source was established before freeze.
- Unobservable option tenors: retained as missing; never imputed from future or synthetic observations.

These exclusions are limitations, not post-hoc choices after fresh outcomes.

## Missing-data policy
- Never forward-fill across a signal boundary.
- Add explicit missing indicators where a feature can be absent.
- Impute numeric missing values using training-window medians only.
- Standardization parameters are fit on the training window only.
- Fresh observations are transformed using frozen parameters from their preceding training window.
- Features with zero training observations or zero variance are excluded by the frozen preprocessing rule.
- Failed observations and source-coverage reasons remain in audit artifacts.

## Primary model
Regularized logistic regression predicting whether next weekly NIFTY expiry return is positive.
- L2 penalty.
- C = 1.0.
- Training-window median imputation + missing indicators + standardization.
- No PCA.
- No random shuffling.
- Expanding walk-forward training.
- Minimum historical warm-up: 60 eligible weekly observations.
- Bull signal: probability >= 0.55.
- Bear signal: probability <= 0.45.
- Otherwise: no trade.

## Secondary diagnostics
- Shallow gradient-boosted tree: max depth 2, 100 estimators, learning rate 0.05, minimum leaf 10.
- Option-implied-only regularized logistic model with the same preprocessing and thresholds.
These are diagnostics and are not independently tuned on the fresh holdout.

## Controls
- Frozen Phase 6 original-direction counterfactual.
- No-trade control.
- Simple NIFTY-return-sign control.

For every eligible week, compute both Bull and Bear downstream three-leg option counterfactual P&L before applying the selected direction, so alternative models never rely on fabricated opposite-side P&L.

## Economic endpoint
Primary endpoint is downstream weekly three-leg option net P&L after the established Paytm Money proxy, exchange/statutory charges, GST and adverse slippage.

Slippage sensitivity:
- 0 ticks.
- 1 tick (primary).
- 2 ticks.

Costs are applied using their effective dates where relevant. The 65-unit normalization is retained as a notional comparison convention, not a historical claim about the lot size for every observation.

## Statistical analysis
Primary:
- total and mean weekly net P&L;
- profit factor;
- maximum drawdown;
- worst trade;
- loss frequency;
- 10,000-replicate percentile bootstrap 95% CI for mean weekly net P&L;
- paired weekly P&L difference versus the frozen Phase 6 control.

Secondary:
- directional Brier score and AUC.

Robustness:
- 0/1/2 tick slippage;
- effective-date cost sensitivity;
- chronological first/last segments;
- missing-data stress;
- preregistered feature-group ablation;
- block-bootstrap sensitivity if serial dependence is material;
- multiple-comparison awareness without selective reporting.

## Promotion gates
A candidate is promoted only if every gate passes:
1. >=26 eligible fresh weeks.
2. Positive mean net P&L after costs/slippage.
3. 95% bootstrap CI for mean weekly net P&L does not cross zero.
4. Profit factor > 1.20.
5. Maximum drawdown is not worse than Phase 6 original-direction control by >10%.
6. Worst trade is not worse by >15%.
7. Loss frequency does not increase by >10 percentage points versus the Phase 6 control.
8. Improvement is demonstrated in downstream option P&L, not direction metrics alone.
9. Results remain economically consistent under preregistered cost/slippage sensitivities.
10. No post-hoc fresh-holdout feature/model/threshold selection.

Failure of any primary gate means no promotion.

## Stop rule
If the fresh period is too short, data quality is inadequate, or no candidate passes all gates, report the failure/insufficiency and stop. Do not reopen the old sample for tuning. A later restart requires a new information set, a new untouched period, and a new preregistration version.
