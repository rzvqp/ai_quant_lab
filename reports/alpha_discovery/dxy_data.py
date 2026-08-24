"""dxy_data.py — Mandate ALPHA-XAUUSD-DXY-CAUSAL-INCREMENTAL-INFORMATION-001 (FOUNDATION).
Causal loader/aligner for the RATIFIED ICE DXY H1 dataset (acquisition_staging/dxy) joined to XAUUSD H1
(OANDA_XAUUSD_H1_from_M15_v2 = the same reference the DXY coverage was matched against). Honors the ratified
timestamp contract: DXY feature available at dxy.time+3600; join requires dxy_close <= XAUUSD decision (bar close).
merge_asof backward on (dxy.time+3600) vs (xau.time+3600). Per-slice DXY features (governed slices only, no
between-block continuous). Small predeclared lag set {0,1,2,4} H1. NO strategy here — data + causal join only.
"""
import os, numpy as np, pandas as pd
import hist_data as hd
_HERE=os.path.dirname(os.path.abspath(__file__))
DXYDIR=os.path.join(os.path.dirname(os.path.dirname(_HERE)),"acquisition_staging","dxy")
if not os.path.isdir(DXYDIR): DXYDIR=os.path.join("C:\\Users\\MEDION GAMING\\ai_quant_lab-alpha-automation","acquisition_staging","dxy")
SLICES={"b0":"DXY_B0_RESEARCH_SLICE.csv","b1":"DXY_B1_RESEARCH_SLICE.csv","y2123":"DXY_2021_2023_RESEARCH_SLICE.csv"}
Y2123=(1627344000,1703883600)  # 2021-07-27T00:00Z .. 2023-12-29T21:00Z (DXY slice window)
LAGS=(0,1,2,4)

def xau_h1():
    d=hd._load("H1"); t=d["time"].to_numpy()
    d["is_y2123"]=(t>=Y2123[0])&(t<=Y2123[1])
    return d

def dxy_feats(d):
    """Causal DXY features from DXY closes (all known at the DXY bar's close). Small predeclared set (§5/§11)."""
    d=d.sort_values("time").reset_index(drop=True); c=d["close"].to_numpy(); h=d["high"].to_numpy(); l=d["low"].to_numpy()
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=pd.Series(tr).rolling(14).mean().to_numpy(); atr_ma=pd.Series(atr).rolling(30).mean().shift(1).to_numpy()
    ema20=pd.Series(c).ewm(span=20,adjust=True).mean().to_numpy()
    s1=pd.Series(c).shift(1).to_numpy(); s4=pd.Series(c).shift(4).to_numpy(); s8=pd.Series(c).shift(8).to_numpy()
    net=c-pd.Series(c).shift(8).to_numpy(); path=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(8).sum().shift(1).to_numpy()
    d["d_ret1"]=c-s1                          # 1h DXY change (points)
    d["d_ret4"]=c-s4                          # 4h DXY change (points)
    d["d_eff"]=np.where(path>0,net/path,np.nan)  # directional efficiency(8)
    d["d_atr"]=atr; d["d_vr"]=atr/atr_ma      # volatility + vol ratio
    d["d_imp"]=(c-s4)/atr                     # impulse in ATR (4h)
    v_rec=(c-s4)/atr; v_pri=(s4-s8)/atr; d["d_accel"]=v_rec-v_pri  # acceleration (4h vel vs prior)
    d["d_dist"]=(c-ema20)/atr                 # distance from recent structure
    return d

def load_dxy():
    out={}
    for era,f in SLICES.items():
        d=pd.read_csv(os.path.join(DXYDIR,f)).drop_duplicates("time").sort_values("time").reset_index(drop=True)
        out[era]=dxy_feats(d)
    return out

FEATCOLS=["d_ret1","d_ret4","d_eff","d_atr","d_vr","d_imp","d_accel","d_dist"]

def align(xau_era, dxy_era):
    """Causal merge_asof: XAUUSD decision (bar close = time+3600) <- most recent DXY bar with close (time+3600) <= decision.
    Attaches lag0 features + lagged {1,2,4} (shifted on the DXY series). Returns merged xau frame + coverage stats."""
    xau=xau_era.sort_values("time").reset_index(drop=True).copy(); xau["decision"]=xau["time"].to_numpy()+3600
    dxy=dxy_era.sort_values("time").reset_index(drop=True).copy(); dxy["dclose"]=dxy["time"].to_numpy()+3600
    cols={}
    for f in FEATCOLS:
        for L in LAGS:
            cols[f"{f}_l{L}"]=dxy[f].shift(L)
    dxy_lag=pd.concat([dxy[["dclose","time"]].rename(columns={"time":"dxy_time"}), pd.DataFrame(cols)],axis=1)
    m=pd.merge_asof(xau, dxy_lag, left_on="decision", right_on="dclose", direction="backward")
    # causal assertion + coverage
    okm=m["dclose"].notna().to_numpy()
    assert (m.loc[okm,"dclose"].to_numpy() <= m.loc[okm,"decision"].to_numpy()).all(), "DXY CAUSAL VIOLATION"
    same_hour=okm & (m["dclose"].to_numpy()==m["decision"].to_numpy())   # DXY bar closes exactly at decision (same-hour)
    within2h=okm & ((m["decision"].to_numpy()-m["dclose"].fillna(-1).to_numpy())<=2*3600)
    return m, dict(n=len(m), matched=int(okm.sum()), same_hour=int(same_hour.sum()), within2h=int(within2h.sum()))

def build(verbose=False):
    xa=xau_h1(); dx=load_dxy(); out={}
    for era,mask_col in (("b0","is_b0"),("b1","is_b1"),("y2123","is_y2123")):
        sub=xa[xa[mask_col]].reset_index(drop=True)
        m,cov=align(sub, dx[era]); out[era]=m
        if verbose:
            print(f"  {era}: XAUUSD H1={cov['n']}  DXY-matched={cov['matched']}  same-hour={cov['same_hour']} ({100*cov['same_hour']/cov['n']:.1f}%)  within2h={cov['within2h']} ({100*cov['within2h']/cov['n']:.1f}%)")
    return out

if __name__=="__main__":
    print("DXY FOUNDATION — causal XAUUSD-H1 <- ratified ICE DXY H1 join. Coverage per era (same-hour vs contract report):")
    frames=build(verbose=True)
    # sanity: known NEGATIVE DXY->gold relationship should appear via the causal join (not a strategy — a join sanity check)
    print("\nSANITY (causal join correctness): corr(DXY recent 4h return, XAUUSD forward 24h return):")
    for era,m in frames.items():
        c=m["close"].to_numpy(); fwd=pd.Series(c).shift(-24).to_numpy()-c
        d4=m["d_ret4_l0"].to_numpy(); ok=np.isfinite(d4)&np.isfinite(fwd)
        r=np.corrcoef(d4[ok],fwd[ok])[0,1] if ok.sum()>100 else float("nan")
        print(f"   {era}: corr={r:+.3f} (n={int(ok.sum())})  [expect NEGATIVE: DXY up -> gold down]")
