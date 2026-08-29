"""volpath_phase2.py — VOLPATH Phase-2 BOUNDED falsification of the two Phase-1 candidates. §14 redundancy check FIRST. Full STRESS cost.
D-FAMILY (post-classification momentum entry): from a mature compression, wait for the first range break + a confirmed 2-bar follow-
through (close >= 0.3ATR beyond the break level in break dir), then ENTER in that direction (next-bar open). Compare to the RAW breakout
BASELINE (VOLTIME-2, no confirmation) with the SAME stop/target — if post-classification does NOT beat the raw breakout net, it is
REDUNDANT_WITH_PREVIOUSLY_CLOSED_FRONTIER. B-FAMILY (range-boundary straddle): both sides armed at rHi/rLo; two-sided spread cost;
measure both-side-activation, double-loss, net. STRESS 0.24 (single-side); straddle pays cost per activated side. Blocks D/C/O. No mining."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; H=48; M=16
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy()
    comp=(atr<atr_ma).astype(int); cd=np.zeros(n,int)
    for i in range(1,n): cd[i]=cd[i-1]+1 if comp[i] else 0
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    ev=[]; last=-10**9
    for T in range(60,n-H-M-6):
        if cd[T]>=12 and np.isfinite(atr[T]) and atr[T]>0 and T-last>=H: ev.append(T); last=T
    def bracket(entry,stop,tgt,dirn,ei):
        segl=l[ei:ei+H]; segh=h[ei:ei+H]
        if dirn>0: fs=np.where(segl<=stop)[0]; ft=np.where(segh>=tgt)[0]
        else: fs=np.where(segh>=stop)[0]; ft=np.where(segl<=tgt)[0]
        fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
        if fstop==ftgt==10**9: return None
        rr=abs(tgt-entry)/abs(entry-stop)
        return rr if ftgt<fstop else -1.0
    RAW=[]; PC=[]  # (era,R)
    strad=[]       # per-event straddle outcome
    for T in ev:
        a=atr[T]; W=min(cd[T],40); rHi=np.max(h[T-W+1:T+1]); rLo=np.min(l[T-W+1:T+1]); e=era(T)
        # first break within M bars
        fb=None
        for j in range(T+1,T+1+M):
            if c[j]>rHi: fb=(j,1,rHi); break
            if c[j]<rLo: fb=(j,-1,rLo); break
        if fb:
            j,dirn,lvl=fb; stop=(rLo-0.1*a) if dirn>0 else (rHi+0.1*a)
            # RAW breakout baseline: enter next bar after break
            ei=j+1
            if ei<n-H:
                entry=o[ei]; risk=abs(entry-stop)
                if risk>0.05*a:
                    tgt=entry+2*risk*dirn; r=bracket(entry,stop,tgt,dirn,ei)
                    if r is not None: RAW.append((e,r))
            # POST-CLASSIFICATION: require 2-bar follow-through >=0.3ATR beyond lvl in dir, then enter
            if j+2<n and ((c[j+2]-lvl)*dirn)>=0.3*a:
                ei2=j+3
                if ei2<n-H:
                    entry=o[ei2]; risk=abs(entry-stop)
                    if risk>0.05*a:
                        tgt=entry+2*risk*dirn; r=bracket(entry,stop,tgt,dirn,ei2)
                        if r is not None: PC.append((e,r))
        # STRADDLE at range boundaries (both armed): long@rHi target rHi+1.5ATR stop rLo; short mirror; 2-sided
        segh=h[T+1:T+1+H]; segl=l[T+1:T+1+H]
        up_hit=np.where(segh>=rHi)[0]; dn_hit=np.where(segl>=-1)[0]  # placeholder
        dn_hit=np.where(segl<=rLo)[0]
        def side_R(trig_arr, dirn, lvl, opp):
            if len(trig_arr)==0: return None
            b=trig_arr[0]; ei=T+1+b
            entry=lvl; risk=abs(entry-opp)  # stop at opposite boundary
            tgt=entry+1.5*a*dirn
            if risk<=0.05*a: return None
            r=bracket(entry,opp,tgt,dirn,ei)
            return r
        rL=side_R(up_hit,1,rHi,rLo-0.1*a); rS=side_R(dn_hit,-1,rLo,rHi+0.1*a)
        acts=[x for x in [rL,rS] if x is not None]
        if acts:
            both=(rL is not None and rS is not None)
            net=sum(acts) - COST*len(acts)  # spread per activated side
            strad.append((e,net,both))
    def enet(rows):
        return np.mean([x[1]-COST for x in rows]) if rows else float('nan')
    st=lambda a:(len(a), enet(a))
    def line(name,rows):
        N,net=st(rows)
        parts=[]
        for e in ["D","C","O"]:
            d=[x for x in rows if x[0]==e]; parts.append(f"{e}={enet(d):+.3f}")
        return f"{name:26s}: n={N:4d} netR={net:+.3f} | "+" ".join(parts)
    print("VOLPATH Phase-2 (STRESS 0.24). §14 redundancy: post-classification must BEAT the raw breakout to be non-redundant.")
    print("  "+line("RAW breakout (baseline)",RAW))
    print("  "+line("POST-CLASSIFICATION (D)",PC))
    # straddle
    N=len(strad); both=np.mean([x[2] for x in strad]) if strad else float('nan'); net=np.mean([x[1] for x in strad]) if strad else float('nan')
    es=" ".join(f"{e}={np.mean([x[1] for x in strad if x[0]==e]):+.3f}" for e in ["D","C","O"])
    print(f"  STRADDLE range-boundary   : n={N:4d} netR/event={net:+.3f} both-side-activation={both:.3f} | {es}")
    rawnet=st(RAW)[1]; pcnet=st(PC)[1]
    print(f"\nREDUNDANCY VERDICT: post-classification net {pcnet:+.3f} vs raw breakout {rawnet:+.3f} -> "+
          ("BEATS baseline (non-redundant, investigate)" if (pcnet>rawnet+0.03 and pcnet>0) else "does NOT beat baseline / still net-negative = REDUNDANT_WITH_PREVIOUSLY_CLOSED_FRONTIER"))
    print("=> if both candidates net<=0 cross-era (and PC not > baseline) -> VOLPATH closes as information-only (no monetizable path asymmetry).")
if __name__=="__main__": main()
