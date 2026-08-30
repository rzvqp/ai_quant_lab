"""tsm_ordermotif.py — TEMPORAL_SEQUENCE_MINING_V1 §6B: pure ORDER test via 3-segment ordered-sign motif.

Partition the L-window into 3 equal ordered sub-segments; sign each sub-segment's return -> 27 ordered motif classes. Two paths with
the SAME net move but different ORDER fall in DIFFERENT classes (e.g. [+,+,-] vs [-,+,+]). This is the cleanest test that ORDER matters:
if temporal order carries directional info, some ordered class must show a stable, cost-surviving P(continue)/net-R separation that its
net-matched counterpart does not. Groups are frozen BEFORE outcome. Positive-control column = P(up) which for the leakage check we also
compute per class (should be flat for causal classes). cur_data M15 UTC.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import tsm_core as TC
from tsm_contrast import build_anchors
from tsm_falsify import dir_R

def seg_sign(c, s, t):
    L=t-s; a=s+L//3; b=s+2*L//3
    r1=np.sign(c[a]-c[s]); r2=np.sign(c[b]-c[a]); r3=np.sign(c[t]-c[b])
    return (int(r1),int(r2),int(r3))

def main():
    P=TC.load_panel(); c=P["c"]; n=P["n"]; yr=P["yr"]
    idx=build_anchors(P); L=32; H=32
    lab,_,_,_=TC.triple_barrier(P, idx, b=1.5, H=H)
    rows=[]
    for k,t in enumerate(idx):
        s=t-L
        if s<1: continue
        m=seg_sign(c,s,t); net=c[t]-c[s]; side=1 if net>=0 else -1
        r=dir_R(P,t,side,H)
        if r is None or lab[k]==0:
            if r is None: continue
        up=1 if lab[k]>0 else (0 if lab[k]<0 else -1)
        cont=1 if ((side>0 and lab[k]>0) or (side<0 and lab[k]<0)) else (0 if lab[k]!=0 else -1)
        rows.append((t,m,side,net,r,up,cont))
    T=np.array([x[0] for x in rows]); M=[x[1] for x in rows]; NET=np.array([x[3] for x in rows])
    R=np.array([x[4] for x in rows]); UP=np.array([x[5] for x in rows]); CONT=np.array([x[6] for x in rows])
    era=np.array([P["era"](t) for t in T]); dev=yr[T]<=2019
    # group by ordered motif
    from collections import defaultdict
    g=defaultdict(list)
    for i,m in enumerate(M): g[m].append(i)
    print(f"anchors={len(rows)} ; 3-segment ordered-sign classes populated={len(g)} (max 27)")
    print(f"{'motif':12s} {'N':>6s} {'netR':>7s} {'D':>7s} {'C':>7s} {'O':>7s} {'DEV':>7s} {'OOS':>7s} {'Pcont':>6s} {'Pup':>6s}")
    # ORDER pairs: compare net-matched reversals of order, e.g. (+,+,-) vs (-,+,+) share net sign but differ in order
    best=[]
    for m,ii in sorted(g.items(), key=lambda kv:-len(kv[1])):
        ii=np.array(ii)
        if len(ii)<150: continue
        rr=R[ii]; e=era[ii]; dv=dev[ii]; ct=CONT[ii]; upp=UP[ii]
        def mn(mask): return rr[mask].mean() if mask.sum()>0 else np.nan
        row=(m,len(ii),rr.mean(),mn(e=='D'),mn(e=='C'),mn(e=='O'),mn(dv),mn(~dv),(ct[ct>=0]>0).mean(),(upp[upp>=0]>0).mean())
        best.append(row)
        print(f"{str(m):12s} {len(ii):6d} {rr.mean():+.3f} {mn(e=='D'):+.3f} {mn(e=='C'):+.3f} {mn(e=='O'):+.3f} {mn(dv):+.3f} {mn(~dv):+.3f} {(ct[ct>=0]>0).mean():.3f} {(upp[upp>=0]>0).mean():.3f}")
    # explicit ORDER-matters check: for each net-sign, does the ordered-class net-R spread exceed cost-relevant threshold, sign-stable?
    surv=[r for r in best if r[2]>0 and np.sign(r[3])==np.sign(r[4])==np.sign(r[5])==1 and r[6]>0 and r[7]>0]
    print(f"\nORDERED classes with net-positive cost-surviving cross-era-stable net-R: {len(surv)}")
    for r in surv: print("   SURVIVOR", r)
    # pure order contrast: mean netR of 'late-energy' orders (last seg dominant) vs 'early-energy' (first seg dominant), net-matched
    print("\npure-order contrast (same 3 signs, different position of the strong segment) handled by class table above.")

if __name__=="__main__":
    main()
