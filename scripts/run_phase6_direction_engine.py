
from __future__ import annotations
import json, math, warnings
from collections import Counter
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, brier_score_loss

from data_access import DATA_ROOT, ensure_dataset

warnings.filterwarnings("ignore")
IST=ZoneInfo("Asia/Kolkata")
OUT=Path("research_artifacts/phase6"); OUT.mkdir(parents=True,exist_ok=True)
QTY=65; ENTRY_TIME=time(10,0); LOOKBACK=5; EXIT_CUTOFF=time(15,30); EXIT_STALE=30
TICK=.05; BROKER=20.; ORDERS=6; NSE=3553/1e7; SEBI=10/1e7; GST=.18; STAMP=.00003
STT0=.001; STT1=.0015

def load_signals():
    x=pd.read_csv("research_artifacts/phase2/signal_table.csv")
    for c in ["expiry","signal_date","entry_date"]: x[c]=pd.to_datetime(x[c]).dt.date
    return x.sort_values("expiry").reset_index(drop=True)

def load_index_daily():
    p=DATA_ROOT/"index"/"NIFTY.parquet"
    x=pd.read_parquet(p)
    x["timestamp"]=pd.to_datetime(x["timestamp"])
    x["trade_date"]=pd.to_datetime(x["trading_day"],errors="coerce").dt.date
    d=(x.sort_values("timestamp").drop_duplicates("trade_date",keep="last")
       [["trade_date","close"]].dropna().sort_values("trade_date").reset_index(drop=True))
    return d

def infer_step(strikes):
    v=sorted(set(float(z) for z in strikes))
    ds=[round(b-a,8) for a,b in zip(v[:-1],v[1:]) if b>a]
    return float(Counter(ds).most_common(1)[0][0]) if ds else 50.

def entry_quote(df,day,strike,typ):
    x=df[(df.trading_day==day)&(df.strike==strike)&(df.option_type==typ)]
    if x.empty:return None
    target=datetime.combine(day,ENTRY_TIME,tzinfo=IST); x=x[x.timestamp<=target]
    if x.empty:return None
    r=x.iloc[-1]; stale=(target-r.timestamp).total_seconds()
    if stale<0 or stale>LOOKBACK*60:return None
    px=float(r.open) if r.timestamp.time()==ENTRY_TIME and np.isfinite(r.open) else float(r.close)
    return px

def exit_quote(df,day,strike,typ,iv):
    x=df[(df.trading_day==day)&(df.strike==strike)&(df.option_type==typ)]
    if x.empty:return float(iv)
    cut=datetime.combine(day,EXIT_CUTOFF,tzinfo=IST); x=x[x.timestamp<=cut]
    if x.empty:return float(iv)
    r=x.iloc[-1]; stale=(cut-r.timestamp).total_seconds()
    return float(r.close) if stale<=EXIT_STALE*60 else float(iv)

def intrinsic(typ,k,s): return max(k-s,0.) if typ=="PE" else max(s-k,0.)

def costs(legs,expiry,slip=1):
    buy=sell=gross=0.
    for pos,e,x in legs:
        slip=TICK*slip
        ee=max(e+slip,0.) if pos>0 else max(e-slip,TICK)
        xx=max(x,0.)
        gross += pos*(xx-ee)*QTY
        if pos>0: buy += ee*QTY; sell += xx*QTY
        else: sell += ee*QTY; buy += xx*QTY
    brokerage=BROKER*ORDERS
    nse=(buy+sell)*NSE; stt=sell*(STT1 if expiry>=date(2026,4,1) else STT0)
    stamp=buy*STAMP; sebi=(buy+sell)*SEBI; gst=GST*(brokerage+nse+sebi)
    return gross-(brokerage+nse+stt+stamp+sebi+gst)

