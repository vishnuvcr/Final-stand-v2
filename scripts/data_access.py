from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, snapshot_download

HF_REPO = "thetrademarkk/india-index-options-1m"
DATA_ROOT = Path("data_cache/hf_nifty")
MIN_EXPIRY = dt.date(2022, 1, 1)


def ensure_dataset(min_expiry: dt.date = MIN_EXPIRY) -> dict:
    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token)
    info = api.repo_info(HF_REPO, repo_type="dataset")
    files = api.list_repo_files(HF_REPO, repo_type="dataset")
    option_paths = []
    expiry_dates = []
    for p in files:
        if not (p.startswith("options/NIFTY/") and p.endswith(".parquet")):
            continue
        stem = Path(p).stem
        try:
            expiry = dt.date.fromisoformat(stem)
        except ValueError:
            continue
        if expiry >= min_expiry:
            option_paths.append(p)
            expiry_dates.append(expiry)
    option_paths.sort()
    patterns = ["index/NIFTY.parquet"] + option_paths
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=HF_REPO,
        repo_type="dataset",
        local_dir=str(DATA_ROOT),
        allow_patterns=patterns,
        token=token,
        max_workers=8,
    )
    return {
        "repo": HF_REPO,
        "revision": getattr(info, "sha", None),
        "option_files": len(option_paths),
        "min_expiry": min(expiry_dates).isoformat() if expiry_dates else None,
        "max_expiry": max(expiry_dates).isoformat() if expiry_dates else None,
        "root": str(DATA_ROOT),
    }


def ensure_index() -> None:
    token = os.environ.get("HF_TOKEN")
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=HF_REPO,
        repo_type="dataset",
        local_dir=str(DATA_ROOT),
        allow_patterns=["index/NIFTY.parquet"],
        token=token,
        max_workers=2,
    )

def load_index() -> pd.DataFrame:
    path = DATA_ROOT / "index" / "NIFTY.parquet"
    df = pd.read_parquet(path)
    if "timestamp" not in df.columns:
        raise ValueError("NIFTY index file lacks timestamp")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def option_files() -> list[Path]:
    return sorted((DATA_ROOT / "options" / "NIFTY").glob("*.parquet"))
