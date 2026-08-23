"""cur_data.py — CURRENT-REGIME data substrate (mandate ALPHA-XAUUSD-CURRENT-REGIME-SPECIALIST-DISCOVERY-001 +
CURRENT_DATA_REBASE_AUTHORIZED). Loads the authorized canonical XAUUSD M15 through the latest fully closed bar
(wp5b OANDA_XAUUSD_M15.csv, 2011-07..~2026-07), same feature recipe as hist_data (_feat: atr14/ema/effic/atr_ma),
causal H4/H1 aggregation for MARKET_OPERATING_MODE_V1. Read-only on the ratified CSV; no future info in features.
"""
import os, numpy as np, pandas as pd
MKT=r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"
TF_SECONDS={"H1":3600,"H4":14400}

def _feat(df):
    o,h,l,c=(df[k].to_numpy() for k in ("open","high","low","close"))
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    df["atr"]=pd.Series(tr).rolling(14).mean().to_numpy()
    df["ema20"]=pd.Series(c).ewm(span=20,adjust=True).mean().to_numpy()
    df["ema50"]=pd.Series(c).ewm(span=50,adjust=True).mean().to_numpy()
    net=c-pd.Series(c).shift(20).to_numpy(); path=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(20).sum().shift(1).to_numpy()
    df["effic"]=np.where(path>0,net/path,np.nan)
    df["atr_ma"]=pd.Series(df["atr"]).rolling(30).mean().shift(1).to_numpy()
    return df

def load_m15():
    d=pd.read_csv(MKT).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    d["dt"]=pd.to_datetime(d["time"],unit="s",utc=True); d=_feat(d); d["close_time"]=d["time"].to_numpy()+900
    return d

def agg(m15, tf):
    sec=TF_SECONDS[tf]
    b=(m15["time"]//sec)*sec
    g=m15.assign(b=b).groupby("b")
    x=g.agg(open=("open","first"),high=("high","max"),low=("low","min"),close=("close","last"),
            volume=("volume","sum"),close_time=("time","last")).reset_index().rename(columns={"b":"time"})
    x["dt"]=pd.to_datetime(x["time"],unit="s",utc=True); x=_feat(x); x["close_time"]=x["close_time"].to_numpy()+900
    return x

def causal_bucket_asof(times, bucket_starts, tf):
    """THE canonical timestamp-alignment contract (VE-CURRENT-REGIME-TEMPORAL-CAUSALITY-REPAIR-001): for
    each finer-grained (e.g. M15) timestamp in `times`, finds the START of the most recently FULLY-CLOSED
    `tf` bucket ("H1"/"H4") among `bucket_starts` -- i.e. the bucket whose own CLOSE (start+TF_SECONDS[tf])
    is <= that timestamp -- NEVER the bucket containing `times` itself, and never one that closes after it.

    `agg()` above keys each aggregated bucket by its own START timestamp T, but any label/descriptor
    computed FROM that bucket's data (its own close, ATR, or anything derived from either) is only truly
    knowable once the bucket CLOSES, at T+TF_SECONDS[tf]. This is a proper backward-asof search over
    whichever buckets actually EXIST in `bucket_starts` -- deliberately NOT fixed-offset arithmetic
    (T-TF_SECONDS[tf]), which was tried first here and found to silently name a bucket that never traded
    (absent from any real `bucket_starts`/cache) across every session/weekend/holiday gap -- discarding
    otherwise-valid, already-closed prior information for roughly one bucket-width after every such gap
    (measured: 5,352 of 355,696 M15 bars in the full canonical history disagreed between the two methods,
    97% of them at the Sunday reopen). This exactly matches, and is now the single canonical form of, this
    codebase's own already-established `merge_asof(..., direction="backward")` on `close_time` convention
    (see `cur_cr13_trade.py`'s `h4_up_map`) -- there must be only one such convention, not a second,
    subtly-stricter one living here; every join from a lower-timeframe entry timestamp to a per-bucket
    label/regime-state/descriptor keyed by `agg()`'s own `time` column (start) -- including every
    `__cur_cache__/*.parquet` cache built from it -- goes through this function.

    Returns -1 (a sentinel that can never equal a real bucket-start timestamp) wherever no bucket has
    closed yet as of that timestamp (start of history)."""
    sec=TF_SECONDS[tf]
    starts=np.asarray(sorted(set(int(x) for x in bucket_starts)),np.int64)
    close_times=starts+sec
    t=np.asarray(times,np.int64)
    idx=np.searchsorted(close_times,t,side="right")-1
    out=np.full(t.shape,-1,dtype=np.int64)
    ok=idx>=0
    out[ok]=starts[idx[ok]]
    return out

if __name__=="__main__":
    import market_mode as MM
    m=load_m15(); print(f"M15: n={len(m)} range={m['dt'].min()} .. {m['dt'].max()} lastclose={m['close'].iloc[-1]:.1f}")
    h4=agg(m,"H4"); lab=MM.mode(h4)
    # recent windows
    for label,days in [("last 3mo",90),("last 6mo",180),("last 12mo",365),("2024 full",None)]:
        if days:
            cut=m["dt"].max()-pd.Timedelta(days=days); w=m[m["dt"]>=cut]; lw=lab[(h4["dt"]>=cut).to_numpy()]
        else:
            w=m[(m["dt"]>=pd.Timestamp("2024-01-01",tz="UTC"))&(m["dt"]<pd.Timestamp("2025-01-01",tz="UTC"))]
            msk=((h4["dt"]>=pd.Timestamp("2024-01-01",tz="UTC"))&(h4["dt"]<pd.Timestamp("2025-01-01",tz="UTC"))).to_numpy(); lw=lab[msk]
        if len(w)<50: continue
        vr=(w["atr"]/w["atr_ma"]).median(); eff=w["effic"].median(); px0,px1=w["close"].iloc[0],w["close"].iloc[-1]
        from collections import Counter; md=Counter(lw); tot=max(len(lw),1)
        modes=" ".join(f"{k[:9]}{v/tot:.0%}" for k,v in md.most_common(3))
        print(f"  {label:10s}: px {px0:.0f}->{px1:.0f} ({100*(px1/px0-1):+.0f}%) atr_med={w['atr'].median():.1f} vr_med={vr:.2f} effic_med={eff:+.2f} | modes: {modes}")