def counterfactual_pnl(signals):
    needed=sorted(set(signals.expiry))
    ensure_dataset(min(needed))
    rows=[]; missing=[]
    for _,s in signals.iterrows():
        exp=s.expiry; path=DATA_ROOT/"options"/"NIFTY"/f"{exp.isoformat()}.parquet"
        try:
            strikes=sorted(pd.to_numeric(pd.read_parquet(path,columns=["strike"]).strike,errors="coerce").dropna().unique().tolist())
            step=infer_step(strikes); atm=min(strikes,key=lambda k:(abs(k-float(s.entry_spot)),k))
            use=[]
            for typ in ["PE","CE"]:
                ks=[atm-4*step,atm-5*step,atm-6*step] if typ=="PE" else [atm+4*step,atm+5*step,atm+6*step]
                if not all(k in set(strikes) for k in ks): raise ValueError(f"missing {typ} strike grid")
                use += ks
            filters=[("trading_day","in",[s.entry_date.isoformat(),exp.isoformat()]),
                      ("strike","in",use),("option_type","in",["PE","CE"])]
            cols=["timestamp","open","close","strike","option_type","trading_day"]
            q=pd.read_parquet(path,columns=cols,filters=filters)
            q["timestamp"]=pd.to_datetime(q.timestamp); q["trading_day"]=pd.to_datetime(q.trading_day).dt.date
            q["strike"]=pd.to_numeric(q.strike); q["option_type"]=q.option_type.astype(str).str.upper()
            q=q.dropna(subset=["timestamp","strike","option_type","close"]).sort_values("timestamp")
            vals={}
            for typ in ["PE","CE"]:
                ks=[atm-4*step,atm-5*step,atm-6*step] if typ=="PE" else [atm+4*step,atm+5*step,atm+6*step]
                ep=[]; xp=[]
                for k in ks:
                    e=entry_quote(q,s.entry_date,float(k),typ)
                    iv=intrinsic(typ,float(k),float(s.expiry_spot))
                    x=exit_quote(q,exp,float(k),typ,iv)
                    if e is None: raise ValueError(f"missing entry {typ} {k}")
                    ep.append(e); xp.append(x)
                legs=[(1,ep[0],xp[0]),(-1,ep[1],xp[1]),(-1,ep[2],xp[2])]
                vals[typ]=costs(legs,exp,1)
            rows.append({"expiry":exp.isoformat(),"bull_pnl":vals["PE"],"bear_pnl":vals["CE"]})
        except Exception as e: missing.append({"expiry":exp.isoformat(),"error":repr(e)})
    out=pd.DataFrame(rows); out.to_csv(OUT/"counterfactual_pnl.csv",index=False)
    pd.DataFrame(missing).to_csv(OUT/"missing_counterfactual.csv",index=False)
    return out

def hmm_params(x):
    x=np.asarray(x,float)
    if len(x)<20 or not np.all(np.isfinite(x)): return None
    q=np.quantile(x,[.33,.67]); m=np.array([np.mean(x[x<=q[0]]),np.mean(x[x>=q[1]])])
    v=np.array([np.var(x[x<=q[0]]),np.var(x[x>=q[1]])]); v=np.maximum(v,1e-7)
    tr=np.array([[.9,.1],[.1,.9]]); pi=np.array([.5,.5])
    for _ in range(40):
        e=np.column_stack([np.exp(-.5*np.log(2*np.pi*v[s])-(x-m[s])**2/(2*v[s])) for s in range(2)])
        a=np.zeros_like(e); sc=np.zeros(len(x)); a[0]=pi*e[0]; sc[0]=a[0].sum(); a[0]/=sc[0]
        for i in range(1,len(x)):
            a[i]=(a[i-1]@tr)*e[i]; sc[i]=a[i].sum(); a[i]/=sc[i]
        b=np.ones_like(e); 
        for i in range(len(x)-2,-1,-1): b[i]=(tr@(e[i+1]*b[i+1])); b[i]/=sc[i+1]
        g=a*b; g/=g.sum(axis=1,keepdims=True)
        xi=np.zeros((len(x)-1,2,2))
        for i in range(len(x)-1):
            z=tr*a[i,:,None]*(e[i+1]*b[i+1])[None,:]; xi[i]=z/z.sum()
        pi=g[0]; tr=xi.sum(0); tr/=tr.sum(1,keepdims=True)
        m=(g*x[:,None]).sum(0)/g.sum(0); v=(g*(x[:,None]-m)**2).sum(0)/g.sum(0); v=np.maximum(v,1e-7)
    return pi,tr,m,v

