# Data Manifest — Phase 1

## Primary option source
- Dataset: Hugging Face thetrademarkk/india-index-options-1m
- NIFTY option path: options/NIFTY/{EXPIRY}.parquet
- NIFTY spot path: index/NIFTY.parquet
- Granularity: 1-minute
- Sample validation file: options/NIFTY/2021-05-27.parquet
- Sample validation rows: 333,365
- Validated option fields: timestamp, open, high, low, close, volume, open_interest, trading_day, symbol, strike, option_type, expiry
- Timestamps are timezone-aware IST

## Secondary spot source
- GitHub: technovusin/nifty50-historical-data
- 1-minute NIFTY50 data by year under 1min/{year}/NIFTY50_1min_{year}.csv
- 2024 sample validated: 92,528 rows

## Exchange rules used
- Weekly NIFTY expiry: Tuesday; if Tuesday is a trading holiday, previous trading day.
- NIFTY index-option tick size: ₹0.05.
- Lot-size history is handled by effective-date tables in the backtest.

## Cost model
- Paytm Money current brokerage proxy: ₹20 per executed F&O order.
- Six option-leg executions per round trip.
- NSE equity-options transaction charge: ₹3,553 per crore premium per side from 2026-03-01.
- STT on option sale: 0.15% of premium from 2026-04-01; 0.10% before that.
- GST: 18% on brokerage and exchange/clearing service components.
- Slippage: one tick (₹0.05) adverse per execution; 2-tick sensitivity.

## Reproducibility
Large parquet files are not committed into Git history. GitHub Actions caches the downloaded Hugging Face snapshot; this manifest plus the run-time source revision/file list provide reproducibility.