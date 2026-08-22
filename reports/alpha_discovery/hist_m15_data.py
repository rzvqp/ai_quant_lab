"""hist_m15_data.py — CAUSAL historical INTRADAY M15 loader (separately-versioned, §2-§4).
Reads RAW data/market/OANDA_XAUUSD_M15.csv but SLICES the exact authorized b0/b1 regions BEFORE any feature
generation (§2). Hard-blocks 2024/2025+/CALIB/gap rows (§2). Proves the research dataframe contains ONLY
authorized timestamps via assertions (§3) -> else DATA_GOVERNANCE_BLOCKER. Builds H1/H4/D1 context by CAUSAL
aggregation from the SAME sliced M15 (close_time = last constituent M15 epoch; FEATURE_AVAILABLE_AT<=DECISION_TIME).
The legacy non-causal D1->H4 merge is NOT used. Frozen artifacts untouched.
"""
import os, numpy as np, pandas as pd
import hist_data as hd   # BLOCKS, PROTECT_FROM, _feat, _regime, align_causal, TICK, PIP, COST
MKT=hd.MKT
TICK=hd.TICK; PIP=hd.PIP; COST=hd.COST; BLOCKS=hd.BLOCKS; PROTECT_FROM=hd.PROTECT_FROM
_FREQ={"H1":"1h","H4":"4h","D1":"1D"}; _MINSUB={"H1":3,"H4":12,"D1":60}  # of 4/16/96 M15 per bar

class DataGovernanceBlocker(Exception): pass

def load_m15_sliced(verbose=True):
    f=os.path.join(MKT,"OANDA_XAUUSD_M15.csv")
    d=pd.read_csv(f, usecols=["time","open","high","low","close","volume"])
    d=d.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    t=d["time"].to_numpy()
    b0=BLOCKS["b0"]; b1=BLOCKS["b1"]; cal=BLOCKS["calib"]
    keep=((t>=b0[0])&(t<=b0[1]))|((t>=b1[0])&(t<=b1[1]))
    d=d[keep].reset_index(drop=True)
    t=d["time"].to_numpy()
    # ---- GOVERNANCE BOUNDARY TEST (§3) ----
    try:
        assert len(d)>0, "empty slice"
        assert t.min()>=b0[0], "min < b0 start"
        assert t.max()<=b1[1], "max > b1 end"
        assert not (t>=PROTECT_FROM).any(), "PROTECTED 2024+ row present"
        assert not ((t>=cal[0])&(t<=cal[1])).any(), "CALIB row present"
        assert not ((t>b0[1])&(t<b1[0])).any(), "manifest-gap (2013-2016) row present"
        assert (((t>=b0[0])&(t<=b0[1]))|((t>=b1[0])&(t<=b1[1]))).all(), "row outside b0 U b1"
    except AssertionError as e:
        raise DataGovernanceBlocker(f"DATA_GOVERNANCE_BLOCKER: {e}")
    d["dt"]=pd.to_datetime(d["time"],unit="s",utc=True)
    d["seg"]=np.where((t>=b0[0])&(t<=b0[1]),0,1)  # 0=b0, 1=b1
    if verbose:
        nb0=int((d["seg"]==0).sum()); nb1=int((d["seg"]==1).sum())
        print(f"[GOVERNANCE PROOF] M15 sliced: rows={len(d)} b0={nb0} b1={nb1}")
        print(f"  min_ts={t.min()} ({d['dt'].min()})  max_ts={t.max()} ({d['dt'].max()})")
        print(f"  protected(>=2024)=0  CALIB=0  gap(2013-2016)=0  outside_b0b1=0  -> ONLY AUTHORIZED TIMESTAMPS")
    return d

def _seg_apply(df, fn):
    parts=[fn(g.copy()) for _,g in df.groupby("seg")]
    return pd.concat(parts).sort_values("time").reset_index(drop=True)

def aggregate(m15, tf):
    """Causal OHLC aggregation of sliced M15 -> tf, per block. close_time = last M15 epoch in bucket."""
    def do(g):
        gg=g.assign(bucket=g["dt"].dt.floor(_FREQ[tf])).groupby("bucket")
        a=gg.agg(open=("open","first"),high=("high","max"),low=("low","min"),close=("close","last"),
                 volume=("volume","sum"),nsub=("open","size"),open_time=("time","first"),
                 close_time=("time","last")).reset_index()
        a=a[a["nsub"]>=_MINSUB[tf]].reset_index(drop=True)
        a["dt"]=a["bucket"]; a["time"]=a["open_time"].astype("int64"); a["seg"]=g["seg"].iloc[0]
        return a[["time","dt","open","high","low","close","volume","nsub","close_time","seg"]]
    return _seg_apply(m15, do)

def build(verbose=True):
    m15=load_m15_sliced(verbose)
    m15=_seg_apply(m15, lambda g: hd._regime(hd._feat(g)))
    tfs={"M15":m15}
    for tf in ("H1","H4","D1"):
        x=aggregate(m15,tf); x=_seg_apply(x, lambda g: hd._regime(hd._feat(g))); tfs[tf]=x
    for tf,x in tfs.items():
        t=x["time"].to_numpy()
        assert not (t>=PROTECT_FROM).any() and t.max()<=BLOCKS["b1"][1], f"{tf} protected leak"
        x["is_b0"]=(x["seg"]==0); x["is_b1"]=(x["seg"]==1); x["is_disc"]=True
    return tfs

def align_causal(low, high, cols, suffix):
    """HTF value usable at low.time only if HTF.close_time <= low.time (bar fully closed)."""
    lo=low.sort_values("time").reset_index(drop=True); hi=high.sort_values("close_time").reset_index(drop=True)
    idx=np.searchsorted(hi["close_time"].to_numpy(), lo["time"].to_numpy(), side="right")-1
    out=lo.copy()
    for c in cols:
        col=hi[c].to_numpy()
        if np.issubdtype(col.dtype,np.number):
            v=np.full(len(lo),np.nan); m=idx>=0; v[m]=col[idx[m]]
        else:
            v=np.full(len(lo),None,object); m=idx>=0; v[np.where(m)[0]]=col[idx[m]]
        out[c+suffix]=v
    okm=idx>=0
    assert (hi["close_time"].to_numpy()[idx[okm]] <= lo["time"].to_numpy()[okm]).all(), "CAUSAL VIOLATION"
    out["_hidx"]=idx
    return out

if __name__=="__main__":
    tfs=build()
    for tf,x in tfs.items():
        print(f"{tf}: total={len(x)} b0={int(x['is_b0'].sum())} b1={int(x['is_b1'].sum())} "
              f"range={x['dt'].min().date()}..{x['dt'].max().date()}")
        if "regime" in x:
            print("   b0 regimes:", x[x['is_b0']]["regime"].value_counts().to_dict())
            print("   b1 regimes:", x[x['is_b1']]["regime"].value_counts().to_dict())
    # causal align smoke test M15<-H4
    h4=tfs["H4"].copy(); h4["h4_dn"]=(h4["ema20"]<h4["ema50"]).astype(float)
    mc=align_causal(tfs["M15"],h4,["h4_dn"],"_h4")
    print("M15<-H4 causal align OK; coverage:", np.isfinite(mc["h4_dn_h4"].to_numpy()).mean().round(3))
    print("GOVERNANCE + CAUSAL ASSERTIONS PASSED.")
