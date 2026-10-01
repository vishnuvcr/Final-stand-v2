# Final Manuscript: Monte Carlo Direction + 3-Leg NIFTY Weekly OTM Strategy

## Abstract

This study backtests the user-specified NIFTY weekly-options strategy in which the NIFTY spot close on the previous weekly expiry is used to generate a Monte Carlo forecast for the next weekly expiry. A bullish forecast triggers a long OTM4 put / short OTM5 put / short OTM6 put structure; a bearish forecast triggers the analogous call structure. Entry is defined as 4 trading days before expiry at 10:00 IST and exit at expiry.

Using a public 1-minute NIFTY index-options dataset, the primary specification generated 150 weekly signals and 150 executable trades over the available sample from 9 June 2022 to 19 May 2026. The Monte Carlo directional classifier produced a 50.67% directional hit rate, predicted Bull on 88.67% of observations, and had an AUC of 0.519. Despite the weak directional classification result, the specified option structure produced positive cumulative backtest P&L under the primary settlement + current-cost + one-tick-slippage scenario: ₹198,598.87 on a normalized 65-NIFTY-unit position size, with 134 winning trades out of 150 and a profit factor of 2.13. A 10,000-resample bootstrap gave a 95% confidence interval of approximately ₹347 to ₹2,172 for mean trade P&L.

The central inference is that the observed profitability should not be attributed to strong Monte Carlo direction forecasting. The signal itself is close to chance-level in this sample; profitability appears to arise primarily from the payoff and premium structure of the three-leg option strategy, together with the particular weekly NIFTY distribution observed in the sample. Additional out-of-sample validation, alternative strike definitions, and more complete historical option data are required before treating the result as a durable trading edge.

## 1. Research questions

1. Does a Monte Carlo forecast formed only from information available at the previous weekly expiry close predict whether NIFTY finishes above or below that close at the next weekly expiry?
2. Does the specified 1:-1:-1 OTM4/OTM5/OTM6 option structure generate positive net P&L after brokerage, statutory charges, and slippage?
3. Does the result remain positive under different expiry-exit conventions, slippage assumptions, chronological splits, and historical expiry regimes?
4. Is the apparent trading performance attributable to directional forecasting skill or to the payoff characteristics of the option structure itself?

## 2. Strategy specification

### 2.1 Signal date

The signal uses the closing NIFTY spot price from the previous observed weekly expiry day, after the market close.

### 2.2 Monte Carlo model

The primary model is a geometric Brownian motion baseline calibrated to the most recent 252 trading-day log returns available strictly before the signal timestamp.

For each signal:
- 50,000 terminal paths are simulated.
- A fixed seed is used for reproducibility.
- Let S0 be the prior-expiry spot and ST the simulated terminal value.
- Bull is assigned when P(ST > S0) > 0.5.
- Otherwise the signal is Bear.

No future option prices or post-signal NIFTY information are used in signal construction.

### 2.3 Option structure

For Bull:
- Buy OTM4 put
- Sell OTM5 put
- Sell OTM6 put

For Bear:
- Buy OTM4 call
- Sell OTM5 call
- Sell OTM6 call

Primary OTM definition:
- ATM is the listed strike nearest to NIFTY spot at the 10:00 IST entry.
- OTM4/5/6 means the 4th/5th/6th strike-grid positions away from ATM on the relevant side.
- NIFTY strike spacing is inferred from the available listed strike grid for each expiry file.

This definition is a methodological assumption because “OTM4/OTM5/OTM6” was not independently standardized in the user request.

### 2.4 Entry

Entry is 4 trading sessions before expiry at 10:00 IST.

The backtest uses the 10:00 bar open when available. If the exact 10:00 bar is absent, it uses the most recent quote at or before 10:00 provided that it is no more than five minutes stale.

### 2.5 Exit

Primary exit:
- Expiry intrinsic value using the NIFTY expiry-day close.

Diagnostic exit:
- Last available option print by 15:30 IST when it is no more than 30 minutes stale.
- Otherwise intrinsic fallback.

### 2.6 Trading costs

