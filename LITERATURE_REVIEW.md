# Literature and Methodology Notes

## Monte Carlo / stochastic simulation
The signal model uses a geometric-Brownian-motion Monte Carlo as a transparent baseline rather than an optimized predictive model. The model produces a terminal distribution conditional on the historical drift and volatility estimated only from data available before the signal timestamp.

## Backtest integrity
The design explicitly separates signal formation, entry, and exit timestamps. This is important because backtest overfitting can make a strategy appear strong after enough alternative configurations are tried. Bailey et al. discuss the probability of backtest overfitting and recommend out-of-sample controls; the research therefore fixes a primary specification before the robustness phase.

Primary references:
- Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance. Notices of the AMS. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2308659
- Bailey, D. H., Borwein, J., López de Prado, M., Salehipour, A., & Zhu, Q. J. (2016). Backtest Overfitting in Financial Markets. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2731886
- Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551
- Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2015). The Probability of Backtest Overfitting. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253

## Research implication
The backtest will report the number of configurations tried, keep the 252-session / 50,000-simulation specification fixed as primary, and treat parameter sensitivities as secondary analyses rather than selecting the best-performing variant.


## Phase 7 restart literature additions

### Patra (2025) — Volatility Modelling for Indian Markets
Patra evaluates NIFTY 50 daily options and reports predictive information in ATM and skew-based OTM option features for 30-day realized variance. This supports testing option-surface variables as a distinct information family rather than merely retuning the original Monte Carlo distribution.

### Potharla & Sen (2026) — Conditional Dynamics of Volatility Smile Asymmetry
The study of NIFTY-50 options separates smile intensity and tail asymmetry using curvature measures and reports regime-dependent maturity effects. This motivates preregistered skew, curvature and term-structure variables while avoiding post-hoc feature selection.

### Sajjan (2026) — Variance Risk Premium in Nifty 50 Weekly Expiry Cycles
The study examines 380 weekly expiry cycles through June 2026 and reports that India VIX has aggregate information about weekly move magnitude but regime dependence matters. This supports using India VIX as one component of a broader information set rather than as a standalone direction signal.

### Sources
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5748922
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6857939
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6918100
