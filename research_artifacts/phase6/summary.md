# Phase 6 — Partial execution report

Phase 6 was initiated and the committed Phase-2/3 artifacts were re-used without changing the primary historical specification. A heavy-tail conditional Monte Carlo proxy (Cauchy innovation distribution) was evaluated and an agreement/confidence filter was applied to the existing strategy P&L from the 60th observation onward.

## Findings
- Baseline GBM directional hit rate: 50.67% over 150 observations.
- Cauchy conditional-MC directional hit rate: 50.00% over 150 observations.
- Baseline last-90 trade P&L: ₹165,960.50; win rate 87.78%; max drawdown -₹27,330.62.
- Cauchy agreement filter at 0.52: 69 trades, 76.67% participation, 86.96% win rate, ₹139,382.65 P&L, max drawdown -₹27,330.62.
- At 0.55: 39 trades, 43.33% participation, 87.18% win rate, ₹67,728.79 P&L, max drawdown -₹27,330.62.
- At 0.58: 22 trades, 24.44% participation, 86.36% win rate, ₹28,614.90 P&L, max drawdown -₹27,330.62.
- At 0.60: only 3 trades and negative P&L of ₹28,763.34; max drawdown -₹31,519.99.

## Interpretation
Heavy-tail Monte Carlo alone did not improve directional classification. The simple confidence filter also did not reduce the key drawdown in this sample. This is evidence against spending more effort merely changing the innovation distribution while keeping the same information set.

## Execution limitation
The Phase-6 GitHub Actions workflow and a temporary main-branch runner were committed, but the available GitHub connector does not expose workflow dispatch/run controls and did not return an executable Actions result. Therefore the full planned counterfactual Bull/Bear option repricing, HMM/ML walk-forward ladder, and strategy-level evaluation of direction flips were not claimed as completed. The existing ledger contains realized P&L only for the original predicted side, so opposite-side P&L was not fabricated.

## Next research decision
The evidence supports moving to richer conditioning variables—market regime, volatility state, option-implied information, breadth, global cross-market variables, and a supervised model—only after a runnable counterfactual backtest path is available. The primary promotion gate remains downstream costed P&L/drawdown, not directional accuracy alone.
