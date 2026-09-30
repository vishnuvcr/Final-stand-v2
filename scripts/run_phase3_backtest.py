from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from data_access import DATA_ROOT, ensure_dataset

IST = ZoneInfo("Asia/Kolkata")
OUT = Path("research_artifacts/phase3")
OUT.mkdir(parents=True, exist_ok=True)

QTY = 65
ENTRY_TIME = time(10, 0)
ENTRY_LOOKBACK_MIN = 5
EXIT_CUTOFF_TIME = time(15, 30)
EXIT_MAX_STALE_MIN = 30
TICK = 0.05

BROKERAGE_PER_ORDER = 20.0
ORDERS_PER_ROUND_TRIP = 6
NSE_TX_PER_RUPEE = 3553.0 / 1e7
SEBI_PER_RUPEE = 10.0 / 1e7
GST_RATE = 0.18
STAMP_RATE = 0.00003
STT_BEFORE_2026_04_01 = 0.0010
STT_FROM_2026_04_01 = 0.0015


def load_signals() -> pd.DataFrame:
    p = Path("research_artifacts/phase2/signal_table.csv")
    df = pd.read_csv(p)
    for c in ["expiry", "signal_date", "entry_date"]:
        df[c] = pd.to_datetime(df[c]).dt.date
    return df.sort_values("expiry").reset_index(drop=True)


def option_path(expiry: date) -> Path:
    return DATA_ROOT / "options" / "NIFTY" / f"{expiry.isoformat()}.parquet"


def load_strikes(expiry: date) -> list[float]:
    p = option_path(expiry)
    if not p.exists():
        raise FileNotFoundError(p)
    s = pd.read_parquet(p, columns=["strike"])["strike"]
    return sorted(pd.to_numeric(s, errors="coerce").dropna().unique().tolist())

def load_option_quotes(expiry: date, entry_date: date, strikes: list[float], option_type: str) -> pd.DataFrame:
    p = option_path(expiry)
    filters = [
        ("trading_day", "in", [entry_date.isoformat(), expiry.isoformat()]),
        ("strike", "in", strikes),
        ("option_type", "=", option_type),
    ]
    use = ["timestamp", "open", "close", "strike", "option_type", "trading_day"]
    df = pd.read_parquet(p, columns=use, filters=filters)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["trading_day"] = pd.to_datetime(df["trading_day"]).dt.date
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
    df["option_type"] = df["option_type"].astype(str).str.upper()
    return df.dropna(subset=["timestamp", "strike", "option_type", "close"]).sort_values("timestamp")


def infer_strike_step(strikes: list[float]) -> float:
    vals = sorted(set(float(x) for x in strikes))
    diffs = [round(b - a, 8) for a, b in zip(vals[:-1], vals[1:]) if b > a]
    return float(Counter(diffs).most_common(1)[0][0]) if diffs else 50.0


def pick_atm(all_strikes: list[float], spot: float) -> float:
    return min(sorted(set(all_strikes)), key=lambda x: (abs(x - spot), x))


def entry_quote(df: pd.DataFrame, entry_date: date, strike: float, option_type: str) -> dict | None:
    x = df[(df["trading_day"] == entry_date) & (df["strike"] == strike) & (df["option_type"] == option_type)]
    if x.empty:
        return None
    target = datetime.combine(entry_date, ENTRY_TIME, tzinfo=IST)
    x = x[x["timestamp"] <= target]
    if x.empty:
        return None
    row = x.iloc[-1]
    stale = (target - row["timestamp"]).total_seconds()
    if stale < 0 or stale > ENTRY_LOOKBACK_MIN * 60:
        return None
    if row["timestamp"].time() == ENTRY_TIME and np.isfinite(row["open"]):
        return {"price": float(row["open"]), "timestamp": row["timestamp"], "stale_seconds": stale, "method": "10:00_open"}
    return {"price": float(row["close"]), "timestamp": row["timestamp"], "stale_seconds": stale, "method": "pre10_close"}


