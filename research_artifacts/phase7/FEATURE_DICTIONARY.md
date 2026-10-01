# Phase 7 Feature Dictionary

| Group | Feature family | Timing rule | Primary transformation |
|---|---|---|---|
| Option surface | ATM IV | known by signal timestamp | level, change, percentile |
| Option surface | IV skew | known by signal timestamp | fixed-delta/moneyness put-call skew |
| Option surface | IV term structure | known by signal timestamp | slope, curvature, ratios |
| Option surface | OI/volume/liquidity | known by signal timestamp | concentration, z-score, spread |
| Volatility | India VIX | prior available observation | level, change, percentile |
| Flows | FII/FPI | publication-time verified | net flow, rolling z-score |
| Flows | DII | publication-time verified | net flow, rolling z-score |
| Breadth | Advances/declines | timestamp verified | A/D ratio, breadth z-score |
| Breadth | Constituent trend breadth | timestamp verified | % above MA20/MA50 |
| Global | S&P 500 / Nasdaq | prior session | return, gap |
| Global | VIX | prior session | level, change |
| FX | USDINR | prior available fixing/session | return, z-score |
| Commodities | Brent | prior session | return, shock |
| Commodities | Gold | prior session | return, shock |
| Regime | realized volatility | pre-signal NIFTY | 5/20/60D |
| Regime | trend/drawdown | pre-signal NIFTY | moving-average distance, drawdown |
| Events | corporate actions | announcement/ex-date verified | binary/event count |
| News | news/event metadata | publication-time verified | count/category/sentiment |

All features must carry source_timestamp, availability_timestamp, and feature_cutoff_timestamp. A feature is invalid if its availability cannot be established before the signal cutoff.