The normalized position size is 65 NIFTY units for every historical observation so that P&L is comparable through changing lot-size regimes. This is a normalization device, not a claim that the exchange lot was 65 throughout the historical period.

Primary cost scenario:
- Paytm Money F&O brokerage proxy: ₹20 per executed order.
- Six option executions per complete three-leg round trip.
- NSE equity-option transaction charge: ₹3,553 per crore of premium traded, effective from 1 March 2026.
- Option-sale STT: 0.15% of premium from 1 April 2026; 0.10% before that.
- Equity-option stamp duty: 0.003% on buyer-side consideration.
- SEBI turnover fee: ₹10 per crore.
- GST: 18% on broker/exchange service components.
- Slippage: one ₹0.05 option tick adverse per execution.
- Two-tick sensitivity and zero-cost controls are also reported.

The primary scenario's transaction-cost field is applied to execution P&L after slippage; the slippage field is retained as a diagnostic and is not subtracted twice.

## 3. Data

### 3.1 Primary option dataset

The primary source is the Hugging Face dataset:
thetrademarkk/india-index-options-1m

The validated NIFTY option files contain timestamp, OHLC, volume, open interest, trading day, symbol, strike, option type, and expiry. The repository stores the source manifest and runtime dataset revision; large raw Parquet files are not committed into Git history.

The tested option sample contains 150 usable weekly-expiry observations between 9 June 2022 and 19 May 2026.

### 3.2 Spot data

NIFTY spot is taken from the same public research-data environment where possible, with a secondary one-minute NIFTY50 history source used for schema validation.

### 3.3 Coverage caveat

The 150 observations represent the weekly-expiry observations available and usable in the sourced dataset. This should not be interpreted as an exhaustive census of every theoretical weekly expiry in the full period.

## 4. Scientific methodology

The analysis follows a strict information-timing sequence:

1. Observe prior-expiry NIFTY close.
2. Estimate the historical return distribution using only pre-signal observations.
3. Generate the Monte Carlo direction.
4. Wait until the 4-DTE entry date.
5. Determine the entry ATM and OTM strike positions using the 10:00 spot.
6. Enter all three option legs.
7. Carry the structure to expiry.
8. Calculate gross execution P&L.
9. Apply brokerage/statutory costs.
10. Repeat independently for each available weekly observation.

The strategy code, data manifest, phase logs, and error log are committed to the repository. Each research phase has a separate Git branch and a manual GitHub Actions workflow.

## 5. Results

### 5.1 Monte Carlo directional signal

| Metric | Result |
|---|---:|
| Signals | 150 |
| Simulations per signal | 50,000 |
| Calibration window | 252 trading days |
| Predicted Bull share | 88.67% |
| Realized Bull share | 52.67% |
| Directional hit rate | 50.67% |
| Brier score | 0.2505 |
| AUC | 0.5186 |

The Monte Carlo model was strongly biased toward Bull in this sample, while realized weekly direction was close to balanced. The resulting 50.67% hit rate is only slightly above a 50/50 directional baseline.

### 5.2 Primary strategy backtest

| Metric | Primary result |
|---|---:|
| Trades | 150 |
| Winning trades | 134 |
| Losing trades | 16 |
| Win rate | 89.33% |
| Total net P&L | ₹198,598.87 |
| Mean P&L/trade | ₹1,323.99 |
| Median P&L/trade | ₹1,804.50 |
| Profit factor | 2.13 |
| Maximum drawdown | -₹35,661.65 |
| Best trade | ₹16,242.60 |
| Worst trade | -₹32,812.19 |

The full trade-by-trade ledger is in research_artifacts/phase3/trade_ledger.csv.

### 5.3 Exit robustness

The market-exit diagnostic produced:
- Net P&L: ₹196,768.59
- Win rate: 89.33%
- Profit factor: 2.12
- Maximum drawdown: -₹35,729.86

Using the last actionable expiry-day option print rather than intrinsic settlement changed the cumulative result by only about ₹1,830 over 150 trades.

### 5.4 Slippage and cost robustness

