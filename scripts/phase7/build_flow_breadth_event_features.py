from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data_cache" / "phase7"
OUT = ROOT / "research_artifacts" / "phase7"
CUTOFF = dt.date(2026, 5, 19)


def parse_flows():
    rows = []
    for p in sorted((RAW / "fii_dii_source" / "data").glob("*.json")):
        try:
            x = json.loads(p.read_text(encoding="utf-8"))
            e = x.get("equity", {})
            rows.append({
                "date": pd.to_datetime(x.get("date") or p.stem, errors="coerce").date(),
                "fii_net": float(e.get("fii_net", np.nan)),
                "dii_net": float(e.get("dii_net", np.nan)),
                "flow_source": x.get("source", "unknown"),
            })
        except Exception:
            continue
    df = pd.DataFrame(rows).dropna(subset=["date"]).drop_duplicates("date").sort_values("date")
    for col in ["fii_net", "dii_net"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[f"{col}_z20"] = (df[col] - df[col].rolling(20).mean()) / df[col].rolling(20).std()
        df[f"{col}_sum5"] = df[col].rolling(5).sum()
    return df


def read_pr(path):
    df = pd.read_csv(path)
    def col(names):
        for n in names:
            if n in df.columns:
                return n
        return None
    sym = col(["SYMBOL","TckrSymb"])
    series = col(["SERIES","SctySrs"])
    close = col(["CLOSE","ClsPric"])
    prev = col(["PREV_CLOSE","PrvsClsgPric"])
    if not all([sym, close, prev]):
        raise ValueError(f"unsupported PR schema {path.name}: {list(df.columns)[:20]}")
    if series:
        df = df[df[series].astype(str).str.upper().eq("EQ")]
    c = pd.to_numeric(df[close], errors="coerce")
    pc = pd.to_numeric(df[prev], errors="coerce")
    valid = pd.DataFrame({"c": c, "pc": pc}).dropna()
    adv = int((valid["c"] > valid["pc"]).sum())
    dec = int((valid["c"] < valid["pc"]).sum())
    unc = int((valid["c"] == valid["pc"]).sum())
    return adv, dec, unc


def count_corporate_actions(path):
    if not path.exists():
        return np.nan
    try:
        df = pd.read_csv(path)
        return int(len(df))
    except Exception:
        try:
            return int(sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore")))
        except Exception:
            return np.nan


def main():
    flow = parse_flows()
    pr_rows, ca_rows = [], []
    for p in sorted((RAW / "daily_reports").glob("pr_*.csv")):
        d = dt.date.fromisoformat(p.stem.replace("pr_", ""))
        try:
            a, dec, unc = read_pr(p)
            pr_rows.append({
                "date": d, "advances": a, "declines": dec, "unchanged": unc,
                "breadth_net": a-dec, "breadth_ratio": a/max(dec,1)
            })
        except Exception:
            continue
        ca_rows.append({"date": d, "corporate_action_rows": count_corporate_actions(
            RAW/"daily_reports"/f"bc_{d}.csv")})
    breadth = pd.DataFrame(pr_rows)
    if not breadth.empty:
        breadth = breadth.sort_values("date")
    if not breadth.empty:
        breadth["breadth_z20"] = (breadth["breadth_net"] - breadth["breadth_net"].rolling(20).mean()) / breadth["breadth_net"].rolling(20).std()
    ca = pd.DataFrame(ca_rows)
    if not ca.empty:
        ca = ca.drop_duplicates("date")
    # Signal-time safe alignment: use the last completed session strictly before the signal date.
    signal_dates = set()
    sig = ROOT / "research_artifacts" / "phase2" / "signal_table.csv"
    if sig.exists():
        signal_dates.update(pd.read_csv(sig, usecols=["signal_date"])["signal_date"].dropna().astype(str))
    signal_dates.update(pd.date_range(dt.date(2026,5,20), dt.date.today(), freq="W-TUE").strftime("%Y-%m-%d"))
    signals = pd.DataFrame({"signal_date": sorted(signal_dates)})
    signals["signal_date"] = pd.to_datetime(signals["signal_date"]).astype("datetime64[ns]").astype("datetime64[ns]")
    if not flow.empty:
        flow["date"] = pd.to_datetime(flow["date"]).astype("datetime64[ns]").astype("datetime64[ns]")
        signals = pd.merge_asof(signals.sort_values("signal_date"), flow.sort_values("date"),
                                left_on="signal_date", right_on="date", direction="backward",
                                allow_exact_matches=False)
    if not breadth.empty:
        breadth["date"] = pd.to_datetime(breadth["date"]).astype("datetime64[ns]").astype("datetime64[ns]")
        signals = pd.merge_asof(signals.sort_values("signal_date"), breadth.sort_values("date"),
                                left_on="signal_date", right_on="date", direction="backward",
                                allow_exact_matches=False)
    if not ca.empty:
        ca["date"] = pd.to_datetime(ca["date"]).astype("datetime64[ns]").astype("datetime64[ns]")
        signals = pd.merge_asof(signals.sort_values("signal_date"), ca.sort_values("date"),
                                left_on="signal_date", right_on="date", direction="backward",
                                allow_exact_matches=False)
    signals["sample_status"] = np.where(signals["signal_date"].dt.date <= CUTOFF, "development", "fresh_untouched")
    signals["flow_breadth_feature_lag"] = "strictly_prior_session"
    signals.to_parquet(OUT/"flow_breadth_event_features.parquet", index=False)
    coverage = {
        "signal_rows": int(len(signals)),
        "flow_rows": int(flow["date"].nunique()) if not flow.empty else 0,
        "breadth_rows": int(len(breadth)),
        "breadth_source_status": "available" if not breadth.empty else "unavailable_no_daily_pr_rows",
        "corporate_action_rows_available": int(ca["corporate_action_rows"].notna().sum()) if not ca.empty else 0,
        "fresh_rows": int((signals["sample_status"]=="fresh_untouched").sum()),
        "performance_evaluation_run": False,
        "model_selection_run": False,
        "status": "feature_inventory_only",
    }
    (OUT/"flow_breadth_event_status.json").write_text(json.dumps(coverage, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