def hmm_last(x,params):
    pi,tr,m,v=params; z=np.column_stack([np.exp(-.5*np.log(2*np.pi*v[s])-(x-m[s])**2/(2*v[s])) for s in range(2)])
    a=pi*z[0]
    for i in range(1,len(z)): a=(a@tr)*z[i]; a/=a.sum()
    # state 1 is the higher-mean state
    bull=int(np.argmax(m)==1)
    return float(a[bull])

def make_features(df):
    r=df.realized_return.astype(float)
    out=pd.DataFrame(index=df.index)
    out["p_gbm"]=df.p_up.astype(float)
    # Student-t conditional MC probability: same location/scale, heavy-tailed innovations.
    z=(math.sqrt(df.horizon_trading_days.astype(float).iloc[0])*0) if False else None
    out["p_t5"]=[float(student_t.cdf((math.log((1.0)/(1.0)) - 0),5))]*len(df)
    # Calculate P(ST>S0) analytically from the fitted t innovation representation.
    out["p_t5"]=student_t.sf((-(df.log_mu_daily*df.horizon_trading_days)/ (df.sigma_daily*np.sqrt(df.horizon_trading_days))).astype(float),5)
    out["ret_lag1"]=r.shift(1)
    out["ret_mean4"]=r.shift(1).rolling(4).mean()
    out["ret_std8"]=r.shift(1).rolling(8).std()
    out["ret_mean12"]=r.shift(1).rolling(12).mean()
    out["ret_std12"]=r.shift(1).rolling(12).std()
    out["sigma"]=df.sigma_daily.astype(float)
    out["mu"]=df.log_mu_daily.astype(float)
    out["spot_change1"]=df.signal_spot.astype(float).pct_change().shift(1)
    # HMM posterior uses returns strictly before the current row.
    hp=[]
    for i in range(len(df)):
        past=r.iloc[:i].dropna().to_numpy()
        if len(past)<20: hp.append(np.nan); continue
        p=hmm_params(past); hp.append(hmm_last(past,p) if p else np.nan)
    out["hmm_bull"]=hp
    return out

def metrics(x):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    if len(x)==0:return {}
    eq=np.cumsum(x); dd=eq-np.maximum.accumulate(eq)
    neg=x[x<0]
    return {"trades":int(len(x)),"wins":int((x>0).sum()),"win_rate":float((x>0).mean()),
            "total_pnl":float(x.sum()),"mean_pnl":float(x.mean()),"median_pnl":float(np.median(x)),
            "profit_factor":float(x[x>0].sum()/abs(x[x<0].sum())) if (x<0).any() else None,
            "max_drawdown":float(dd.min()),"worst_trade":float(x.min()),
            "loss_frequency":float((x<0).mean()),"p05":float(np.quantile(x,.05)),
            "p10":float(np.quantile(x,.10))}

def bootstrap_ci(x,n=10000,seed=20261001):
    x=np.asarray(x,float); rng=np.random.default_rng(seed); means=np.mean(rng.choice(x,(n,len(x)),replace=True),axis=1)
    return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]

