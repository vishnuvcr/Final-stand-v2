from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
HF=ROOT/"data_cache"/"phase7"/"hf_nifty"
OUT=ROOT/"research_artifacts"/"phase7"
MONEYNESS=[0.95,0.975,1.0,1.025,1.05]
CUTOFF=dt.date(2026,5,19)

def cdf(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

def b76(F,K,T,s,is_call):
    if T<=0 or s<=0: return max(F-K,0) if is_call else max(K-F,0)
    q=s*math.sqrt(T); d1=(math.log(F/K)+0.5*s*s*T)/q; d2=d1-q
    return F*cdf(d1)-K*cdf(d2) if is_call else K*cdf(-d2)-F*cdf(-d1)

def iv(price,F,K,T,is_call):
    intrinsic=max(F-K,0) if is_call else max(K-F,0)
    if not np.isfinite(price) or price<=intrinsic or F<=0 or K<=0 or T<=0: return np.nan
    lo,hi=1e-6,5.0
    for _ in range(80):
        m=(lo+hi)/2
        if b76(F,K,T,m,is_call)>price: hi=m
        else: lo=m
    return (lo+hi)/2

def pick(df,target):
    if df.empty: return None
    return df.iloc[(df["strike"]-target).abs().argmin()]

def normalize(df):
    aliases={
      "timestamp":["timestamp","datetime","date"],
      "strike":["strike","strike_price","strikePrice"],
      "otype":["option_type","optionType","type"],
      "close":["close","Close","c"],
      "oi":["open_interest","oi","Open Interest"],
      "volume":["volume","Volume","vol"],
    }
    cols={}
    for k,v in aliases.items():
        cols[k]=next((x for x in v if x in df.columns),None)
    if not all(cols.values()): raise ValueError(f"HF option schema: {list(df.columns)}")
    out=pd.DataFrame({k:df[v] for k,v in cols.items()})
    out["timestamp"]=pd.to_datetime(out["timestamp"],errors="coerce")
    out["strike"]=pd.to_numeric(out["strike"],errors="coerce")
    out["close"]=pd.to_numeric(out["close"],errors="coerce")
    out["oi"]=pd.to_numeric(out["oi"],errors="coerce")
    out["volume"]=pd.to_numeric(out["volume"],errors="coerce")
    out["otype"]=out["otype"].astype(str).str.upper()
    return out.dropna(subset=["timestamp","strike","close"])

def spot_map():
    p=HF/"index"/"NIFTY.parquet"
    df=pd.read_parquet(p)
    t=pd.to_datetime(df["timestamp"],errors="coerce")
    price=pd.to_numeric(df["close"] if "close" in df.columns else df["Close"],errors="coerce")
    x=pd.DataFrame({"timestamp":t,"spot":price}).dropna().sort_values("timestamp")
    return x

def signal_dates():
    sig=ROOT/"research_artifacts"/"phase2"/"signal_table.csv"
    d=pd.read_csv(sig,usecols=["signal_date"])["signal_date"].dropna().astype(str).tolist() if sig.exists() else []
    d += pd.date_range(dt.date(2026,5,20),dt.date.today(),freq="W-TUE").strftime("%Y-%m-%d").tolist()
    return sorted(set(dt.date.fromisoformat(x) for x in d))

def main():
    files=sorted((HF/"options"/"NIFTY").glob("*.parquet"))
    expiry_files={}
    for p in files:
        try: expiry_files[dt.date.fromisoformat(p.stem)]=p
        except ValueError: continue
    spots=spot_map()
    rows=[]; errors=[]
    for d in signal_dates():
        srow=spots[spots["timestamp"]<=pd.Timestamp(f"{d} 15:30:00")].tail(1)
        if srow.empty:
            errors.append({"signal_date":str(d),"error":"missing_spot"}); continue
        S=float(srow.iloc[0]["spot"])
        exps=sorted(x for x in expiry_files if 3 <= (x-d).days <= 45)
        if not exps:
            errors.append({"signal_date":str(d),"error":"no_hf_expiry_files"}); continue
        selected=[exps[0]]
        if len(exps)>1: selected.append(exps[1])
        month=[x for x in exps if (x-d).days>=21]
        if month and month[0] not in selected: selected.append(month[0])
        for tenor,expiry in zip(["1w","2w","1m"],selected):
            try:
                df=normalize(pd.read_parquet(expiry_files[expiry]))
                cutoff=pd.Timestamp(f"{d} 15:30:00")
                day=df[(df["timestamp"]<=cutoff)&(df["timestamp"].dt.date==d)].copy()
                if day.empty: raise ValueError("no option bars before signal cutoff")
                tstamp=day["timestamp"].max()
                day=day[day["timestamp"]==tstamp]
                calls=day[day["otype"].isin(["CE","CALL"])]
                puts=day[day["otype"].isin(["PE","PUT"])]
                pairs=calls.merge(puts,on="strike",suffixes=("_c","_p"))
                pairs=pairs[(pairs["strike"]>=0.98*S)&(pairs["strike"]<=1.02*S)]
                pairs["forward"]=pairs["strike"]+pairs["close_c"]-pairs["close_p"]
                pairs=pairs[np.isfinite(pairs["forward"])&(pairs["forward"]>0)]
                F=float(pairs["forward"].median()) if not pairs.empty else S
                T=(expiry-d).days/365.25
                ivs={}; ois={}; vols={}
                for m in MONEYNESS:
                    target=F*m
                    c=pick(calls,target); p=pick(puts,target)
                    if c is not None:
                        ivs[f"ce_{m:.3f}"]=iv(c["close"],F,c["strike"],T,True); ois[f"ce_{m:.3f}"]=c["oi"]; vols[f"ce_{m:.3f}"]=c["volume"]
                    if p is not None:
                        ivs[f"pe_{m:.3f}"]=iv(p["close"],F,p["strike"],T,False); ois[f"pe_{m:.3f}"]=p["oi"]; vols[f"pe_{m:.3f}"]=p["volume"]
                atm=np.nanmean([ivs.get("ce_1.000",np.nan),ivs.get("pe_1.000",np.nan)])
                pw,cw=ivs.get("pe_0.950",np.nan),ivs.get("ce_1.050",np.nan)
                rows.append({
                  "signal_date":str(d),"expiry":str(expiry),"tenor":tenor,"feature_cutoff_timestamp":f"{d} 15:30:00+05:30",
                  "spot":S,"forward":F,"atm_iv":atm,
                  "put_call_skew_5pct":pw-cw if np.isfinite(pw) and np.isfinite(cw) else np.nan,
                  "iv_curvature_5pct":np.nanmean([pw,cw])-atm if np.isfinite(atm) and np.isfinite(pw) and np.isfinite(cw) else np.nan,
                  "pcr_oi_5pct":np.nansum([v for k,v in ois.items() if k.startswith("pe_")])/max(np.nansum([v for k,v in ois.items() if k.startswith("ce_")]),1e-12),
                  "pcr_volume_5pct":np.nansum([v for k,v in vols.items() if k.startswith("pe_")])/max(np.nansum([v for k,v in vols.items() if k.startswith("ce_")]),1e-12),
                  "oi_total_5pct":np.nansum(list(ois.values())),"volume_total_5pct":np.nansum(list(vols.values())),
                  "iv_method":"Black76_forward_from_same-expiry_ATM_call_put_parity_no_discount",
                  "source":"thetrademarkk/india-index-options-1m"
                })
            except Exception as exc:
                errors.append({"signal_date":str(d),"expiry":str(expiry),"tenor":tenor,"error":f"{type(exc).__name__}:{exc}"})
    out=pd.DataFrame(rows)
    if out.empty: raise SystemExit("No HF option-surface rows built")
    wide=out.pivot(index="signal_date",columns="tenor")
    wide.columns=[f"{a}_{b}" for a,b in wide.columns]
    wide=wide.reset_index()
    for c in ["atm_iv_1w","atm_iv_2w","atm_iv_1m"]:
        if c not in wide: wide[c]=np.nan
    wide["iv_term_slope_2w_1w"]=wide["atm_iv_2w"]-wide["atm_iv_1w"]
    wide["iv_term_slope_1m_1w"]=wide["atm_iv_1m"]-wide["atm_iv_1w"]
    wide["sample_status"]=np.where(pd.to_datetime(wide["signal_date"]).dt.date<=CUTOFF,"development","fresh_untouched")
    wide.to_parquet(OUT/"option_surface_features.parquet",index=False)
    pd.DataFrame(errors).to_csv(OUT/"option_surface_errors.csv",index=False)
    (OUT/"option_surface_status.json").write_text(json.dumps({"rows":len(wide),"errors":len(errors),"performance_evaluation_run":False,"model_selection_run":False,"source":"thetrademarkk/india-index-options-1m"},indent=2),encoding="utf-8")

if __name__=="__main__": main()
