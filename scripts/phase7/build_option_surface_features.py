from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data_cache" / "phase7"
OPT = RAW / "nifty_option_eod"
OUT = ROOT / "research_artifacts" / "phase7"
OUT.mkdir(parents=True, exist_ok=True)

MONEYNESS = [0.95, 0.975, 1.0, 1.025, 1.05]
MIN_DAYS = 3
MAX_DAYS = 45


def norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black76_price(F, K, T, sigma, is_call):
    if T <= 0 or sigma <= 0 or F <= 0 or K <= 0:
        return max(F - K, 0.0) if is_call else max(K - F, 0.0)
    srt = sigma * math.sqrt(T)
    d1 = (math.log(F / K) + 0.5 * sigma * sigma * T) / srt
    d2 = d1 - srt
    if is_call:
        return F * norm_cdf(d1) - K * norm_cdf(d2)
    return K * norm_cdf(-d2) - F * norm_cdf(-d1)


def implied_vol(price, F, K, T, is_call):
    if not np.isfinite(price) or price <= 0 or F <= 0 or K <= 0 or T <= 0:
        return np.nan
    intrinsic = max(F - K, 0.0) if is_call else max(K - F, 0.0)
    upper = F if is_call else K
    if price < intrinsic - 1e-8 or price >= upper:
        return np.nan
    lo, hi = 1e-6, 5.0
    for _ in range(80):
        mid = (lo + hi) / 2
        val = black76_price(F, K, T, mid, is_call)
        if val > price:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def pick_col(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None


def read_option_file(path):
    df = pd.read_csv(path)
    aliases = {
        "instrument": ["INSTRUMENT", "FinInstrmTp"],
        "symbol": ["SYMBOL", "TckrSymb"],
        "expiry": ["EXPIRY_DT", "XpryDt"],
        "strike": ["STRIKE_PR", "StrkPric"],
        "otype": ["OPTION_TYP", "OptnTp"],
        "close": ["CLOSE", "ClsPric"],
        "volume": ["CONTRACTS", "TtlTradgVol"],
        "oi": ["OPEN_INT", "OpnIntrst"],
    }
    cols = {k: pick_col(df, v) for k, v in aliases.items()}
    if not all(cols[k] for k in ["symbol", "expiry", "strike", "otype", "close", "volume", "oi"]):
        raise ValueError(f"unrecognized option schema: {path.name}: {list(df.columns)[:20]}")
    out = pd.DataFrame({
        "symbol": df[cols["symbol"]].astype(str).str.strip(),
        "expiry": pd.to_datetime(df[cols["expiry"]], errors="coerce", dayfirst=True),
        "strike": pd.to_numeric(df[cols["strike"]], errors="coerce"),
        "otype": df[cols["otype"]].astype(str).str.upper().str.strip(),
        "close": pd.to_numeric(df[cols["close"]], errors="coerce"),
        "volume": pd.to_numeric(df[cols["volume"]], errors="coerce"),
        "oi": pd.to_numeric(df[cols["oi"]], errors="coerce"),
    })
    out = out[(out["symbol"].str.upper() == "NIFTY") & out["otype"].isin(["CE", "PE"])]
    return out.dropna(subset=["expiry", "strike", "close"])


def nearest_value(df, target):
    if df.empty:
        return None
    idx = (df["strike"] - target).abs().idxmin()
    return df.loc[idx]


def main():
    spot_path = RAW / "nifty.parquet"
    if not spot_path.exists():
        raise SystemExit("nifty.parquet missing")
    spot = pd.read_parquet(spot_path)
    date_col = "source_timestamp"
    spot[date_col] = pd.to_datetime(spot[date_col]).dt.date
    spot_px = pd.to_numeric(spot["Close"], errors="coerce")
    spot_map = dict(zip(spot[date_col], spot_px))

    rows, errors = [], []
    for path in sorted(OPT.glob("optidx_*.csv")):
        try:
            signal_date = dt.date.fromisoformat(path.stem.replace("optidx_", ""))
            S = float(spot_map.get(signal_date, np.nan))
            if not np.isfinite(S):
                errors.append({"signal_date": str(signal_date), "error": "missing_nifty_spot"})
                continue
            chain = read_option_file(path)
            expiries = sorted({x.date() for x in chain["expiry"].dropna()})
            expiries = [x for x in expiries if MIN_DAYS <= (x - signal_date).days <= MAX_DAYS]
            if not expiries:
                errors.append({"signal_date": str(signal_date), "error": "no_eligible_expiry"})
                continue
            selected = []
            for x in expiries:
                d = (x - signal_date).days
                if not selected or d != selected[-1][1]:
                    selected.append((x, d))
            # 1W = nearest eligible; 2W = second eligible if present; 1M = nearest >=21d.
            buckets = {"1w": selected[0][0]}
            if len(selected) >= 2:
                buckets["2w"] = selected[1][0]
            monthly = [x for x in selected if x[1] >= 21]
            if monthly:
                buckets["1m"] = monthly[0][0]

            for tenor, expiry in buckets.items():
                T = (expiry - signal_date).days / 365.25
                ch = chain[chain["expiry"].dt.date == expiry].copy()
                calls, puts = ch[ch["otype"] == "CE"], ch[ch["otype"] == "PE"]
                # Synthetic forward from call-put parity around spot, using a median across nearby strikes.
                pairs = calls.merge(puts, on="strike", suffixes=("_c", "_p"))
                pairs = pairs[(pairs["strike"] >= 0.98*S) & (pairs["strike"] <= 1.02*S)]
                pairs["forward"] = pairs["strike"] + pairs["close_c"] - pairs["close_p"]
                pairs = pairs[np.isfinite(pairs["forward"]) & (pairs["forward"] > 0)]
                F = float(pairs["forward"].median()) if not pairs.empty else S

                iv = {}
                oi = {}
                vol = {}
                for m in MONEYNESS:
                    target = F * m
                    c = nearest_value(calls, target)
                    p = nearest_value(puts, target)
                    if c is not None:
                        iv[f"ce_iv_{m:.3f}"] = implied_vol(float(c["close"]), F, float(c["strike"]), T, True)
                        oi[f"ce_oi_{m:.3f}"] = float(c["oi"])
                        vol[f"ce_vol_{m:.3f}"] = float(c["volume"])
                    if p is not None:
                        iv[f"pe_iv_{m:.3f}"] = implied_vol(float(p["close"]), F, float(p["strike"]), T, False)
                        oi[f"pe_oi_{m:.3f}"] = float(p["oi"])
                        vol[f"pe_vol_{m:.3f}"] = float(p["volume"])

                atm_ce, atm_pe = iv.get("ce_iv_1.000"), iv.get("pe_iv_1.000")
                atm = np.nanmean([atm_ce, atm_pe]) if any(np.isfinite(x) for x in [atm_ce, atm_pe]) else np.nan
                put_wing, call_wing = iv.get("pe_iv_0.950"), iv.get("ce_iv_1.050")
                row = {
                    "signal_date": str(signal_date), "expiry": str(expiry), "tenor": tenor,
                    "spot": S, "forward": F, "days_to_expiry": (expiry-signal_date).days,
                    "atm_iv": atm,
                    "put_call_skew_5pct": put_wing - call_wing if np.isfinite(put_wing) and np.isfinite(call_wing) else np.nan,
                    "iv_curvature_5pct": (np.nanmean([put_wing, call_wing]) - atm) if np.isfinite(atm) and np.isfinite(put_wing) and np.isfinite(call_wing) else np.nan,
                    "pcr_oi_5pct": np.nansum([oi.get(f"pe_oi_{m:.3f}", np.nan) for m in MONEYNESS]) / max(np.nansum([oi.get(f"ce_oi_{m:.3f}", np.nan) for m in MONEYNESS]), 1e-12),
                    "pcr_volume_5pct": np.nansum([vol.get(f"pe_vol_{m:.3f}", np.nan) for m in MONEYNESS]) / max(np.nansum([vol.get(f"ce_vol_{m:.3f}", np.nan) for m in MONEYNESS]), 1e-12),
                    "oi_total_5pct": np.nansum(list(oi.values())),
                    "volume_total_5pct": np.nansum(list(vol.values())),
                    "iv_method": "Black76_forward_from_ATM_call_put_parity_no_discount",
                }
                rows.append(row)
        except Exception as exc:
            errors.append({"signal_date": path.stem.replace("optidx_", ""), "error": f"{type(exc).__name__}:{exc}"})

    out = pd.DataFrame(rows)
    if out.empty:
        raise SystemExit("No option-surface rows built")
    wide = out.pivot(index="signal_date", columns="tenor")
    wide.columns = [f"{a}_{b}" for a,b in wide.columns]
    wide = wide.reset_index()
    for col in ["atm_iv_1w","atm_iv_2w","atm_iv_1m"]:
        if col not in wide: wide[col] = np.nan
    wide["iv_term_slope_2w_1w"] = wide["atm_iv_2w"] - wide["atm_iv_1w"]
    wide["iv_term_slope_1m_1w"] = wide["atm_iv_1m"] - wide["atm_iv_1w"]
    wide["sample_status"] = np.where(pd.to_datetime(wide["signal_date"]).dt.date <= dt.date(2026,5,19), "development", "fresh_untouched")
    wide.to_parquet(OUT/"option_surface_features.parquet", index=False)
    pd.DataFrame(errors).to_csv(OUT/"option_surface_errors.csv", index=False)
    summary = {
        "rows": int(len(wide)),
        "development_rows": int((wide["sample_status"]=="development").sum()),
        "fresh_rows": int((wide["sample_status"]=="fresh_untouched").sum()),
        "errors": len(errors),
        "performance_evaluation_run": False,
        "model_selection_run": False,
        "iv_method": "Black76_forward_from_ATM_call_put_parity_no_discount",
    }
    (OUT/"option_surface_status.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