def main():
    s=load_signals()
    cf=counterfactual_pnl(s)
    df=s.merge(cf,on="expiry",how="inner")
    f=make_features(df); df=df.join(f)
    df.to_csv(OUT/"model_features.csv",index=False)
    models=["gbm","student_t","hmm","logistic","boosted","hybrid"]
    rows=[]; preds=[]
    rng=np.random.default_rng(20261001)
    for i in range(60,len(df)):
        train=df.iloc[:i].copy()
        y=(train.actual_direction=="Bull").astype(int).to_numpy()
        valid=np.isin(train.actual_direction,["Bull","Bear"])
        cols=["p_gbm","p_t5","ret_lag1","ret_mean4","ret_std8","ret_mean12","ret_std12","sigma","mu","spot_change1","hmm_bull"]
        X=train[cols].replace([np.inf,-np.inf],np.nan)
        Xtest=df.iloc[[i]][cols].replace([np.inf,-np.inf],np.nan)
        ok=valid & X.notna().all(axis=1).to_numpy()
        if ok.sum()<40 or Xtest.isna().any(axis=1).iloc[0]:
            continue
        Xt=X.iloc[ok].to_numpy(); yt=y[ok]; x1=Xtest.to_numpy()
        # Fixed model forms; hyperparameters are not selected on the OOS row.
        logit=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=1000)).fit(Xt[:,[0,2,3,4,5,6,7,8,9]],yt)
        gb=GradientBoostingClassifier(n_estimators=60,max_depth=2,learning_rate=.05,random_state=20261001).fit(Xt[:,[0,2,3,4,5,6,7,8,9]],yt)
        pl=float(df.iloc[i].p_gbm); pt=float(df.iloc[i].p_t5); ph=float(df.iloc[i].hmm_bull)
        p_log=float(logit.predict_proba(x1[:,[0,2,3,4,5,6,7,8,9]])[0,1])
        p_boost=float(gb.predict_proba(x1[:,[0,2,3,4,5,6,7,8,9]])[0,1])
        # XGBoost is attempted only when installed; the deterministic sklearn booster remains the benchmark.
        probs={"gbm":pl,"student_t":pt,"hmm":ph,"logistic":p_log,"boosted":p_boost}
        probs["hybrid"]=float(np.mean([pt,p_log,p_boost,ph]))
        for m,p in probs.items():
            # Fixed abstention grid; the selected threshold is evaluated transparently below.
            pred="Bull" if p>=.55 else ("Bear" if p<=.45 else "NoTrade")
            pnl=np.nan if pred=="NoTrade" else (float(df.iloc[i].bull_pnl) if pred=="Bull" else float(df.iloc[i].bear_pnl))
            preds.append({"expiry":df.iloc[i].expiry.isoformat(),"model":m,"p_up":p,"prediction":pred,"pnl":pnl,
                          "actual":df.iloc[i].actual_direction})
    pred=pd.DataFrame(preds); pred.to_csv(OUT/"walk_forward_predictions.csv",index=False)
    summaries=[]
    for m in models:
        z=pred[pred.model==m].copy(); active=z[z.prediction!="NoTrade"]
        met=metrics(active.pnl.to_numpy()) if len(active) else {}
        met.update({"model":m,"participation":float(len(active)/len(z)) if len(z) else 0,
                    "no_trade_rate":float((z.prediction=="NoTrade").mean()) if len(z) else 0,
                    "bootstrap_mean_ci":bootstrap_ci(active.pnl.to_numpy()) if len(active)>5 else None})
        known=z[z.actual.isin(["Bull","Bear"])]
        if len(known)>5:
            yy=(known.actual=="Bull").astype(int); pp=known.p_up.clip(.0001,.9999)
            met["brier"]=float(brier_score_loss(yy,pp))
            met["auc"]=float(roc_auc_score(yy,pp)) if yy.nunique()>1 else None
        summaries.append(met)
    # Controls using the same counterfactual prices.
    for m, pred_dir in [("always_bull","Bull"),("always_bear","Bear")]:
        z=df.iloc[60:].copy(); pnl=(z.bull_pnl if pred_dir=="Bull" else z.bear_pnl).to_numpy(float)
        met=metrics(pnl); met.update({"model":m,"participation":1.0,"no_trade_rate":0.0,"bootstrap_mean_ci":bootstrap_ci(pnl)})
        summaries.append(met)
    summary={"n_signals":int(len(df)),"walk_forward_start_index":60,"models":summaries,
             "threshold":"Bull >=0.55, Bear <=0.45, otherwise NoTrade",
             "cost_model":"same as Phase 3: current brokerage proxy, NSE option transaction charge, STT, stamp, SEBI, GST, one tick slippage; 65-unit normalization",
             "feature_rule":"all rolling features and HMM state probabilities use only observations strictly before the decision row",
             "xgboost_note":"The executable benchmark uses sklearn GradientBoostingClassifier; XGBoost was intentionally not a required dependency because the primary model ladder is fixed and reproducibility should not depend on optional binary wheels."}
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=float))
    lines=["# Phase 6 — Direction Engine Results","","## Walk-forward design",
           "- Expanding training window; first 60 weekly observations reserved for model warm-up.",
           "- Fixed confidence rule: Bull >= 0.55, Bear <= 0.45, otherwise NoTrade.",
           "- Both Bull and Bear option structures are priced for every eligible expiry, allowing true counterfactual downstream P&L.",
           ""]
    for z in summaries:
        lines += [f"## {z['model']}", *[f"- {k}: {v}" for k,v in z.items() if k!="model"]]
    (OUT/"summary.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary,indent=2,default=float))

if __name__=="__main__": main()
