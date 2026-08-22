"""Phase 2: can early E1-E4 anatomy raise P(A clean 80p) / lower P(B) for PDH families? Undecided-conditioned,
DISC/CONF, remaining room. Fix day-of-week. Decide READY/WEAK/NONE per family."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import pdh_short as PS
h=PS.h;l=PS.l;c=PS.c;o=PS.o;uday=PS.uday;n=PS.n;PIP=PS.PIP;OBJ=PS.OBJ;HOR=PS.HOR
rowsL=PS.rowsL; rowsN=PS.rowsN

# fix DOW (uday is ns) - diagnostic
for rows in (rowsL,rowsN):
    for r in rows: r["dow"]=int(pd.to_datetime(r["day"],unit="ns",utc=True).dayofweek)
print("=== DAY-OF-WEEK P(A clean 80p) FIXED (diagnostic only) ===")
for rows,name in ((rowsL,"L"),(rowsN,"N")):
    s=" ".join(f"{['Mo','Tu','We','Th','Fr','Sa','Su'][d]}:{np.mean([r['cls']=='A_clean' for r in rows if r['dow']==d]) if any(r['dow']==d for r in rows) else float('nan'):.2f}(n{sum(r['dow']==d for r in rows)})" for d in range(7))
    print(f"  {name}: {s}")

def auc(y,x):
    y=np.array(y);x=np.array(x);m=np.isfinite(x);y=y[m];x=x[m];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

def feats(s,k):
    i=s["i"]; P=s["P"]; sweep_hi=h[i]; obj=c[i]-OBJ*PIP; seg=list(range(i+1,i+1+k))
    if seg[-1]>=n or any(uday[j]!=s["day"] for j in seg): return None
    hi=max(h[j] for j in seg); lo=min(l[j] for j in seg); cl=c[seg[-1]]
    resolved="newhi" if hi>sweep_hi else ("obj" if lo<=obj else "undecided")
    return dict(net_prog=(c[i]-cl)/PIP,downside_prog=(c[i]-lo)/PIP,upside_retr=(hi-c[i])/PIP,
                dist_below_pdh=(P-cl)/PIP,dist_to_sweep=(sweep_hi-hi)/PIP,close_below_pdh=float(cl<P),
                last_bear=(o[seg[-1]]-c[seg[-1]])/PIP,failed_ext=float(hi<sweep_hi),
                resolved=resolved,mfe_sofar=(c[i]-lo)/PIP)

def split_rows(rows):
    r2=sorted(rows,key=lambda r:r["i"]); cut=r2[int(len(r2)*0.6)]["i"]
    for r in rows: r["split"]="DISC" if r["i"]<cut else "CONF"
    return rows
FEATS=["net_prog","downside_prog","upside_retr","dist_below_pdh","dist_to_sweep","close_below_pdh","last_bear","failed_ext"]
for rows,name in ((split_rows(rowsL),"FAMILY L / London"),(split_rows(rowsN),"FAMILY N / NewYork")):
    print(f"\n=== {name}: early anatomy A(clean 80p) vs not-A, undecided-at-Ek, DISC/CONF ===")
    for k in (1,2,3,4):
        und=[]
        for s in rows:
            ff=feats(s,k)
            if ff and ff["resolved"]=="undecided": s[f"F{k}"]=ff; und.append(s)
        d=[s for s in und if s["split"]=="DISC"]; cf=[s for s in und if s["split"]=="CONF"]
        bD=np.mean([r["cls"]=="A_clean" for r in d]) if d else np.nan; bC=np.mean([r["cls"]=="A_clean" for r in cf]) if cf else np.nan
        # best stable feature
        best=None
        for f in FEATS:
            ad=auc([int(s["cls"]=="A_clean") for s in d],[s[f"F{k}"][f] for s in d])
            ac=auc([int(s["cls"]=="A_clean") for s in cf],[s[f"F{k}"][f] for s in cf])
            if np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.08 and abs(ac-.5)>.08:
                if best is None or abs(ac-.5)>abs(best[2]-.5): best=(f,ad,ac)
        pct=np.median([ (OBJ-s[f"F{k}"]["mfe_sofar"]) for s in und]) if und else np.nan
        bstr=f"stable-best {best[0]} DISC{best[1]:.2f}/CONF{best[2]:.2f}" if best else "NO stable feature (DISC/CONF sign-flip or weak)"
        print(f"  E{k}: undecided n={len(und)} (DISC {len(d)} baseA={bD:.3f}|CONF {len(cf)} baseA={bC:.3f}) medRemainTo80p={pct:.0f}p | {bstr}")
