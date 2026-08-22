"""market_mode.py — MARKET_OPERATING_MODE_V1 (Mandate ...HIERARCHICAL-MODE..., §3-8). Price-only, causal, H4.
FROZEN taxonomy defined from price behavior ONLY (no P&L, no future labels). Solves §4: separates a genuine
PRIMARY BEAR from a CORRECTION inside a bull (and vice versa) via a two-scale H4 view — a PRIMARY backbone
(displacement over P=30 H4 bars ~5 trading days) vs the IMMEDIATE direction (I=6 H4 bars ~1 day). Volatility
(vr) and extension (ext) carried as ATTRIBUTE tags, NOT separate modes (avoid combinatorial explosion).
Research-local NEUTRAL_ROTATION is NOT canonical RANGE (§7). D1 not used (§6).
"""
import numpy as np, pandas as pd
# ---- FROZEN thresholds (price-structure reasoning, not fit to outcomes) ----
P=30; I=6            # primary backbone lookback (H4 bars ~5d) ; immediate lookback (~1d)
PRIM_T=1.0           # primary displacement threshold in ATR (a multi-day directional move)
IMM_T=0.3            # immediate displacement threshold in ATR
EFF_T=0.25           # efficiency boundary (neutral rotation vs directional), matches regime taxonomy
MODES=["PRIMARY_BULL_IMPULSE","BULL_CORRECTION","PRIMARY_BEAR_IMPULSE","BEAR_CORRECTION","NEUTRAL_ROTATION","TRANSITION"]

def mode(df):
    """FROZEN causal H4 market-operating-mode. All inputs known at H4 bar close."""
    c=df["close"].to_numpy(); atr=df["atr"].to_numpy(); eff=df["effic"].to_numpy()
    pdisp=(c-pd.Series(c).shift(P).to_numpy())/atr     # primary backbone displacement (ATR)
    idisp=(c-pd.Series(c).shift(I).to_numpy())/atr     # immediate displacement (ATR)
    prim=np.where(pdisp>PRIM_T,1,np.where(pdisp< -PRIM_T,-1,0))   # +1 bull / -1 bear / 0 neutral backbone
    imm =np.where(idisp>IMM_T,1,np.where(idisp< -IMM_T,-1,0))
    lab=np.full(len(df),"NA",dtype=object)
    for i in range(len(df)):
        if not (np.isfinite(pdisp[i]) and np.isfinite(idisp[i]) and np.isfinite(eff[i])): continue
        if prim[i]==1:   lab[i]="PRIMARY_BULL_IMPULSE" if imm[i]>=0 else "BULL_CORRECTION"
        elif prim[i]==-1:lab[i]="PRIMARY_BEAR_IMPULSE" if imm[i]<=0 else "BEAR_CORRECTION"
        else:            lab[i]="NEUTRAL_ROTATION" if abs(eff[i])<EFF_T else "TRANSITION"
    return lab

def vol_tag(df):
    vr=(df["atr"]/df["atr_ma"]).to_numpy()
    return np.where(vr>1.3,"HIGH",np.where(vr<0.85,"LOW","NORMAL"))

def episodes_days(lab, mask, dt):
    """episodes = contiguous runs of same mode within mask; return per-mode {episodes, bars, unique_days, avg_dur_h}."""
    idx=np.where(mask)[0]; out={m:{"bars":0,"episodes":0,"days":set()} for m in MODES}
    prev=None
    for i in idx:
        m=lab[i]
        if m not in out: continue
        out[m]["bars"]+=1; out[m]["days"].add(pd.Timestamp(dt[i]).floor("D"))
        if m!=prev: out[m]["episodes"]+=1
        prev=m
    for m in out: out[m]["unique_days"]=len(out[m].pop("days")); out[m]["avg_dur_h"]=(4*out[m]["bars"]/out[m]["episodes"]) if out[m]["episodes"] else 0
    return out

def transition_matrix(lab, mask):
    idx=np.where(mask)[0]; T={a:{b:0 for b in MODES} for a in MODES}; prev=None
    for i in idx:
        m=lab[i]
        if m not in MODES: prev=None; continue
        if prev is not None and prev!=m and prev in MODES: T[prev][m]+=1
        prev=m
    return T

def _report(tag, df, mask):
    lab=mode(df); dt=df["dt"].to_numpy() if "dt" in df.columns else pd.to_datetime(df["time"],unit="s",utc=True).to_numpy()
    n=int(mask.sum()); ed=episodes_days(lab,mask,dt)
    print(f"\n[{tag}] H4 bars={n}")
    for m in MODES:
        e=ed[m]; pct=100*e["bars"]/max(n,1)
        print(f"   {m:22s} bars={e['bars']:5d} ({pct:4.1f}%)  episodes={e['episodes']:4d}  uniqueDays={e['unique_days']:4d}  avgDur={e['avg_dur_h']:.0f}h")

def main():
    import swing_base as sb, hist_data as hd
    print("MARKET_OPERATING_MODE_V1 (frozen, price-only, causal H4). Population per era + transition matrix.")
    print(f"Thresholds: P={P} I={I} PRIM_T={PRIM_T} IMM_T={IMM_T} EFF_T={EFF_T}")
    # b0/b1 from hist H4 ; 2021/2022/2023 from gated sb H4
    h=hd._load("H4")
    _report("b0 2011-2013", h, h["is_b0"].to_numpy())
    _report("b1 2016-2018", h, h["is_b1"].to_numpy())
    sh=sb.build_frames()["H4"]; yr=sh["dt"].dt.year.to_numpy(); dev=sh["is_dev"].to_numpy()
    for y in (2021,2022,2023): _report(f"{y} (gated)", sh, dev&(yr==y))
    # transition matrix on b0 (representative)
    print("\nTRANSITION MATRIX (b0, episode-level counts):")
    T=transition_matrix(mode(h), h["is_b0"].to_numpy())
    hdr="from\\to        "+" ".join(f"{m[:8]:>8s}" for m in MODES); print("  "+hdr)
    for a in MODES: print(f"  {a[:14]:14s} "+" ".join(f"{T[a][b]:8d}" for b in MODES))

if __name__=="__main__":
    main()
