"""hist_data.py — CAUSAL historical XAUUSD loader (separately-versioned, §6). Different price-only population.
Reads data/market/OANDA_XAUUSD_{D1,H4,H1}_from_M15_v2.csv. HTF context is available ONLY after its bar has
fully closed (successor bar opened): FEATURE_AVAILABLE_AT <= DECISION_TIME. The legacy non-causal D1->H4 merge
is NOT used. Discovery blocks = b0 (2011-2013) + b1 (2016-2018) [DISCOVERY_CONSUMED, usable for NEW discovery,
NOT validation]. CALIB 2020-2021 = out-of-discovery readout. 2024+ PROTECTED -> excluded (asserted).
"""
import os, numpy as np, pandas as pd
_HERE=os.path.dirname(os.path.abspath(__file__))
MKT=os.path.join(os.path.dirname(os.path.dirname(_HERE)),"data","market")  # ai_quant_lab-alpha-automation/data/market
if not os.path.isdir(MKT): MKT=os.path.join("C:\\Users\\MEDION GAMING\\ai_quant_lab-alpha-automation","data","market")
TICK=0.01; PIP=0.10
COST={"GROSS":0.00,"BASE":0.05,"STRESS":0.24}
BLOCKS={"b0":(1311697800,1380300300),"b1":(1452502800,1523015550),"calib":(1597128300,1630844100)}
PROTECT_FROM=int(pd.Timestamp("2024-01-01",tz="UTC").timestamp())

def _feat(df):
    o,h,l,c=(df[k].to_numpy() for k in ("open","high","low","close"))
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    df["atr"]=pd.Series(tr).rolling(14).mean().to_numpy()
    df["ema20"]=pd.Series(c).ewm(span=20,adjust=True).mean().to_numpy()
    df["ema50"]=pd.Series(c).ewm(span=50,adjust=True).mean().to_numpy()
    net=c-pd.Series(c).shift(20).to_numpy()
    path=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(20).sum().shift(1).to_numpy()
    df["effic"]=np.where(path>0,net/path,np.nan)
    df["atr_ma"]=pd.Series(df["atr"]).rolling(30).mean().shift(1).to_numpy()
    return df

def _regime(df):
    e20,e50,eff=(df[k].to_numpy() for k in ("ema20","ema50","effic"))
    up=(e20>e50)&(eff>0.30); dn=(e20<e50)&(eff<-0.30); rng=(np.abs(eff)<0.20)
    lab=np.full(len(df),"REGIME_INDEPENDENT",object); lab[rng]="RANGE"; lab[up]="TREND_UP"; lab[dn]="TREND_DOWN"
    df["regime"]=lab; return df

def _load(kind):
    f={"D1":"OANDA_XAUUSD_D1_from_M15_v2.csv","H4":"OANDA_XAUUSD_H4_from_M15_v2.csv","H1":"OANDA_XAUUSD_H1_from_M15_v2.csv"}[kind]
    d=pd.read_csv(os.path.join(MKT,f)).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    d["dt"]=pd.to_datetime(d["time"],unit="s",utc=True)
    d=_regime(_feat(d))
    t=d["time"].to_numpy()
    d["is_b0"]=(t>=BLOCKS["b0"][0])&(t<=BLOCKS["b0"][1])
    d["is_b1"]=(t>=BLOCKS["b1"][0])&(t<=BLOCKS["b1"][1])
    d["is_disc"]=d["is_b0"]|d["is_b1"]
    d["is_calib"]=(t>=BLOCKS["calib"][0])&(t<=BLOCKS["calib"][1])
    return d

def align_causal(low, high, cols, suffix):
    """HTF value usable at low.time ONLY if the HTF bar's SUCCESSOR has opened (bar fully closed).
    available_at[i] = high.time[i+1]; pick last i with available_at[i] <= low.time. No lookahead."""
    hi=high.sort_values("time").reset_index(drop=True); lo=low.sort_values("time").reset_index(drop=True)
    ht=hi["time"].to_numpy(); avail=np.empty(len(ht)); avail[:-1]=ht[1:]; avail[-1]=np.inf
    idx=np.searchsorted(avail, lo["time"].to_numpy(), side="right")-1
    out=lo.copy()
    for c in cols:
        col=hi[c].to_numpy()
        if np.issubdtype(col.dtype,np.number):
            v=np.full(len(lo),np.nan); m=idx>=0; v[m]=col[idx[m]]
        else:
            v=np.full(len(lo),None,object); m=idx>=0; v[np.where(m)[0]]=col[idx[m]]
        out[c+suffix]=v
    out["_hidx"]=idx
    # causal assertion: chosen HTF bar opened strictly before decision time
    okm=idx>=0
    assert (ht[idx[okm]] < lo["time"].to_numpy()[okm]).all(), "CAUSAL VIOLATION: HTF open >= decision time"
    return out

def load():
    tfs={k:_load(k) for k in ("D1","H4","H1")}
    for k,x in tfs.items():
        assert not ((x["is_disc"]|x["is_calib"]) & (x["time"].to_numpy()>=PROTECT_FROM)).any(), f"{k} PROTECTED-region leak"
    return tfs

if __name__=="__main__":
    tfs=load()
    for k,x in tfs.items():
        d=x[x["is_disc"]]
        print(f"{k}: total={len(x)} DISC(b0+b1)={len(d)} calib={int(x['is_calib'].sum())} "
              f"range={x['dt'].min().date()}..{x['dt'].max().date()}")
        if "regime" in x:
            print("   DISC regimes:", d["regime"].value_counts().to_dict())
    # causal alignment smoke test H4<-D1
    h4=tfs["H4"]; d1=tfs["D1"].copy(); d1["d1_dn"]=(d1["ema20"]<d1["ema50"]).astype(float)
    hc=align_causal(h4,d1,["d1_dn"],"_d1")
    print("H4<-D1 causal align OK; d1_dn coverage:", np.isfinite(hc["d1_dn_d1"].to_numpy()).mean().round(3))
    print("CAUSAL ASSERTIONS PASSED; PROTECTED 2024+ excluded from disc/calib.")