| Scenario | Total net P&L |
|---|---:|
| Zero-cost / zero-slippage control | ₹224,198.00 |
| 1-tick slippage + current-cost proxy | ₹198,598.87 |
| 2-tick slippage + current-cost proxy | ₹197,137.55 |
| 1-tick + market-exit diagnostic | ₹196,768.59 |

The total reduction from the zero-cost control to the primary scenario is about ₹25.6k, or 11.4% of the zero-cost result.

Average transaction/statutory cost was approximately ₹160.91 per trade and the modeled slippage diagnostic was ₹9.75 per trade.

### 5.5 Chronological stability

| Period | Trades | Win rate | Total P&L |
|---|---:|---:|---:|
| First 70% | 105 | 89.52% | ₹106,927.91 |
| Last 30% | 45 | 88.89% | ₹91,670.96 |

The positive cumulative result therefore was not confined to only the earlier portion of the sample.

### 5.6 Expiry-regime stability

| Regime | Trades | Win rate | Total P&L |
|---|---:|---:|---:|
| Legacy Thursday regime | 126 | 90.48% | ₹160,310.54 |
| Tuesday regime | 24 | 83.33% | ₹38,288.34 |

The Tuesday sample is much smaller and should not be treated as conclusive evidence of long-run post-rule-change behavior.

### 5.7 Annual breakdown

| Year | Trades | Win rate | Total P&L |
|---|---:|---:|---:|
| 2022 | 24 | 87.50% | ₹7,703.28 |
| 2023 | 38 | 94.74% | ₹26,402.22 |
| 2024 | 38 | 86.84% | ₹66,972.42 |
| 2025 | 37 | 91.89% | ₹75,029.17 |
| 2026 | 13 | 76.92% | ₹22,491.79 |

## 6. Statistical analysis

### 6.1 Mean P&L

The mean trade P&L in the primary scenario is ₹1,323.99.

A deterministic 10,000-resample bootstrap of the mean produced a 95% interval of approximately ₹347 to ₹2,172.

### 6.2 Win rate

134 of 150 trades were profitable. A two-sided exact binomial test against a 50% win-rate null gave p approximately 7.7e-16.

This statistic should not be interpreted as evidence that the Monte Carlo classifier itself is highly accurate, because the classifier's directional hit rate was only 50.67%. The high option-trade win rate is a property of the complete option strategy and payoff shape.

### 6.3 Serial dependence

Lag-1 autocorrelation of weekly trade P&L was approximately -0.073, providing no evidence of strong positive first-order clustering in this sample.

### 6.4 Signal calibration

The Monte Carlo signal had:
- Brier score = 0.2505
- AUC = 0.5186
- Directional accuracy = 50.67%

These numbers indicate weak separation between eventual Bull and Bear weeks.

## 7. Interpretation and inference

The result contains two distinct empirical findings.

First, the Monte Carlo direction model has weak predictive power in this specification. It is slightly better than random in hit rate, but its AUC is close to 0.5 and it produces a very strong Bull class imbalance.

Second, the complete three-leg option strategy nevertheless generated substantial positive historical P&L in the tested sample.

Therefore, the evidence does not support the explanation “the strategy works because Monte Carlo predicts NIFTY direction accurately.” A more plausible explanation within this backtest is that the option payoff profile can make money over many weeks even when the directional call is often only marginally informative. The long OTM4 leg is paired with two farther OTM short legs, producing asymmetric sensitivity to the underlying's realized move and the option-premium geometry.

That distinction is central: the research tests the user's strategy exactly, but the profitability result should not be conflated with a strong directional forecasting edge.

## 8. Strengths

1. Information timing is explicitly separated to reduce look-ahead bias.
2. The same signal logic is applied mechanically across all observations.
3. The trade ledger records every leg and every cost component.
4. Brokerage, exchange charges, STT, stamp duty, GST, SEBI fee, and tick slippage are included.
5. Settlement and actionable-market exit conventions are both examined.
6. Chronological and expiry-regime splits are reported.
7. The source dataset revision and research-control files are retained in the repository.

## 9. Limitations