def exit_quote(df: pd.DataFrame, expiry: date, strike: float, option_type: str, intrinsic_value: float) -> dict:
    x = df[(df["trading_day"] == expiry) & (df["strike"] == strike) & (df["option_type"] == option_type)]
    if x.empty:
        return {"price": float(intrinsic_value), "timestamp": pd.NaT, "stale_seconds": None, "method": "intrinsic_fallback"}
    cutoff = datetime.combine(expiry, EXIT_CUTOFF_TIME, tzinfo=IST)
    x = x[x["timestamp"] <= cutoff]
    if x.empty:
        return {"price": float(intrinsic_value), "timestamp": pd.NaT, "stale_seconds": None, "method": "intrinsic_fallback"}
    row = x.iloc[-1]
    stale = (cutoff - row["timestamp"]).total_seconds()
    if stale > EXIT_MAX_STALE_MIN * 60:
        return {"price": float(intrinsic_value), "timestamp": pd.NaT, "stale_seconds": stale, "method": "intrinsic_fallback"}
    return {"price": float(row["close"]), "timestamp": row["timestamp"], "stale_seconds": stale, "method": "market_last"}


def intrinsic(option_type: str, strike: float, spot: float) -> float:
    return max(strike - spot, 0.0) if option_type == "PE" else max(spot - strike, 0.0)


def stt_rate(exit_date: date) -> float:
    return STT_FROM_2026_04_01 if exit_date >= date(2026, 4, 1) else STT_BEFORE_2026_04_01


def exec_prices(entry_raw: float, exit_raw: float, position: int, slippage_ticks: int, exit_is_market: bool) -> tuple[float, float, float]:
    slip = TICK * slippage_ticks
    if position > 0:
        entry_exec = max(entry_raw + slip, 0.0)
        exit_exec = max(exit_raw - slip, 0.0) if exit_is_market else max(exit_raw, 0.0)
    else:
        entry_exec = max(entry_raw - slip, TICK)
        exit_exec = max(exit_raw + slip, 0.0) if exit_is_market else max(exit_raw, 0.0)
    slip_cost_points = abs(entry_exec - entry_raw) + (abs(exit_exec - exit_raw) if exit_is_market else 0.0)
    return entry_exec, exit_exec, slip_cost_points


def scenario_costs(legs: list[dict], exit_date: date, qty: int, slippage_ticks: int, market_exit: bool, apply_costs: bool) -> dict:
    buy_turnover = sell_turnover = gross = slip_cost = 0.0
    for leg in legs:
        pos = int(leg["position"])
        eraw = float(leg["entry_raw"])
        xraw = float(leg["exit_raw_market"] if market_exit else leg["exit_raw_intrinsic"])
        entry_exec, exit_exec, leg_slip = exec_prices(eraw, xraw, pos, slippage_ticks, market_exit)
        gross += pos * (exit_exec - entry_exec) * qty
        slip_cost += leg_slip * qty
        entry_value = entry_exec * qty
        exit_value = exit_exec * qty
        if pos > 0:
            buy_turnover += entry_value
            sell_turnover += exit_value
        else:
            sell_turnover += entry_value
            buy_turnover += exit_value
    total_turnover = buy_turnover + sell_turnover
    if not apply_costs:
        detail = {"brokerage": 0.0, "nse_transaction": 0.0, "stt": 0.0, "stamp": 0.0, "sebi": 0.0, "gst": 0.0}
        costs = 0.0
    else:
        brokerage = BROKERAGE_PER_ORDER * ORDERS_PER_ROUND_TRIP
        nse_tx = total_turnover * NSE_TX_PER_RUPEE
        stt = sell_turnover * stt_rate(exit_date)
        stamp = buy_turnover * STAMP_RATE
        sebi = total_turnover * SEBI_PER_RUPEE
        gst = GST_RATE * (brokerage + nse_tx + sebi)
        detail = {"brokerage": brokerage, "nse_transaction": nse_tx, "stt": stt, "stamp": stamp, "sebi": sebi, "gst": gst}
        costs = brokerage + nse_tx + stt + stamp + sebi + gst
    return {
        "gross_pnl": gross,
        "slippage_cost": slip_cost,
        "transaction_cost": costs,
        "net_pnl": gross - costs,
        "buy_turnover": buy_turnover,
        "sell_turnover": sell_turnover,
        **detail,
    }


