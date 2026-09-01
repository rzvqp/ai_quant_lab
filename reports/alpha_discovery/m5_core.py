"""m5_core.py — M5_EVENT_REVEALED_DIRECTION_FACTORY_V1 core. NATIVE XAUUSD M5 (no aggregation), conditional-response state machines.

Direction is EVENT-REVEALED (sign of the causal event), never forecast. Conservative same-bar ordering (ambiguous bar -> STOP). Native M5
only (2021-07-27+). Cost = price 0.419/risk (canonical 0.24R@median-M15-ATR) applied per-trade; report cost%risk. 1 project pip = $0.10.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")

COST=0.419; PIP=0.10
M5=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\data\market\OANDA_XAUUSD_M5.csv"

def load():
    d=pd.read_csv(M5).drop_duplicates("time").sort_values("time").reset_index(drop=True)
    t=d["time"].values.astype("int64"); o=d["open"].values.astype(float); h=d["high"].values.astype(float)
    l=d["low"].values.astype(float); c=d["close"].values.astype(float)
    dt=pd.to_datetime(t,unit='s',utc=True); yr=dt.year.values; hr=dt.hour.values; n=len(c)
    tr=np.maximum.reduce([h-l,np.abs(h-np.r_[c[0],c[:-1]]),np.abs(l-np.r_[c[0],c[:-1]])])
    atr=pd.Series(tr).rolling(14).mean().shift(1).to_numpy()          # causal ATR (known at bar open)
    atr50=pd.Series(tr).rolling(50).mean().shift(1).to_numpy()
    return dict(t=t,o=o,h=h,l=l,c=c,dt=dt,yr=yr,hr=hr,n=n,atr=atr,atr50=atr50)

def resolve(M, k, side, stop_px, exit_mode="2R", tgtR=2.0, H=96):
    """Enter at M5 OPEN of bar k (signal complete at k-1 close). Conservative same-bar (both reachable -> stop). H bars horizon (~8h).
    exit_mode: '2R' fixed | 'struct' (target = 3R structural proxy) | 'trail' (ATR chandelier) | 'time' (exit at H or +/-). net-R after cost.
    Also returns raw-path stats: mfe_R, mae_R, reach100/200/300 pips before invalidation."""
    o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"]
    if k>=n or not np.isfinite(stop_px): return None
    entry=o[k]; risk=abs(entry-stop_px)
    if risk<=0: return None
    end=min(k+H,n-1); mfe=-1e9; mae=1e9
    reach={100:0,200:0,300:0}; invalid_at=None
    # trailing state
    trail=stop_px; res=None; exit_bar=end
    for j in range(k,end+1):
        fav=(h[j]-entry)/risk if side>0 else (entry-l[j])/risk
        adv=(entry-l[j])/risk if side>0 else (h[j]-entry)/risk
        mfe=max(mfe,fav); mae=min(mae,-adv)
        favpip=((h[j]-entry) if side>0 else (entry-l[j]))/PIP
        for lv in (100,200,300):
            if reach[lv]==0 and favpip>=lv and invalid_at is None: reach[lv]=1
        s_hit=(l[j]<=stop_px) if side>0 else (h[j]>=stop_px)
        if exit_mode=="2R":
            tgt=entry+side*tgtR*risk; t_hit=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
            if s_hit and t_hit: res=-1.0; exit_bar=j; break
            if s_hit: res=-1.0; invalid_at=j; exit_bar=j; break
            if t_hit: res=tgtR; exit_bar=j; break
        elif exit_mode=="struct":
            tgt=entry+side*3.0*risk; t_hit=(h[j]>=tgt) if side>0 else (l[j]<=tgt)
            if s_hit and t_hit: res=-1.0; exit_bar=j; break
            if s_hit: res=-1.0; invalid_at=j; exit_bar=j; break
            if t_hit: res=3.0; exit_bar=j; break
        elif exit_mode=="trail":
            # chandelier: once +1R reached, trail stop to (extreme - 2*ATR); exit on trail hit
            if s_hit: res=-1.0; invalid_at=j; exit_bar=j; break
            if fav>=1.0:
                nt=(h[j]-2*atr[j]) if side>0 else (l[j]+2*atr[j])
                trail=max(trail,nt) if side>0 else min(trail,nt)
            th=(l[j]<=trail) if side>0 else (h[j]>=trail)
            if fav>=1.0 and th: res=(trail-entry)/risk*side; exit_bar=j; break
        elif exit_mode=="time":
            if s_hit: res=-1.0; invalid_at=j; exit_bar=j; break
    if res is None: res=side*(c[exit_bar]-entry)/risk
    return dict(net=res-COST/risk, g=res, mfe_R=mfe, mae_R=mae, risk=risk, k=k, side=side,
                r100=reach[100], r200=reach[200], r300=reach[300], hold=exit_bar-k)

def dedup_episodes(entries, gap=48):
    """Event-level dedup: entries within `gap` M5 bars (~4h) collapse to one independent episode."""
    entries=np.sort(np.asarray(entries)); keep=[]; last=-10**9
    for e in entries:
        if e-last>gap: keep.append(e); last=e
    return np.array(keep)

if __name__=="__main__":
    M=load()
    print(f"M5_DATA_AUDIT: bars={M['n']} start={M['dt'].min()} end={M['dt'].max()} years={sorted(set(M['yr'].tolist()))}")
    print(f"median M5 ATR={np.nanmedian(M['atr']):.3f} (price) = {np.nanmedian(M['atr'])/PIP:.0f} pips ; cost {COST}/risk")
