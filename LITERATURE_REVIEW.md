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
