# Phase 6 — Direction Engine v2

## Objective
Reduce the frequency and magnitude of losing weeks and maximum drawdown while preserving the existing 1:-1:-1 NIFTY OTM4/OTM5/OTM6 payoff buffer. Directional accuracy is a secondary diagnostic; the promotion metric is downstream, costed option-strategy P&L under strict chronological out-of-sample evaluation.

## Model ladder
1. Existing 252-session GBM Monte Carlo baseline.
2. Student-t conditional Monte Carlo using the same leakage-safe rolling moments.
3. Expanding 2-state Gaussian HMM regime probability, estimated only from returns known before each decision.
4. Logistic regression directional model.
5. Shallow boosted-tree directional model (XGBoost when available; deterministic sklearn fallback).
6. Hybrid probability = equal-weight ensemble of conditional Monte Carlo, logistic, boosted-tree, and HMM probabilities.
7. Abstention/no-trade thresholds tested at fixed confidence bands; threshold selection, when used, is made only from prior observations.
8. Downstream counterfactual option backtest prices both Bull and Bear structures for every eligible expiry, with the existing brokerage/statutory/slippage model.

## Validation
- Expanding walk-forward only.
- Minimum training history: 60 observations.
- No current/future label is used to form a feature.
- Weekly labels resolve at expiry; no random train/test shuffling.
- Primary evaluation remains the same 150-observation period and normalized 65-unit position size.
- Every candidate is compared against current GBM, always-Bull, always-Bear, and no-trade controls.
- Costs: same Paytm Money proxy, NSE transaction charges, STT, stamp, SEBI fee, GST and one-tick slippage.
- Promotion requires improvement in downstream OOS loss frequency/tail loss/drawdown without sacrificing economic robustness; no model is promoted solely because of accuracy.

## Statistical outputs
For every model and threshold: trades, participation, win rate, total/mean/median P&L, profit factor, maximum drawdown, worst trade, loss frequency, lower-tail loss quantiles, bootstrap confidence interval for mean P&L, and directional Brier/AUC where defined. Also report chronological first/last segments and model-vs-baseline paired trade differences.

## Phase gates
6.1 data/features and counterfactual pricing
6.2 model ladder
6.3 walk-forward evaluation
6.4 robustness/statistical analysis
6.5 manuscript and README update
6.6 final reproducibility check

## Research status
Phase 6 is the active phase. Results must be committed with the code, model specification, errors, and reproducibility metadata.

## Execution status
Workflow trigger commit issued; results will be committed by GitHub Actions after data/model execution.
