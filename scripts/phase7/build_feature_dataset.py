from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data_cache" / "phase7"
OUT = ROOT / "research_artifacts" / "phase7"
OUT.mkdir(parents=True, exist_ok=True)
CUTOFF = dt.date(2026, 5, 19)

def add_returns(df):
    df=df.sort_values("source_timestamp").copy()
    px=pd.to_numeric(df["Close"],errors="coerce")
    df["ret_1d"]=np.log(px/px.shift(1))
    df["rv_5d"]=df["ret_1d"].rolling(5).std()*np.sqrt(252)
    df["rv_20d"]=df["ret_1d"].rolling(20).std()*np.sqrt(252)
    df["rv_60d"]=df["ret_1d"].rolling(60).std()*np.sqrt(252)
    return df

def main():
    frames={}
    for name in ["nifty","sp500","nasdaq","vix","usd_inr","brent","gold"]:
        p=RAW/f"{name}.parquet"
        if p.exists(): frames[name]=add_returns(pd.read_parquet(p))
    if "sp500" not in frames: raise SystemExit("No global source acquired.")
    base=frames["nifty"][["source_timestamp","ret_1d"]].rename(columns={"ret_1d":"nifty_ret_1d"}) if "nifty" in frames else frames["sp500"][["source_timestamp","ret_1d"]].rename(columns={"ret_1d":"sp500_ret_1d"})
    for name in ["nasdaq","vix","usd_inr","brent","gold"]:
        if name in frames:
            x=frames[name][["source_timestamp","ret_1d"]].rename(columns={"ret_1d":f"{name}_ret_1d"})
            base=base.merge(x,on="source_timestamp",how="outer")
    if "india_vix" in frames:
        pass
    base["signal_date"]=pd.to_datetime(base["source_timestamp"]).dt.date
    base["sample_status"]=np.where(base["signal_date"]<=CUTOFF,"development","fresh_untouched")
    base["availability_timestamp"]=base["source_timestamp"].astype(str)+" 23:59:59"
    base["feature_cutoff_timestamp"]=base["source_timestamp"].astype(str)+" 23:59:59"
    base.to_parquet(OUT/"new_information_set_global.parquet",index=False)
    summary={"status":"data_layer_in_progress","development_end":str(CUTOFF),
             "fresh_boundary":str(CUTOFF+dt.timedelta(days=1)),
             "fresh_rows_present":int((base["sample_status"]=="fresh_untouched").sum()),
             "performance_evaluation_run":False,"model_selection_run":False}
    (OUT/"data_layer_status.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")

if __name__=="__main__": main()