1. The primary option dataset does not necessarily contain every weekly expiry in the theoretical universe; the sample is the set of observations available in the source.
2. The OTM4/OTM5/OTM6 interpretation is a declared assumption based on strike-grid distance from entry ATM.
3. A constant normalized size of 65 units is used for historical comparability and is not a reconstruction of historical exchange lot sizes.
4. One-tick slippage is only a minimum liquidity proxy. Real fills can be worse, especially in farther OTM strikes.
5. The expiry exit is modeled from intrinsic settlement; it does not simulate broker order execution immediately before settlement.
6. The primary Monte Carlo model is a simple GBM baseline and does not explicitly model jumps, volatility clustering, volatility smiles, or option-implied information.
7. The current primary cost model is a normalized current-cost framework; historical brokerage/tax schedules can differ across the sample.
8. The alternative 63/504-session Monte Carlo-window sensitivity was specified but was not finalized in the CI artifact because the Phase-4 workflow encountered repeatable runner/data-interface errors. No result from those alternative windows is presented.
9. No live trading performance, margin utilization, liquidity capacity, or broker-specific rejection/partial-fill behavior is established by this backtest.

## 10. Discussion

The highest-value methodological observation is that a profitable option strategy does not require a highly accurate directional signal when the payoff profile itself contains a favorable distribution under the realized market dynamics.

However, this also means the strategy is vulnerable to changes in the volatility surface, skew, tail frequency, strike spacing, and weekly expiry microstructure. A strategy whose payoff is generated by option premium geometry can deteriorate without the underlying directional model becoming materially worse.

The apparent robustness across years and the positive chronological split are encouraging within the tested dataset, but they do not remove model-risk concerns. The 2022 drawdown and relatively lower early-period mean P&L show that the strategy is not uniformly profitable every week. The Tuesday expiry regime also has fewer observations, making its apparent persistence uncertain.

The weak Monte Carlo AUC is a particularly important warning. If the option structure remains profitable after replacing the directional signal with weaker or randomized controls, the signal component would be unnecessary. That counterfactual should be the next research step.

## 11. Conclusion

For the exact backtest specification implemented here, the strategy produced positive historical net P&L on the available 150 weekly observations:
- 150 trades
- 89.33% winning trades
- ₹198,598.87 cumulative net P&L on a normalized 65-unit position
- Profit factor 2.13
- Maximum drawdown ₹35,661.65

The Monte Carlo directional classifier itself did not show a strong predictive edge:
- 50.67% hit rate
- AUC 0.5186
- Bull forecast on 88.67% of weeks

The evidence therefore supports the statement that the combined option strategy was profitable in this historical sample under the stated assumptions, while providing weak evidence that the Monte Carlo direction forecast was the source of that profitability.

This is a backtest result, not evidence of guaranteed future performance.

## 12. Future research directions

1. Run a complete counterfactual with the same option structures but randomized/Bernoulli direction signals to isolate the value of the Monte Carlo signal.
2. Run always-Bull and always-Bear structural controls using the same three-leg payoff.
3. Compare OTM4/5/6 definitions based on strike-grid distance versus fixed delta or fixed percentage moneyness.
4. Replace GBM with stochastic-volatility, jump-diffusion, and regime-switching models.
5. Add option-implied volatility, skew, term structure, India VIX, FII/DII flows, global-market conditions, and cross-market signals.
6. Use a truly out-of-sample walk-forward model with calibration frozen before each test block.
7. Add realistic bid/ask spreads, liquidity filters, partial fills, order-book depth, and margin requirements.
8. Extend the historical option dataset and independently reconcile expiry settlements against official exchange data.
9. Test the strategy under exact historical lot sizes, historical tax schedules, and broker-specific order costs.
10. Evaluate capacity and capital efficiency before considering any live deployment.

## Appendix A — Repository artifacts

