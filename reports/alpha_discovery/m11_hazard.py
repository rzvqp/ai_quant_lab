"""m11_hazard.py — M11 PATH/HAZARD (info-first): duration-in-state branch. In a causal ema-up state (ema20>ema50), does the
target-before-stop ORDERING P(up 1.5ATR before dn 1.5ATR) change materially with DURATION since state onset — and is any
duration band robustly directional across eras (not era-split)? Pure price, causal. Data cur_data M15 2011-2026."""
import numpy as np, pandas as pd
import cur_data as CD
from cur_cr2 import fwd
def main():
    m=CD.load_m15(); e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); n=len(m)
    up_state=e20>e50; onset=up_state&~np.r_[False,up_state[:-1]]
    age=np.full(n,-1); k=-1
    for i in range(n):
        if onset[i]: k=0
        elif up_state[i] and k>=0: k+=1
        elif not up_state[i]: k=-1
        age[i]=k
    up,dn,af=fwd(m); yr=m["dt"].dt.year.to_numpy(); ok=(af!=0)&up_state&(age>=0)
    def pup(msk):
        a=af[msk]; return (float((a==1).mean()), int(msk.sum())) if msk.sum()>=200 else (float('nan'),int(msk.sum()))
    print("M11 hazard: P(up-1.5ATR-first) in ema-up state by DURATION band [ALL | D<=2018 | C19-22 | O23+]:")
    for lab,am in [("age 0-8",(age>=0)&(age<=8)),("age 9-48",(age>=9)&(age<=48)),("age 49-192",(age>=49)&(age<=192)),("age 193+",age>=193)]:
        row=f"  {lab:10s}:"
        for pl,ym in [("ALL",np.ones(n,bool)),("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            p,nn=pup(ok&am&ym); row+=f" {pl} {p:.3f}(n{nn})" if nn>=200 else f" {pl} thin"
        print(row)
    print("  => M11 duration edge only if a band's P(up1st) is robustly >0.5 (or <0.5) across ALL eras (not era-split).")
if __name__=="__main__": main()
