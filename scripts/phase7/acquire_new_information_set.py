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
        tickers = {"nifty":"^NSEI","sp500":"^GSPC","nasdaq":"^IXIC","vix":"^VIX","usd_inr":"INR=X","brent":"BZ=F","gold":"GC=F"}
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
    # Secondary, reproducible FII/DII cash-flow archive. NSE remains canonical;
    # this public GitHub archive is used as a historical backfill/validation source.
    try:
        import subprocess
        flow_repo = RAW / "fii_dii_source"
        if not flow_repo.exists():
            subprocess.run([
                "git","clone","--depth","1","--filter=blob:none","--sparse",
                "https://github.com/chirag127/fii-dii-activity-api.git", str(flow_repo)
            ], check=True)
            subprocess.run(["git","-C",str(flow_repo),"sparse-checkout","set","data"], check=True)
        manifest["sources"].append({
            "name":"fii_dii_public_archive",
            "url":"https://github.com/chirag127/fii-dii-activity-api",
            "path":str(flow_repo / "data"),
            "role":"secondary_historical_backfill_validation"
        })
    except Exception as exc:
        manifest["notes"].append(f"fii_dii_archive_error:{type(exc).__name__}:{exc}")
    save_json(RAW / "source_manifest.json", manifest)

def acquire_nse_exchange_features():
    try:
        from nse import NSE
        with NSE(download_folder=RAW, server=True) as nse:
            vix = nse.fetch_historical_vix_data(from_date=START, to_date=END)
        pd.DataFrame(vix).to_parquet(RAW / "india_vix.parquet", index=False)
    except Exception as exc:
        manifest_note = {"error": f"india_vix:{type(exc).__name__}:{exc}"}
        save_json(RAW / "india_vix_error.json", manifest_note)

    # Daily NSE F&O option snapshots from the official archive URL, accessed
    # through the nse package session to handle exchange cookies/rate limits.
    try:
        from nse import NSE
        sig = ROOT / "research_artifacts" / "phase2" / "signal_table.csv"
        dates = pd.read_csv(sig, usecols=["signal_date"])["signal_date"].dropna().unique().tolist() if sig.exists() else []
        fresh = pd.date_range(dt.date(2026, 5, 20), END, freq="W-TUE").strftime("%Y-%m-%d").tolist()
        dates = sorted(set(dates + fresh))
        out = RAW / "nifty_option_eod"
        out.mkdir(parents=True, exist_ok=True)
        with NSE(download_folder=out, server=True) as nse:
            for d in dates:
                target = out / f"optidx_{d}.csv"
                if target.exists():
                    continue
                day = dt.date.fromisoformat(d)
                urls = [
                    f"https://nsearchives.nseindia.com/content/fo/optidx{day:%d%m%Y}.csv",
                    f"https://archives.nseindia.com/content/fo/optidx{day:%d%m%Y}.csv",
                ]
                downloaded = None
                for url in urls:
                    try:
                        downloaded = nse.download_document(url)
                        if downloaded and Path(downloaded).exists():
                            Path(downloaded).replace(target)
                            break
                    except Exception:
                        continue
                if not target.exists():
                    (out / f"optidx_{d}.missing").touch()
    except Exception as exc:
        save_json(RAW / "nse_option_error.json", {"error": f"{type(exc).__name__}:{exc}"})

    # Capital-market PR snapshots for full-market breadth and corporate-action flags.
    try:
        import subprocess
        report_dir = RAW / "daily_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        sig = ROOT / "research_artifacts" / "phase2" / "signal_table.csv"
        dates = pd.read_csv(sig, usecols=["signal_date"])["signal_date"].dropna().unique().tolist() if sig.exists() else []
        fresh = pd.date_range(dt.date(2026, 5, 20), END, freq="W-TUE").strftime("%Y-%m-%d").tolist()
        dates = sorted(set(dates + fresh))
        for d in dates:
            for typ, prefix in [("pr","pr"),("corp_actions","bc")]:
                target = report_dir / f"{prefix}_{d}.csv"
                if target.exists():
                    continue
                try:
                    subprocess.run(
                        ["nse-data","reports","--type",typ,"--date",d],
                        cwd=report_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                    )
                    candidates = sorted(report_dir.glob(f"{prefix}*"))
                    if candidates:
                        candidates[-1].replace(target)
                    else:
                        subprocess.run(
                            ["nse-data","get","equities",typ,d],
                            cwd=report_dir, stdout=target.open("wb"),
                            stderr=subprocess.DEVNULL, check=True
                        )
                except Exception:
                    (report_dir / f"{prefix}_{d}.missing").touch()
    except Exception as exc:
        save_json(RAW / "nse_equity_report_error.json", {"error": f"{type(exc).__name__}:{exc}"})

if __name__ == "__main__":
    main()
