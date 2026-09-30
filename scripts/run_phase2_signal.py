from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_access import ensure_dataset, load_index, option_files

OUT = Path("research_artifacts/phase2")
OUT.mkdir(parents=True, exist_ok=True)

CAL_WINDOW = 252
N_SIMS = 50_000
SEED = 20261001
TEST_START = dt.date(2022, 1, 1)


def daily_index(index: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = index.copy()
    work["trade_date"] = pd.to_datetime(work["trading_day"], errors="coerce").dt.date
    daily = (
        work.sort_values("timestamp")
        .drop_duplicates("trade_date", keep="last")
        [["trade_date", "close"]]
        .dropna()
        .sort_values("trade_date")
        .reset_index(drop=True)
    )
    at_10 = work[work["timestamp"].dt.strftime("%H:%M") == "10:00"].copy()
    at_10["trade_date"] = pd.to_datetime(at_10["trading_day"], errors="coerce").dt.date
    at_10 = (
        at_10.sort_values("timestamp")
        .drop_duplicates("trade_date", keep="first")
        [["trade_date", "open"]]
        .rename(columns={"open": "entry_spot"})
    )
    return daily, at_10


def expiry_dates() -> list[dt.date]:
    dates = []
    for p in option_files():
        try:
            d = dt.date.fromisoformat(p.stem)
        except ValueError:
            continue
        if d >= TEST_START:
            dates.append(d)
    return sorted(set(dates))


def run() -> None:
    meta = ensure_dataset(TEST_START)
    index = load_index()
    daily, at10 = daily_index(index)
    date_list = daily["trade_date"].tolist()
    date_pos = {d: i for i, d in enumerate(date_list)}
    closes = daily["close"].to_numpy(float)

    rows = []
    exps = expiry_dates()
    for i in range(1, len(exps)):
        expiry = exps[i]
        signal = exps[i - 1]
        if signal not in date_pos or expiry not in date_pos:
            continue
        signal_pos = date_pos[signal]
        expiry_pos = date_pos[expiry]
        if expiry_pos - signal_pos <= 0:
            continue
        if signal_pos < CAL_WINDOW:
            continue
        entry_pos = expiry_pos - 4
        if entry_pos < 0 or entry_pos <= signal_pos:
            continue
        entry_date = date_list[entry_pos]
        s0 = float(closes[signal_pos])
        terminal_actual = float(closes[expiry_pos])
        ret = np.log(closes[1:] / closes[:-1])
        hist = ret[signal_pos - CAL_WINDOW : signal_pos]
        mu = float(np.mean(hist))
        sigma = float(np.std(hist, ddof=1))
        if not np.isfinite(mu) or not np.isfinite(sigma) or sigma <= 0:
            continue
        horizon = expiry_pos - signal_pos
        rng = np.random.default_rng(SEED + i)
        z = rng.standard_normal(N_SIMS)
        terminals = s0 * np.exp((mu - 0.5 * sigma * sigma) * horizon + sigma * np.sqrt(horizon) * z)
        p_up = float(np.mean(terminals > s0))
        pred = "Bull" if p_up > 0.5 else "Bear"
        actual = "Bull" if terminal_actual > s0 else ("Bear" if terminal_actual < s0 else "Flat")
        entry_row = at10[at10["trade_date"] == entry_date]
        if entry_row.empty:
            continue
        entry_spot = float(entry_row.iloc[0]["entry_spot"])
        rows.append({
            "expiry": expiry.isoformat(),
            "signal_date": signal.isoformat(),
            "entry_date": entry_date.isoformat(),
            "signal_spot": s0,
            "entry_spot": entry_spot,
            "expiry_spot": terminal_actual,
            "realized_return": terminal_actual / s0 - 1.0,
            "log_mu_daily": mu,
            "sigma_daily": sigma,
            "horizon_trading_days": horizon,
            "p_up": p_up,
            "predicted_direction": pred,
            "actual_direction": actual,
            "signal_hit": int(pred == actual),
            "entry_spot_available": 1,
        })

    out = pd.DataFrame(rows).sort_values("expiry")
    out.to_csv(OUT / "signal_table.csv", index=False)
    summary = {
        "dataset": meta,
        "calibration_window": CAL_WINDOW,
        "simulations_per_signal": N_SIMS,
        "seed": SEED,
        "signals": int(len(out)),
        "hit_rate_excluding_flat": float(out.loc[out["actual_direction"] != "Flat", "signal_hit"].mean()) if not out.empty else None,
        "bull_fraction": float((out["predicted_direction"] == "Bull").mean()) if not out.empty else None,
        "actual_bull_fraction": float((out["actual_direction"] == "Bull").mean()) if not out.empty else None,
        "mean_p_up": float(out["p_up"].mean()) if not out.empty else None,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    (OUT / "summary.md").write_text(
        "# Phase 2 — Monte Carlo signal

"
        f"- Signals generated: {summary['signals']}\n"
        f"- Calibration: {CAL_WINDOW} daily log returns\n"
        f"- Simulations/signal: {N_SIMS}\n"
        f"- Direction rule: P(S_expiry > S_signal) > 0.5 => Bull; otherwise Bear\n"
        f"- Signal hit rate (excluding flat outcomes): {summary['hit_rate_excluding_flat']}\n"
        f"- Predicted Bull share: {summary['bull_fraction']}\n"
        f"- Actual Bull share: {summary['actual_bull_fraction']}\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()