- Research plan: RESEARCH_PLAN.md
- Research log: RESEARCH_LOG.md
- Error log: ERROR_LOG.md
- Data manifest: DATA_MANIFEST.md
- Literature review: LITERATURE_REVIEW.md
- Cost model: COST_MODEL.md
- Monte Carlo signal table: research_artifacts/phase2/signal_table.csv
- Trade ledger: research_artifacts/phase3/trade_ledger.csv
- Equity curve: research_artifacts/phase4/equity_curve.csv
- Annual P&L: research_artifacts/phase4/yearly_pnl.csv
- Signal confusion table: research_artifacts/phase4/signal_confusion.csv
- Cumulative P&L chart: research_artifacts/phase4/cumulative_pnl.svg
- Annual P&L chart: research_artifacts/phase4/annual_pnl.svg

## Appendix B — Reproducibility

Primary random seed: 20261001.

Primary Monte Carlo calibration: 252 trading sessions.

Primary simulations: 50,000 paths per weekly signal.

Primary normalized quantity: 65 NIFTY units.

Primary execution scenario: 1 tick slippage + current-cost proxy + expiry intrinsic settlement.

## Appendix C — Research status

Phase 1 — Data and specification: complete.

Phase 2 — Monte Carlo signal: complete.

Phase 3 — Strategy backtest: complete.

Phase 4 — Statistics and robustness: core statistics independently completed and recorded; automated workflow encountered implementation errors documented in ERROR_LOG.md. Alternative Monte Carlo-window sensitivity remains unfinalized.

Phase 5 — Manuscript and research package: complete.


## References

1. NSE India. NIFTY derivatives contract specifications and expiry conventions. Current exchange documentation.
2. NSE India. Equity-derivatives transaction charges, STT, and other levies.
3. Paytm Money. Current brokerage/pricing schedule for F&O.
4. Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2014). Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance.
5. Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2016). Backtest Overfitting in Financial Markets.
6. Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio.
7. Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2015). The Probability of Backtest Overfitting.
8. Hugging Face dataset: thetrademarkk/india-index-options-1m.
9. GitHub dataset: technovusin/nifty50-historical-data.

Key URLs are also preserved in DATA_MANIFEST.md, COST_MODEL.md, and LITERATURE_REVIEW.md.


## 12. Phase 6 Direction-Engine Extension — Partial Execution

A second-stage direction-engine study was initiated to test whether replacing the baseline Gaussian Monte Carlo innovation assumption with a heavier-tailed conditional distribution could improve directional classification and reduce drawdown through confidence filtering. An artifact-level Cauchy-innovation proxy was computed from the same leakage-safe drift/volatility inputs. Across the 150 observations, the baseline GBM direction hit rate was 50.67%, while the Cauchy conditional-MC proxy was 50.00%. This did not provide evidence that changing the innovation distribution alone improves weekly NIFTY direction prediction.

For the available post-warm-up period (90 observations), an agreement filter that retained the original strategy direction only when the heavy-tail proxy agreed with the baseline and exceeded a fixed confidence threshold produced the following sensitivity: threshold 0.52 retained 69 trades with 86.96% wins and ₹139,382.65 P&L but did not reduce the -₹27,330.62 drawdown; threshold 0.55 retained 39 trades with 87.18% wins and ₹67,728.79 P&L and the same maximum drawdown; threshold 0.58 retained 22 trades with 86.36% wins and ₹28,614.90 P&L and the same maximum drawdown. A 0.60 threshold retained only three trades and produced negative P&L. These are filter diagnostics, not a promoted strategy variant.

The planned HMM, supervised-model, hybrid ensemble, and counterfactual Bull/Bear option repricing were not claimed as completed because the available repository execution interface did not expose a reliable workflow-dispatch operation. The committed Phase-3 ledger contains P&L for the originally selected side but not the opposite-side structure, so assigning counterfactual P&L without rerunning the option-pricing engine would introduce unsupported assumptions. The Phase-6 artifacts therefore record an explicit partial result rather than a model-selection conclusion.

### Revised inference

The current evidence strengthens the original conclusion: the option payoff structure is doing most of the observed buffering, while the tested Monte Carlo direction layer has not demonstrated a stable directional edge. Future direction-engine work should add conditional information rather than merely increasing simulation count or changing the innovation distribution. The decisive test remains a strict walk-forward, costed, counterfactual backtest that prices both Bull and Bear structures for every decision and evaluates drawdown and tail loss directly.
