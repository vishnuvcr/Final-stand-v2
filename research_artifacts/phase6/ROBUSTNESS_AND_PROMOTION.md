# Phase 6 — Robustness and promotion decision

## Primary walk-forward window
The executable Phase-6 run used 150 signals, with the first 60 observations reserved for warm-up and 90 chronological out-of-sample decisions. Both Bull and Bear option structures were repriced for every eligible expiry using the Phase-3 cost/slippage model.

## Original-direction control
For the last 90 observations, applying the original Phase-2 Monte Carlo direction without abstention produced:
- 90 trades
- 87.78% winning trades
- ₹166,402.21 net P&L
- Profit factor 2.41
- Maximum drawdown -₹27,288.66
- Worst trade -₹27,288.66

## Walk-forward models at the fixed 0.55/0.45 abstention rule

| Model | Trades | Participation | Win rate | Total P&L | Profit factor | Max DD | Worst trade | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GBM MC | 41 | 45.6% | 87.80% | ₹72,335.38 | 2.08 | -₹27,288.66 | -₹27,288.66 | 0.575 |
| Student-t MC | 41 | 45.6% | 87.80% | ₹72,335.38 | 2.08 | -₹27,288.66 | -₹27,288.66 | 0.567 |
| HMM | 86 | 95.6% | 84.88% | ₹92,169.66 | 1.55 | -₹44,841.96 | -₹40,824.16 | 0.485 |
| Logistic | 70 | 77.8% | 84.29% | ₹58,998.92 | 1.46 | -₹40,428.48 | -₹27,288.66 | 0.467 |
| Boosted | 79 | 87.8% | 86.08% | ₹53,995.44 | 1.35 | -₹50,466.85 | -₹40,824.16 | 0.547 |
| Hybrid | 52 | 57.8% | 86.54% | ₹48,769.52 | 1.48 | -₹42,000.23 | -₹40,824.16 | 0.514 |

The fixed threshold comparison is deliberately not treated as a hyperparameter optimization result.

## Directional classification diagnostic

Raw probability-to-direction hit rates over the 90 out-of-sample observations were:
- GBM: 47.78%
- Student-t: 46.67%
- HMM: 50.00%
- Logistic: 45.56%
- Boosted: 53.33%
- Hybrid: 48.89%

The boosted model therefore showed the highest raw directional hit rate in this particular walk-forward sample, but its strategy-level drawdown and total P&L were inferior to the original-direction control.

## Threshold sensitivity

Confidence filtering did not yield a stable drawdown improvement:
- GBM at 0.60: 19 trades, 89.47% win rate, ₹46,317.68 P&L, maximum drawdown -₹29,369.35.
- Logistic at 0.65: 31 trades, 87.10% win rate, ₹53,508.74 P&L, maximum drawdown -₹26,966.48.
- Hybrid at 0.65: 12 trades, 83.33% win rate, negative ₹39,958.46 P&L, maximum drawdown -₹68,112.82.
- Higher thresholds generally reduce participation and can leave the sample dominated by a few tail events.

The small apparent drawdown improvement for logistic at 0.65 is not sufficient for promotion because that threshold was inspected after seeing the historical results and the total P&L falls substantially; it also requires independent confirmation on a fresh out-of-sample period.

## Bootstrap uncertainty

The model-specific bootstrap confidence intervals for mean P&L at the fixed threshold include zero for every tested model:
- GBM: approximately -₹547 to ₹3,681
- Student-t: approximately -₹547 to ₹3,681
- HMM: approximately -₹686 to ₹2,556
- Logistic: approximately -₹817 to ₹2,297
- Boosted: approximately -₹1,125 to ₹2,229
- Hybrid: approximately -₹1,473 to ₹2,832

These intervals reinforce that the Phase-6 sample is too small to treat the apparent differences between models as established superiority.

## Promotion gate

**No Phase-6 directional model is promoted.**

The existing strategy remains the benchmark because:
1. The original-direction control generated higher total P&L than every tested Phase-6 model at the fixed abstention rule.
2. None of the new models produced a robust reduction in maximum drawdown.
3. Raw directional accuracy remained close to chance for most models; the boosted model's 53.33% was not enough to translate into better economic outcomes.
4. Heavy-tail Monte Carlo did not improve the direction signal.
5. The option payoff structure remains the dominant source of observed buffering in this sample.

## Research stopping point

Phase 6 is closed at the planned gates. The project should not continue by adding progressively more complex models to the same 150-week sample. Any future research should first acquire a genuinely new information set and a fresh out-of-sample period, then preregister the model/promotion criteria before testing.
