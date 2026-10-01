from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, snapshot_download

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"data_cache"/"phase7"
HF_ROOT=RAW/"hf_nifty"
REPO="thetrademarkk/india-index-options-1m"
CUTOFF=dt.date(2026,5,19)

def signal_dates():
    sig=ROOT/"research_artifacts"/"phase2"/"signal_table.csv"
    dates=pd.read_csv(sig,usecols=["signal_date"])["signal_date"].dropna().astype(str).tolist() if sig.exists() else []
    dates += pd.date_range(dt.date(2026,5,20),dt.date.today(),freq="W-TUE").strftime("%Y-%m-%d").tolist()
    return sorted(set(dt.date.fromisoformat(x) for x in dates))

def main():
    token=os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN is required for the Hugging Face option cache")
    api=HfApi(token=token)
    info=api.repo_info(REPO,repo_type="dataset")
    files=api.list_repo_files(REPO,repo_type="dataset")
    expiries=[]
    for p in files:
        if p.startswith("options/NIFTY/") and p.endswith(".parquet"):
            try:
                expiries.append(dt.date.fromisoformat(Path(p).stem))
            except ValueError:
                pass
    expiries=sorted(set(expiries))
    required=set()
    for d in signal_dates():
        required.update(x for x in expiries if 3 <= (x-d).days <= 45)
    patterns=["index/NIFTY.parquet"]+[f"options/NIFTY/{x.isoformat()}.parquet" for x in sorted(required)]
    HF_ROOT.mkdir(parents=True,exist_ok=True)
    snapshot_download(repo_id=REPO,repo_type="dataset",local_dir=str(HF_ROOT),
                       allow_patterns=patterns,token=token,max_workers=8)
    status={
        "repo":REPO,"revision":getattr(info,"sha",None),
        "required_expiry_files":len(required),
        "available_expiry_files":len(expiries),
        "signal_dates":len(signal_dates()),
        "performance_evaluation_run":False,"model_selection_run":False
    }
    (RAW/"hf_option_status.json").write_text(json.dumps(status,indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
