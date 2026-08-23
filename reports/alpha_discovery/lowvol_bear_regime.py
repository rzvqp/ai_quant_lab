"""lowvol_bear_regime.py — FROZEN causal LOWVOL_BEAR regime (portfolio regime #6, completes the single-axis taxonomy) +
inline info + quick screen. Structural: LOW causal vol + negative trend = a slow orderly decline. FROZEN BEFORE P&L. Causal.
Params structural: W=360, WARM=400, VLO_HI=0.95, E_BEAR=0.30, N_ENTER=4. Data through 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD, swing_base as sb
from cur_cr2 import fwd
W=360; WARM=400; VLO_HI=0.95; E_BEAR=0.30; N_ENTER=4
FP="LOWVOL_BEAR_V1|H4|volratioTRAIL360|VLOhi0.95|Ebear0.30|Nenter4|causal-trailing"

def build_h4(h4):
    e20=h4["ema20"].to_numpy(); e50=h4["ema50"].to_numpy(); eff=h4["effic"].to_numpy(); atr=h4["atr"].to_numpy(); n=len(h4)
    base=pd.Series(atr).rolling(W).median().shift(1).to_numpy(); vr=atr/base
    bb=(e20<e50)&(eff<-E_BEAR)&(vr<=VLO_HI); hold=(e20<e50)&(eff<0)&(vr<=1.05)
    on=np.zeros(n,bool); state=0; cnt=0
    for t in range(n):
        if t<WARM or not np.isfinite(vr[t]) or not np.isfinite(eff[t]): state=0; cnt=0; continue
        if state==0:
            if bb[t]:
                cnt+=1
                if cnt>=N_ENTER: state=1; on[t]=True
            else: cnt=0
        else:
            if hold[t]: on[t]=True
            else: state=0; cnt=0
    return on, vr

def map_to_m15(m, h4, on):
    hm=pd.DataFrame({"close_time":h4["close_time"].to_numpy(),"on":on.astype(float)}).sort_values("close_time")
    mm=pd.DataFrame({"time":m["time"].to_numpy()}).sort_values("time")
    return pd.merge_asof(mm,hm,left_on="time",right_on="close_time",direction="backward").sort_index()["on"].to_numpy()

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=build_h4(h4); c=int(on.sum())
    idx=np.where(on)[0]; lens=[]
    if len(idx):
        s=idx[0]; p=idx[0]
        for i in idx[1:]:
            if i-p>1: lens.append(p-s+1); s=i
            p=i
        lens.append(p-s+1)
    print(f"FROZEN LOWVOL_BEAR regime V1  fp={FP}")
    print(f"  H4 on: {c}/{len(h4)} ({100*c/len(h4):.1f}%) episodes {len(lens)} median {int(np.median(lens)) if lens else 0} H4 bars")
    onm=map_to_m15(m,h4,on); up,dn,af=fwd(m); reg=(onm==1); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    cl=m["close"].to_numpy(); fret=(pd.Series(cl).shift(-96).to_numpy()-cl)/m["atr"].to_numpy()
    def row(msk):
        nn=int(msk.sum())
        if nn<150: return f"n={nn}(thin)"
        return f"n={nn:6d} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f} fwdRet={np.nanmedian(fret[msk]):+.2f}ATR"
    print("  INFO (SHORT lens):  ON:", row(reg&ok))
    for lab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
        print(f"    {lab}:", row(reg&ok&ym))
    atr=m["atr"].to_numpy(); reg2=reg&np.isfinite(atr)&(atr>0)
    def screen(idx,side,sm,rr,name):
        n=len(m); idx=idx[idx<n-1]; dd=sb.dedup_events(idx,12); idx=idx[np.isin(idx,dd)]; sl=sm*atr[idx]
        tr=sb.simulate(m,idx,side,sl,rr=rr,horizon=96,scenario="STRESS"); r=tr["R"].to_numpy()
        y=pd.Series(pd.to_datetime(tr["t_entry"],unit="s",utc=True)).dt.year.to_numpy()
        if len(r)<40: print(f"    {name}: thin"); return
        sr=np.sort(r); k=max(1,len(r)//10); d=r[y<=2021]; cf=r[(y>=2022)&(y<=2024)]; o=r[y>=2025]
        sv=len(r)>=60 and d.mean()>0 and cf.mean()>0 and (len(o)==0 or o.mean()>0) and sr[:-k].mean()>0
        print(f"    {name}: N={len(r)} avgR={r.mean():+.4f} best10rm={sr[:-k].mean():+.4f} | D {d.mean():+.3f} C {cf.mean():+.3f} O {o.mean():+.3f} -> {'SURVIVOR' if sv else 'no'}")
    print("  TRADEABLE:")
    screen(np.where(reg2)[0],-1,1.5,2.0,"regime SHORT 1.5ATR rr2")
    screen(np.where(reg2)[0],-1,2.5,2.0,"regime SHORT 2.5ATR rr2")

if __name__=="__main__":
    main()
