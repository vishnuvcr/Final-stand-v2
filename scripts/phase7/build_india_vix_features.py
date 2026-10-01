from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/"data_cache"/"phase7"
OUT=ROOT/"research_artifacts"/"phase7"
OUT.mkdir(parents=True,exist_ok=True)

def main():
    p=RAW/"india_vix.parquet"
    if not p.exists():
        raise SystemExit("india_vix.parquet missing")
    df=pd.read_parquet(p)
    dcol=next((c for c in ["Date","date","DATE","EOD_DATE"] if c in df.columns),None)
    ccol=next((c for c in ["Close","close","CLOSE","EOD_CLOSE"] if c in df.columns),None)
    if not dcol or not ccol:
        raise SystemExit(f"unrecognized India VIX schema: {list(df.columns)}")
    out=pd.DataFrame({"signal_date":pd.to_datetime(df[dcol],errors="coerce").dt.date,
                      "india_vix":pd.to_numeric(df[ccol],errors="coerce")}).dropna()
    out=out.sort_values("signal_date")
    out["india_vix_change"]=out["india_vix"].pct_change()
    out["india_vix_z20"]=(out["india_vix"]-out["india_vix"].rolling(20).mean())/out["india_vix"].rolling(20).std()
    out["india_vix_z60"]=(out["india_vix"]-out["india_vix"].rolling(60).mean())/out["india_vix"].rolling(60).std()
    out.to_parquet(OUT/"india_vix_features.parquet",index=False)
    (OUT/"india_vix_status.json").write_text(json.dumps({"rows":len(out),"performance_evaluation_run":False,"model_selection_run":False},indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