def max_drawdown(vals: pd.Series) -> float:
    eq = vals.cumsum()
    return float((eq - eq.cummax()).min()) if not eq.empty else 0.0


def summarize(df: pd.DataFrame, col: str) -> dict:
    x = df[col].dropna()
    gains = x[x > 0].sum()
    losses = x[x < 0].sum()
    return {
        "trades": int(x.size),
        "wins": int((x > 0).sum()),
        "losses": int((x < 0).sum()),
        "win_rate": float((x > 0).mean()) if len(x) else None,
        "total_pnl": float(x.sum()) if len(x) else None,
        "avg_pnl": float(x.mean()) if len(x) else None,
        "median_pnl": float(x.median()) if len(x) else None,
        "profit_factor": float(gains / abs(losses)) if losses < 0 else None,
        "max_drawdown": max_drawdown(x) if len(x) else None,
        "best_trade": float(x.max()) if len(x) else None,
        "worst_trade": float(x.min()) if len(x) else None,
    }


def main() -> None:
    signals = load_signals()
    required_expiries = sorted(set(signals["expiry"]))
    ensure_dataset(min(required_expiries))

    rows = []
    missing = []
    for _, s in signals.iterrows():
        exp = s["expiry"]
        try:
            all_strikes = load_strikes(exp)
            step = infer_strike_step(all_strikes)
            atm = pick_atm(all_strikes, float(s["entry_spot"]))
            side = "PE" if s["predicted_direction"] == "Bull" else "CE"
            strikes = (
                {"OTM4": atm - 4 * step, "OTM5": atm - 5 * step, "OTM6": atm - 6 * step}
                if side == "PE"
                else {"OTM4": atm + 4 * step, "OTM5": atm + 5 * step, "OTM6": atm + 6 * step}
            )
            all_strike_set = set(all_strikes)
            if not all(k in all_strike_set for k in strikes.values()):
                raise ValueError(f"required strike absent: ATM={atm}, step={step}, strikes={strikes}")

            opt = load_option_quotes(exp, s["entry_date"], list(strikes.values()), side)
            legs = []
            for label, pos in {"OTM4": 1, "OTM5": -1, "OTM6": -1}.items():
                strike = float(strikes[label])
                q = entry_quote(opt, s["entry_date"], strike, side)
                if q is None:
                    raise ValueError(f"missing entry quote: {label} {strike} {side}")
                intr = intrinsic(side, strike, float(s["expiry_spot"]))
                xq = exit_quote(opt, exp, strike, side, intr)
                legs.append({
                    "label": label,
                    "position": pos,
                    "strike": strike,
                    "option_type": side,
                    "entry_raw": q["price"],
                    "entry_timestamp": str(q["timestamp"]),
                    "entry_stale_seconds": q["stale_seconds"],
                    "entry_method": q["method"],
                    "exit_raw_market": xq["price"],
                    "exit_timestamp": str(xq["timestamp"]) if pd.notna(xq["timestamp"]) else None,
                    "exit_stale_seconds": xq["stale_seconds"],
                    "exit_method": xq["method"],
                    "exit_raw_intrinsic": intr,
                })

            base = {
                "expiry": exp.isoformat(),
                "signal_date": s["signal_date"].isoformat(),
                "entry_date": s["entry_date"].isoformat(),
                "predicted_direction": s["predicted_direction"],
                "actual_direction": s["actual_direction"],
                "signal_spot": float(s["signal_spot"]),
                "entry_spot": float(s["entry_spot"]),
                "expiry_spot": float(s["expiry_spot"]),
                "atm": atm,
                "strike_step": step,
                "side": side,
                "otm4_strike": strikes["OTM4"],
                "otm5_strike": strikes["OTM5"],
                "otm6_strike": strikes["OTM6"],
                "exit_method_otm4": legs[0]["exit_method"],
                "exit_method_otm5": legs[1]["exit_method"],
                "exit_method_otm6": legs[2]["exit_method"],
            }
            for scenario_name, slip_ticks, market_exit, apply_costs in [
                ("settlement_1tick_cost", 1, False, True),
                ("marketexit_1tick_cost", 1, True, True),
                ("settlement_2tick_cost", 2, False, True),
                ("settlement_zero_cost", 0, False, False),
            ]:
                c = scenario_costs(legs, exp, QTY, slip_ticks, market_exit, apply_costs)
                for k, v in c.items():
                    base[f"{scenario_name}_{k}"] = v
            rows.append(base)
        except Exception as exc:
            missing.append({"expiry": exp.isoformat(), "reason": "trade_unavailable", "detail": repr(exc)})

    trades = pd.DataFrame(rows).sort_values("expiry").reset_index(drop=True)
    miss = pd.DataFrame(missing)
    trades.to_csv(OUT / "trade_ledger.csv", index=False)
    miss.to_csv(OUT / "missing_trades.csv", index=False)

    summary = {
        "signals": int(len(signals)),
        "valid_trades": int(len(trades)),
        "missing_trades": int(len(signals) - len(trades)),
        "coverage": float(len(trades) / len(signals)) if len(signals) else None,
        "quantity_normalization": QTY,
        "entry_rule": "10:00 IST open if exact bar; otherwise latest <=10:00 within 5 minutes using close",
        "primary_exit": "expiry intrinsic value using NIFTY expiry close",
        "market_exit_diagnostic": "last option print by 15:30 if <=30 minutes stale; otherwise intrinsic fallback",
        "primary": summarize(trades, "settlement_1tick_cost_net_pnl") if len(trades) else {},
        "market_exit": summarize(trades, "marketexit_1tick_cost_net_pnl") if len(trades) else {},
        "two_tick": summarize(trades, "settlement_2tick_cost_net_pnl") if len(trades) else {},
        "zero_cost": summarize(trades, "settlement_zero_cost_net_pnl") if len(trades) else {},
        "by_prediction": trades.groupby("predicted_direction")["settlement_1tick_cost_net_pnl"].agg(["count","sum","mean","median"]).round(4).to_dict() if len(trades) else {},
        "by_year": trades.assign(year=trades["expiry"].str[:4]).groupby("year")["settlement_1tick_cost_net_pnl"].agg(["count","sum","mean"]).round(4).to_dict() if len(trades) else {},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    lines = [
        "# Phase 3 — Strategy Backtest",
        "",
        f"- Monte Carlo signals: {summary['signals']}",
        f"- Valid option trades: {summary['valid_trades']}",
        f"- Coverage: {summary['coverage']}",
        f"- Primary normalized quantity: {QTY} NIFTY units",
        "",
        "## Primary: settlement + current-cost proxy + 1-tick slippage",
    ]
    lines += [f"- {k.replace('_',' ').title()}: {v}" for k, v in summary["primary"].items()]
    lines += ["", "## Diagnostic: market exit on expiry"]
    lines += [f"- {k.replace('_',' ').title()}: {v}" for k, v in summary["market_exit"].items()]
    lines += ["", "## Sensitivities",
              f"- 2-tick settlement total P&L: {summary['two_tick'].get('total_pnl')}",
              f"- Zero-cost settlement total P&L: {summary['zero_cost'].get('total_pnl')}"]
    (OUT / "summary.md").write_text("\\n".join(lines) + "\\n")


if __name__ == "__main__":
    main()
