"""m04_rotation.py — M04 range-rotation branch (info-first): in a confirmed RANGE (RANGE_REGIME_V1), does price ROTATE boundary
-to-boundary (enter at one boundary, reach the OTHER before breaking out)? P(reach opposite boundary before stop-out beyond entry
boundary), by side, partitioned. Distinct from boundary-fade-to-mid (RS-1). Pure price + frozen RANGE regime. Data 2011-2026."""
import numpy as np, pandas as pd
import cur_data as CD, range_regime as RR
def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4"); inr,rlo,rhi=RR.build_h4_range(h4)
    i,lo_,hi_,mid_=RR.map_to_m15(m,h4,inr,rlo,rhi)
    hi=m["high"].to_numpy(); lo=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy()
    wid=hi_-lo_; reg=(i==1)&np.isfinite(wid)&(wid>0)
    # at lower-boundary touch -> rotate up to upper; at upper-boundary touch -> rotate down to lower
    lo_touch=reg&(lo<=lo_+0.1*wid)&(c>lo_); up_touch=reg&(hi>=hi_-0.1*wid)&(c<hi_)
    def rotate(idx, side):  # side=+1 target upper (long), -1 target lower (short)
        res=[]
        for k in np.where(idx)[0]:
            if k>=n-1: continue
            tgt=hi_[k] if side>0 else lo_[k]; stp=lo_[k]-0.25*wid[k] if side>0 else hi_[k]+0.25*wid[k]
            end=min(k+1+96,n); r=0
            for j in range(k+1,end):
                if (side>0 and hi[j]>=tgt) or (side<0 and lo[j]<=tgt): r=1; break
                if (side>0 and lo[j]<=stp) or (side<0 and hi[j]>=stp): r=-1; break
            res.append((k,r))
        return res
    for nm,idx,side in [("LOWER->rotate UP",lo_touch,1),("UPPER->rotate DN",up_touch,-1)]:
        rr=rotate(idx,side); rr=[(k,r) for k,r in rr if r!=0]
        if len(rr)<150: print(f"  {nm}: n={len(rr)} thin"); continue
        ks=np.array([k for k,_ in rr]); rs=np.array([r for _,r in rr])
        line=f"  {nm}: n={len(rr)} P(reach opposite first)={float((rs==1).mean()):.3f}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            mk=ym[ks]; p=float((rs[mk]==1).mean()) if mk.sum()>=100 else float('nan'); line+=f" | {pl} {p:.3f}"
        print(line)
    print("  => rotation edge only if P(reach opposite first)>0.5 robustly (range rotates, not breaks).")
if __name__=="__main__": main()
