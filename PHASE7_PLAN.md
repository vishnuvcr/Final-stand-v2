# Phase 7 — New Information-Set Restart Protocol

## Purpose
Phase 7 is a restart protocol, not another round of model tweaking on the Phase 1–6 sample. The Phase 6 sample (2022-06-09 through 2026-05-19) is permanently treated as historical development data and is not reopened for feature/model selection.

A restart may proceed only with a genuinely new information set and a fresh, untouched evaluation period.

## Research questions
1. Does adding option-implied information (ATM IV, fixed-moneyness/delta skew, IV term structure, and related surface measures) improve downstream weekly-strategy economics beyond the Phase 6 benchmark?
2. Do India VIX, FII/DII flows, market breadth, global cross-market variables, USDINR, crude, gold, and regime/volatility state variables provide incremental information when timestamped strictly by availability?
3. Do event/news/corporate-action flags add incremental explanatory value without introducing publication-time leakage?
4. Does a preregistered model using this new information set improve costed out-of-sample strategy performance on a fresh untouched period?

## Locked information set
### A. NIFTY option surface
- ATM IV.
- Put-call IV skew at fixed delta/moneyness buckets.
- 1-week / 2-week / 1-month IV term structure where observable.
- IV slope, curvature, and level changes.
- Option volume and open-interest concentration around ATM and OTM strikes.
- Bid/ask spread and liquidity proxies.
- India VIX as a separate volatility-market variable.

### B. Indian market flow and breadth
- FII/FPI net activity.
- DII net activity.
- Cash-market flow changes and rolling z-scores.
- Advance/decline breadth.
- Percentage of eligible NIFTY constituents above 20-day and 50-day moving averages, when reproducibly available.
- Sector breadth/concentration where data quality permits.

### C. Global cross-market state
- S&P 500 / Nasdaq returns.
- CBOE VIX or an equivalent broad global volatility proxy.
- USDINR.
- Brent crude.
- Gold.
- Broad emerging-market/global risk proxy where reproducible.
- Overnight and prior-session changes only; no same-day future information.

### D. Regime and volatility
- 5/20/60-day realized volatility.
- Volatility ratio and volatility-of-volatility proxies.
- Trend, drawdown and range-state measures.
- Cross-asset correlation/risk-on-risk-off state.
- Explicit regime labels derived only from data available at the signal timestamp.

### E. News and corporate actions
- News/event counts and timestamped sentiment/category features rather than unrestricted article text.
- NSE corporate-action/event flags relevant to NIFTY constituents.
- Earnings/dividend/split/bonus/index-event indicators when publication/announcement time can be established.
- If publication timing cannot be verified, the feature is excluded rather than forward-filled.

## Fresh-data boundary
- Development sample: permanently closed at 2026-05-19.
- Fresh holdout begins: 2026-05-20.
- No feature engineering, threshold selection, model selection, or hyperparameter tuning may use any fresh-holdout outcome.
- A minimum of 26 eligible weekly observations is required before a final economic promotion decision. If fewer are available, the result is labelled insufficient_fresh_OOS and no strategy promotion is allowed.
- The fresh period must remain untouched until the complete information set, feature transformations, model class, thresholds, transaction-cost model and promotion criteria are frozen.

## Preregistered methodology
1. Freeze the data dictionary and source hierarchy.
2. Freeze timestamp/availability rules.
3. Freeze feature transformations and missing-data rules.
4. Freeze candidate model classes before evaluating fresh-holdout performance.
5. Use expanding walk-forward training only.
6. Do not randomly shuffle weekly observations.
7. Keep the first 60 observations as a minimum warm-up for supervised/regime models unless a model's preregistered minimum differs.
8. Generate both Bull and Bear counterfactual option P&L for every eligible week.
9. Apply the same Paytm Money proxy, exchange/statutory charges, GST and adverse-slippage framework used previously unless a documented effective-date change requires an update.
10. Preserve a no-trade control, original-direction control, and simple non-model controls.
11. Record all failed observations and missing-data reasons; never silently drop them.
12. Lock the analysis before opening the fresh-period results.

## Promotion criteria — fixed before fresh OOS is opened
A candidate can be promoted only if all primary gates are satisfied on the fresh untouched period:
- At least 26 eligible weekly observations.
- Positive mean net P&L after costs and slippage.
- 95% bootstrap CI for mean weekly net P&L does not cross zero.
- Profit factor > 1.20.
- Maximum drawdown is not worse than the Phase 6 original-direction control by more than 10%.
- Worst trade is not worse than the Phase 6 control by more than 15%.
- No increase in loss frequency greater than 10 percentage points versus the Phase 6 control.
- Improvement must be observed in downstream option P&L, not merely directional accuracy, AUC or Brier score.
- Results must remain directionally/economically consistent under the preregistered cost and slippage sensitivities.
- No post-hoc threshold or feature selection using the fresh holdout.
These are gates, not scores or rankings. Failure of any primary gate means do not promote.

## Statistical analysis
Primary:
- Total and mean net P&L.
- Profit factor.
- Maximum drawdown.
- Worst trade.
- Loss frequency.
- Bootstrap 95% CI for mean P&L.
- Paired weekly P&L difference versus the frozen Phase 6 control.
- Directional Brier/AUC as secondary diagnostics.

Robustness:
- 0/1/2-tick slippage.
- Cost sensitivity using effective-date statutory charges.
- Chronological first/last segments.
- Missing-data stress test.
- Feature-group ablation, frozen before fresh OOS.
- Multiple-comparison awareness; no selective reporting.

## Phase gates
7.1 — Lock restart protocol and feature dictionary.
7.2 — Build/cache the new information-set dataset without opening fresh OOS results.
7.3 — Freeze feature engineering, model classes, costs and promotion criteria.
7.4 — Run fresh untouched OOS (only when >=26 eligible weeks exist).
7.5 — Statistical analysis, robustness and promotion decision.
7.6 — Manuscript addendum and reproducibility audit.

## Current status
**7.1 complete.** The restart protocol is frozen in this branch.
**7.2–7.6 not executed.** As of 2026-10-01, the fresh boundary 2026-05-20 provides fewer than the preregistered 26 weekly observations available for a final promotion decision. No fresh-period performance result is therefore treated as a promotion result.

## Non-negotiable stop rule
Do not reopen Phase 6 for additional model tuning. If Phase 7 later fails, the research stops with the failure documented. A subsequent restart requires a new information set, a new untouched period, and a new preregistration revision.
