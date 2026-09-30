from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest, norm, ttest_1samp

from data_access import ensure_index, load_index

OUT = Path("research_artifacts/phase4")
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261001
BOOT = 10000


def max_drawdown(x: pd.Series) -> float:
    eq = x.cumsum()
    return float((eq - eq.cummax()).min())


def perf(x: pd.Series) -> dict:
    x = x.dropna()
    pos = x[x > 0].sum()
    neg = x[x < 0].sum()
    return {
        "n": int(len(x)),
        "wins": int((x > 0).sum()),
        "win_rate": float((x > 0).mean()) if len(x) else None,
        "total_pnl": float(x.sum()) if len(x) else None,
        "mean_pnl": float(x.mean()) if len(x) else None,
        "median_pnl": float(x.median()) if len(x) else None,
        "std_pnl": float(x.std(ddof=1)) if len(x) > 1 else None,
        "profit_factor": float(pos / abs(neg)) if neg < 0 else None,
        "max_drawdown": max_drawdown(x) if len(x) else None,
    }


def roc_auc_binary(y: np.ndarray, score: np.ndarray) -> float:
    pos = score[y == 1]
    neg = score[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    comparisons = (pos[:, None] > neg[None, :]).mean()
    ties = (pos[:, None] == neg[None, :]).mean()
    return float(comparisons + 0.5 * ties)

def bootstrap_mean(x: np.ndarray, seed: int = SEED) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(BOOT, len(x)))
    means = x[idx].mean(axis=1)
    return float(means.mean()), float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def daily_from_index() -> pd.DataFrame:
    ensure_index()
    idx = load_index()
    idx["trade_date"] = pd.to_datetime(idx["trading_day"]).dt.date
    d = (
        idx.sort_values("timestamp")
        .drop_duplicates("trade_date", keep="last")
        [["trade_date", "close"]]
        .sort_values("trade_date")
        .reset_index(drop=True)
    )
    d["logret"] = np.log(d["close"] / d["close"].shift(1))
    return d


def window_sensitivity(signal_dates: pd.DataFrame) -> pd.DataFrame:
    d = daily_from_index()
    dates = d["trade_date"].tolist()
    close = d["close"].to_numpy(float)
    pos = {v: i for i, v in enumerate(dates)}
    rows = []
    for w in [63, 252, 504]:
        for _, s in signal_dates.iterrows():
            sd = s["signal_date"]
            ed = s["expiry"]
            if sd not in pos or ed not in pos:
                continue
            i = pos[sd]
            j = pos[ed]
            if i < w:
                continue
            hist = d["logret"].iloc[i-w+1:i+1].dropna().to_numpy()
            # Equivalent terminal-up probability under the GBM baseline.
            mu = float(hist.mean())
            sig = float(hist.std(ddof=1))
            h = j - i
            if sig <= 0 or h <= 0:
                continue
            z = ((mu - 0.5 * sig * sig) * h) / (sig * np.sqrt(h))
            p_up = float(norm.cdf(z))
            pred = "Bull" if p_up > 0.5 else "Bear"
            actual = s["actual_direction"]
            rows.append({
                "window": w,
                "expiry": ed,
                "signal_date": sd,
                "p_up": p_up,
                "predicted": pred,
                "actual": actual,
                "hit": int(pred == actual) if actual in ("Bull", "Bear") else np.nan,
            })
    return pd.DataFrame(rows)


