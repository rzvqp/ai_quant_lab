"""frontier_m.py — FRONTIER M: PATH-SURVIVAL study (R26 direct test). A displacement bar is a direction-RESOLVING
structural event (the bar commits a direction). R26 says the failure of such events is PATH-SURVIVAL (adverse-first
whipsaw), and that liquidity/session state governs path survival. Info-first: for displacement-UP (commit LONG) and
displacement-DN (commit SHORT), measure the forward continuation asymmetry P(+70/-50 commit) - P(opposite) AND the
adverse-first rate, per (session x vol-expansion) cell, CROSS-ERA. A path-surviving directional cell = continuation
asym materially + same-sign across eras. If none: path-survival does NOT rescue direction (R26 confirmed). No P&L in
the conditioning (session/vol are causal event-time). Uses passage first-passage.
"""
import numpy as np, pandas as pd, bscreen as bs
from state_path_m15 import passage_m15, Pm
from batch_a import _hr_day
HB=48
SESS=[("Asia",0,7),("Lon",7,13),("NY",13,21)]

def disp(fr, up):
    o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); atr=fr["atr"].to_numpy(); rng=h-l
    if up: return ((c-o)>0.7*atr)&(c>l+0.75*rng)&(rng>1.2*atr)
    else:  return ((o-c)>0.7*atr)&(c<l+0.25*rng)&(rng>1.2*atr)

def main():
    print(f"Frontier M PATH-SURVIVAL: displacement continuation asym P(+70/-50 commit)-P(opp) per session x vol, cross-era. H={HB//4}h.")
    eras=bs.build_eras(); frames={}
    for tag,fr,mask in eras: frames.setdefault(id(fr),fr)
    PSG={k:passage_m15(v,Hmax=HB) for k,v in frames.items()}
    for up in (True,False):
        cd='L' if up else 'S'; opp='S' if up else 'L'
        print(f"\n=== displacement {'UP->LONG' if up else 'DN->SHORT'} (commit {cd}) ===")
        for nm,lo,hi in SESS:
            for vexp,vlab in ((True,"exp"),(False,"cmp")):
                cells=[]; signs=[]
                for tag,fr,mask in eras:
                    ou,od,mfe,mae=PSG[id(fr)]; hr,_,_=_hr_day(fr); vr=(fr["atr"]/fr["atr_ma"]).to_numpy()
                    ev=disp(fr,up)&(hr>=lo)&(hr<hi)&((vr>=1.0) if vexp else (vr<1.0))
                    ev=mask&np.nan_to_num(ev.astype(float),nan=0).astype(bool)
                    idx=np.where(ev)[0]; idx=idx[idx<len(fr)-1]
                    if len(idx)<40: cells.append(f"{tag}:n{len(idx)}"); signs.append(0); continue
                    mm=np.zeros(len(fr),bool); mm[idx]=True
                    a=Pm(ou,od,70,50,cd,HB,mm)[0]-Pm(ou,od,70,50,opp,HB,mm)[0]
                    af=float((mae[idx]>=50).mean())  # adverse-first proxy: hit -50p at some point
                    cells.append(f"{tag}:{a:+.2f}(af{af:.2f})"); signs.append(np.sign(a) if abs(a)>=0.05 else 0)
                nz=[s for s in signs if s!=0]; want=1 if up else -1  # commit-consistent sign
                stable=len(nz)>=3 and len(set(nz))==1 and nz[0]==want
                flag=" <== PATH-SURVIVING CROSS-ERA" if stable else ""
                print(f"  {nm:4s}/{vlab}: "+"  ".join(cells)+flag)

if __name__=="__main__":
    main()
