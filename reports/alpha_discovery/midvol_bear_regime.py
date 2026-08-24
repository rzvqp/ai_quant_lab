"""midvol_bear_regime.py — FROZEN causal MIDVOL_BEAR regime (portfolio regime #4) + inline info test. Structural: MODERATE
causal vol + negative trend (ema-down, effic<0) = a controlled/orderly downtrend (distinct from CRS-1's HIGH-vol crash
correction, from RANGE low-effic, from the bull regimes). REGIME FROZEN BEFORE P&L. Causal normalization (trailing vol
baseline shift(1), bounded effic, no global pct). Info test (SHORT lens): does the regime supply era-consistent DOWN-
continuation? Params structural, pre-P&L: W=360, WARM=400, vol band [0.85,1.20), E_BEAR=0.30, N_ENTER=4. Data thru 2026-07-27.
"""
import numpy as np, pandas as pd
import cur_data as CD
from cur_cr2 import fwd
W=360; WARM=400; VLOW=0.85; VHIGH=1.20; E_BEAR=0.30; N_ENTER=4
FP="MIDVOL_BEAR_V1|H4|volratioTRAIL360|band0.85-1.20|Ebear0.30|Nenter4|causal-trailing"

def build_h4(h4):
    e20=h4["ema20"].to_numpy(); e50=h4["ema50"].to_numpy(); eff=h4["effic"].to_numpy(); atr=h4["atr"].to_numpy(); n=len(h4)
    base=pd.Series(atr).rolling(W).median().shift(1).to_numpy(); vr=atr/base
    bear_bar=(e20<e50)&(eff<-E_BEAR)&(vr>=VLOW)&(vr<VHIGH)
    hold=(e20<e50)&(eff<0)&(vr<VHIGH+0.15)
    on=np.zeros(n,bool); state=0; cnt=0
    for t in range(n):
        if t<WARM or not np.isfinite(vr[t]) or not np.isfinite(eff[t]):
            state=0; cnt=0; continue
        if state==0:
            if bear_bar[t]:
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

def episodes(mask):
    idx=np.where(mask)[0]
    if len(idx)==0: return 0,0
    lens=[]; start=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i-prev>1: lens.append(prev-start+1); start=i
        prev=i
    lens.append(prev-start+1)
    return len(lens), int(np.median(lens))

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); on,_=build_h4(h4); yr4=h4["dt"].dt.year.to_numpy()
    n=len(h4); c=int(on.sum()); nep,ml=episodes(on)
    print(f"FROZEN MIDVOL_BEAR regime V1  fp={FP}")
    print(f"  H4 on bars: {c}/{n} ({100*c/n:.1f}%) | episodes {nep} | median episode {ml} H4 bars (~{ml/6:.1f} days)")
    print("  on% by year:", {int(y):int(100*((yr4==y)&on).sum()/max(1,(yr4==y).sum())) for y in range(2012,2027) if (yr4==y).sum()>50})
    onm=map_to_m15(m,h4,on); up,dn,af=fwd(m); reg=(onm==1); yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)
    cl=m["close"].to_numpy(); fret=(pd.Series(cl).shift(-96).to_numpy()-cl)/m["atr"].to_numpy()
    def row(msk):
        nn=int(msk.sum())
        if nn<150: return f"n={nn}(thin)"
        afr=af[msk]; pdf=float((afr[afr!=0]==-1).mean()) if (afr!=0).sum() else float('nan')
        return f"n={nn:6d} dn-up={np.median(dn[msk])-np.median(up[msk]):+.2f} P(downFirst)={pdf:.3f} fwdRet={np.nanmedian(fret[msk]):+.2f}ATR"
    print("  INFO (SHORT lens; dn-up>0 & P(downFirst)>0.5 & fwdRet<0 = down-continuation):")
    print("    ON       :", row(reg&ok))
    for lab,ym in [("DISC<=2021",yr<=2021),("CONF 22-24",(yr>=2022)&(yr<=2024)),("OOS 25-26",yr>=2025)]:
        print(f"    ON {lab:10s}:", row(reg&ok&ym))

if __name__=="__main__":
    main()
