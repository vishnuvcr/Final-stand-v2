# Research Restart Rule

This project has a permanent anti-overfitting restart rule.

## Closed development sample
All observations through 2026-05-19 belong to the existing development/evaluation history. Phase 6 exhausted the planned model ladder on that sample.

**Never use that same sample for another round of feature/model/threshold tweaking.**

## Required restart
A future restart must introduce information that was not used in Phase 1–6, including where available:
- option-implied skew and IV term structure;
- India VIX;
- FII/FPI and DII flows;
- market breadth;
- global cross-market signals;
- USDINR;
- crude and gold;
- regime/volatility information;
- timestamped news and corporate-action/event features.

The restart must use a fresh untouched period beginning after 2026-05-19, with at least 26 eligible weekly observations before a promotion decision.

## Lock-before-look rule
Before examining fresh-holdout performance, freeze:
- data sources and source hierarchy;
- availability timestamps;
- feature definitions and transformations;
- missing-data policy;
- model classes;
- hyperparameter ranges;
- thresholds;
- transaction-cost/slippage assumptions;
- primary statistical tests;
- promotion criteria.

Any change after fresh-holdout inspection creates a new preregistration version and invalidates the prior fresh-holdout result for promotion.

## Economic decision rule
Promotion is based on costed downstream option P&L and risk, not directional accuracy alone. A candidate must pass every preregistered primary gate in PHASE7_PLAN.md.

## Stop condition
If the fresh period is too short, data quality is inadequate, or no candidate passes all gates, report that result and stop. Do not continue tuning the same sample.