def main() -> None:
    ledger = pd.read_csv("research_artifacts/phase3/trade_ledger.csv")
    signals = pd.read_csv("research_artifacts/phase2/signal_table.csv")
    for df, cols in [(ledger, ["expiry","signal_date","entry_date"]), (signals, ["expiry","signal_date","entry_date"])]:
        for c in cols:
            df[c] = pd.to_datetime(df[c])

    pnl = ledger["settlement_1tick_cost_net_pnl"].to_numpy(float)
    summary = {
        "primary_performance": perf(pd.Series(pnl)),
        "bootstrap_mean": {},
    }

    mean_boot, lo_boot, hi_boot = bootstrap_mean(pnl)
    summary["bootstrap_mean"] = {"mean": mean_boot, "ci95_low": lo_boot, "ci95_high": hi_boot}
    summary["ttest_mean_vs_zero"] = {
        "t_stat": float(ttest_1samp(pnl, 0.0).statistic),
        "p_value": float(ttest_1samp(pnl, 0.0).pvalue),
    }

    wins = int((pnl > 0).sum())
    summary["win_rate_binomial_two_sided"] = {
        "wins": wins,
        "n": len(pnl),
        "p_value_vs_0_5": float(binomtest(wins, len(pnl), 0.5).pvalue),
    }

    # Chronological stability: fixed 70/30 split.
    cut = int(len(ledger) * 0.70)
    summary["chronological_split"] = {
        "train_period": perf(ledger.iloc[:cut]["settlement_1tick_cost_net_pnl"]),
        "test_period": perf(ledger.iloc[cut:]["settlement_1tick_cost_net_pnl"]),
        "split_index": cut,
    }

    # Expiry-regime split: Thursday weekly expiries before Sep-2025 vs Tuesday after.
    ledger["expiry_regime"] = np.where(
        ledger["expiry"] < pd.Timestamp("2025-09-02"),
        "legacy_Thursday_regime",
        "Tuesday_regime",
    )
    summary["expiry_regime"] = {
        k: perf(g["settlement_1tick_cost_net_pnl"])
        for k, g in ledger.groupby("expiry_regime")
    }

    # Direction split.
    summary["predicted_direction"] = {
        k: perf(g["settlement_1tick_cost_net_pnl"])
        for k, g in ledger.groupby("predicted_direction")
    }

    # Serial dependence in weekly P&L.
    summary["lag1_autocorrelation"] = float(pd.Series(pnl).autocorr(lag=1))
    summary["total_cost_burden"] = {
        "gross_pnl": float(ledger["settlement_1tick_cost_gross_pnl"].sum()),
        "slippage_cost": float(ledger["settlement_1tick_cost_slippage_cost"].sum()),
        "transaction_cost": float(ledger["settlement_1tick_cost_transaction_cost"].sum()),
        "net_pnl": float(ledger["settlement_1tick_cost_net_pnl"].sum()),
    }

    # Signal calibration and 252-window primary hit rate.
    signals["actual_binary"] = (signals["actual_direction"] == "Bull").astype(int)
    summary["signal_calibration"] = {
        "brier_score": float(np.mean((signals["p_up"] - signals["actual_binary"]) ** 2)),
        "auc": roc_auc_binary(signals["actual_binary"].to_numpy(int), signals["p_up"].to_numpy(float)),
        "hit_rate": float(signals.loc[signals["actual_direction"] != "Flat", "signal_hit"].mean()),
        "bull_predicted_share": float((signals["predicted_direction"] == "Bull").mean()),
        "bull_realized_share": float((signals["actual_direction"] == "Bull").mean()),
    }

    sens = window_sensitivity(signals)
    sens_summary = (
        sens.groupby("window")
        .agg(
            signals=("hit", "count"),
            hit_rate=("hit", "mean"),
            bull_share=("predicted", lambda x: float((x == "Bull").mean())),
            mean_p_up=("p_up", "mean"),
        )
        .reset_index()
    )
    sens_summary.to_csv(OUT / "mc_window_sensitivity.csv", index=False)

    yearly = ledger.assign(year=ledger["expiry"].dt.year).groupby("year")["settlement_1tick_cost_net_pnl"].agg(["count","sum","mean","median"]).reset_index()
    yearly.to_csv(OUT / "yearly_pnl.csv", index=False)

    regime = ledger.groupby("expiry_regime")["settlement_1tick_cost_net_pnl"].agg(["count","sum","mean","median"]).reset_index()
    regime.to_csv(OUT / "expiry_regime_pnl.csv", index=False)

    # Trade direction confusion and annual cumulative P&L.
    confusion = pd.crosstab(signals["predicted_direction"], signals["actual_direction"])
    confusion.to_csv(OUT / "signal_confusion.csv")

    ordered = ledger.sort_values("expiry").copy()
    ordered["cumulative_pnl"] = ordered["settlement_1tick_cost_net_pnl"].cumsum()
    ordered[["expiry","settlement_1tick_cost_net_pnl","cumulative_pnl"]].to_csv(OUT / "equity_curve.csv", index=False)

    plt.figure(figsize=(10, 5))
    plt.plot(ordered["expiry"], ordered["cumulative_pnl"])
    plt.axhline(0, linewidth=1)
    plt.title("Cumulative NIFTY strategy P&L — 65-unit normalization")
    plt.xlabel("Expiry")
    plt.ylabel("Cumulative P&L (₹)")
    plt.tight_layout()
    plt.savefig(OUT / "cumulative_pnl.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.bar(yearly["year"].astype(str), yearly["sum"])
    plt.title("Annual net P&L — primary cost/slippage scenario")
    plt.xlabel("Expiry year")
    plt.ylabel("Net P&L (₹)")
    plt.tight_layout()
    plt.savefig(OUT / "annual_pnl.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.hist(pnl, bins=20)
    plt.axvline(0, linewidth=1)
    plt.title("Weekly trade P&L distribution")
    plt.xlabel("Net P&L per trade (₹)")
    plt.ylabel("Trades")
    plt.tight_layout()
    plt.savefig(OUT / "pnl_distribution.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.scatter(signals["p_up"], signals["actual_binary"], alpha=0.55)
    plt.axvline(0.5, linewidth=1)
    plt.yticks([0, 1], ["Bear", "Bull"])
    plt.title("Monte Carlo terminal-up probability vs realized direction")
    plt.xlabel("P(NIFTY expiry > signal spot)")
    plt.ylabel("Realized direction")
    plt.tight_layout()
    plt.savefig(OUT / "signal_probability.png", dpi=180)
    plt.close()

    summary["mc_window_sensitivity"] = sens_summary.to_dict(orient="records")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float))

    lines = [
        "# Phase 4 — Statistics and Robustness",
        "",
        "## Primary P&L",
        *[f"- {k.replace('_',' ').title()}: {v}" for k, v in summary["primary_performance"].items()],
        f"- Bootstrap mean P&L 95% CI: [{lo_boot:.2f}, {hi_boot:.2f}]",
        f"- Mean P&L t-test p-value vs 0: {summary['ttest_mean_vs_zero']['p_value']:.6g}",
        f"- Win-rate binomial p-value vs 50%: {summary['win_rate_binomial_two_sided']['p_value_vs_0_5']:.6g}",
        f"- Lag-1 P&L autocorrelation: {summary['lag1_autocorrelation']:.4f}",
        "",
        "## Signal quality",
        f"- Hit rate: {summary['signal_calibration']['hit_rate']:.4f}",
        f"- Brier score: {summary['signal_calibration']['brier_score']:.4f}",
        f"- AUC: {summary['signal_calibration']['auc']:.4f}",
        "",
        "## MC calibration-window sensitivity",
        "| Window | Signals | Hit rate | Bull share | Mean P(up) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in summary["mc_window_sensitivity"]:
        lines.append(f"| {row['window']} | {row['signals']} | {row['hit_rate']:.4f} | {row['bull_share']:.4f} | {row['mean_p_up']:.4f} |")
    lines += [
        "",
        "## Robustness splits",
        "### Chronological 70/30",
        f"- First 70% total P&L: {summary['chronological_split']['train_period']['total_pnl']:.2f}",
        f"- Last 30% total P&L: {summary['chronological_split']['test_period']['total_pnl']:.2f}",
        f"- First 70% win rate: {summary['chronological_split']['train_period']['win_rate']:.4f}",
        f"- Last 30% win rate: {summary['chronological_split']['test_period']['win_rate']:.4f}",
        "",
        "### Expiry-regime split",
        "| Regime | Trades | Total P&L | Mean P&L | Win rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, v in summary["expiry_regime"].items():
        lines.append(f"| {k} | {v['n']} | {v['total_pnl']:.2f} | {v['mean_pnl']:.2f} | {v['win_rate']:.4f} |")
    lines += [
        "",
        "## Cost burden",
        f"- Gross P&L: {summary['total_cost_burden']['gross_pnl']:.2f}",
        f"- Slippage cost: {summary['total_cost_burden']['slippage_cost']:.2f}",
        f"- Transaction/statutory cost: {summary['total_cost_burden']['transaction_cost']:.2f}",
        f"- Net P&L: {summary['total_cost_burden']['net_pnl']:.2f}",
    ]
    (OUT / "summary.md").write_text("\\n".join(lines) + "\\n")


if __name__ == "__main__":
    main()
