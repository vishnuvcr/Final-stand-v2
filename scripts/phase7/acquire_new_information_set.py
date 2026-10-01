from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data_cache" / "phase7"
RAW.mkdir(parents=True, exist_ok=True)
START = dt.date(2022, 1, 1)
END = dt.date.today()
HEADERS = {"User-Agent": "Mozilla/5.0 Final-stand-v2 research data pipeline"}

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

def main():
    manifest = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "start": str(START), "end": str(END),
        "canonical_sources": [
            {"name": "nse_india_vix", "url": "https://www.nseindia.com/resources/exchange-communication-historical-vix"},
            {"name": "nse_option_chain", "url": "https://www.nseindia.com/option-chain"},
            {"name": "nse_fii_dii", "url": "https://www.nseindia.com/reports/fii-dii"},
            {"name": "nse_historical_reports", "url": "https://www.nseindia.com/resources/historical-reports-capital-market-daily-monthly-archives"},
            {"name": "nse_corporate_actions", "url": "https://www.nseindia.com/companies-listing/corporate-filings-actions"},
            {"name": "rbi_reference_rates", "url": "https://www.rbi.org.in/scripts/ReferenceRateArchive.aspx"},
        ],
        "sources": [], "notes": []
    }
    try:
        import yfinance as yf
        tickers = {"sp500":"^GSPC","nasdaq":"^IXIC","vix":"^VIX","usd_inr":"INR=X","brent":"BZ=F","gold":"GC=F"}
        for name, ticker in tickers.items():
            df = yf.download(ticker, start=str(START), end=str(END + dt.timedelta(days=1)),
                             auto_adjust=False, progress=False, group_by="column")
            if df.empty:
                manifest["notes"].append(f"empty_global:{name}")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] for c in df.columns]
            df = df.reset_index()
            df["source"] = "Yahoo Finance"
            df["source_timestamp"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
            df.to_parquet(RAW / f"{name}.parquet", index=False)
            manifest["sources"].append({"name":name,"ticker":ticker,"path":str(RAW / f"{name}.parquet")})
    except Exception as exc:
        manifest["notes"].append(f"global_download_error:{type(exc).__name__}:{exc}")
    save_json(RAW / "source_manifest.json", manifest)

if __name__ == "__main__":
    main()
