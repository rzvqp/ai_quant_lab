"""Phase 2: does early anatomy (E1/E2) discriminate CLEAN (A) from NEW_HIGH_FIRST/CONTINUATION among the
best family L/Pre-London-High? DISC/CONF, undecided-conditioned, remaining room. Confirm F & L/AsiaHigh weak.
Addendum ranking: P(A) high + P(B) low + room + temporal + N. NO execution."""
import sys, os, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import frank_london as FL
h=FL.h;l=FL.l;c=FL.c;o=FL.o;uday=FL.uday;n=FL.n;PIP=FL.PIP;HOR=FL.HOR
rowsLPL=FL.rowsLPL; rowsF=FL.rowsF; rowsLAH=FL.rowsLAH

def auc(y,x):
    y=np.array(y);x=np.array(x);m=np.isfinite(x);y=y[m];x=x[m];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)

# E1/E2 anatomy features (info available at landmark; level L = the swept level)
def feats(s,k):
    i=s["i"]; L=s["L"]; sweep_hi=h[i]; seg=list(range(i+1,i+1+k))
    if seg[-1]>=n or any(uday[j]!=s["day"] for j in seg): return None
    hi=max(h[j] for j in seg); lo=min(l[j] for j in seg); cl=c[seg[-1]]
    return dict(
        net_prog=(c[i]-cl)/PIP, downside_prog=(c[i]-lo)/PIP, upside_retr=(hi-c[i])/PIP,
        dist_below_L=(L-cl)/PIP, dist_to_sweep=(sweep_hi-hi)/PIP, close_below_L=float(cl<L),
        last_bear=(o[seg[-1]]-c[seg[-1]])/PIP, failed_ext=float(hi<sweep_hi),
        resolved=("newhi" if hi>sweep_hi else ("mid" if lo<=s["amid"] else "undecided")),
        remaining=(cl-s["amid"])/PIP)

# DISC/CONF split by day across L/PLL
def split_rows(rows):
    r2=sorted(rows,key=lambda r:r["i"]); cut=r2[int(len(r2)*0.6)]["i"]
    for r in rows: r["split"]="DISC" if r["i"]<cut else "CONF"
    return rows
rowsLPL=split_rows(rowsLPL)

print("=== L/Pre-London-High: early anatomy discriminates A(clean) vs NOT-A, at E1/E2 (undecided-conditioned) ===")
FEATS=["net_prog","downside_prog","upside_retr","dist_below_L","dist_to_sweep","close_below_L","last_bear","failed_ext"]
for k in (1,2):
    und=[]
    for s in rowsLPL:
        ff=feats(s,k)
        if ff and ff["resolved"]=="undecided": s[f"F{k}"]=ff; und.append(s)
    d=[s for s in und if s["split"]=="DISC"]; cf=[s for s in und if s["split"]=="CONF"]
    baseD=np.mean([r["cls"]=="A_clean" for r in d]) if d else np.nan
    baseC=np.mean([r["cls"]=="A_clean" for r in cf]) if cf else np.nan
    rem=np.median([s[f"F{k}"]["remaining"] for s in und])
    print(f"  E{k}: undecided n={len(und)} (DISC {len(d)} baseA={baseD:.3f} | CONF {len(cf)} baseA={baseC:.3f}) medRemain={rem:.1f}p")
    for f in FEATS:
        yd=[int(s["cls"]=="A_clean") for s in d]; xd=[s[f"F{k}"][f] for s in d]
        yc=[int(s["cls"]=="A_clean") for s in cf]; xc=[s[f"F{k}"][f] for s in cf]
        ad=auc(yd,xd); ac=auc(yc,xc)
        flag="  stable" if (np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.06 and abs(ac-.5)>.06) else ""
        print(f"     {f:14} DISC AUC={ad:.2f} CONF AUC={ac:.2f}{flag}")

# simple rule on L/PLH undecided-at-E1: net downside>0 AND close below L
print("\n=== L/PLH simple rule (E1): net downside>0 AND close-below-PreLondonHigh -> P(A clean) ===")
und=[s for s in rowsLPL if feats(s,1) and feats(s,1)["resolved"]=="undecided"]
for s in und: s["F1"]=feats(s,1)
for tag in ("DISC","CONF"):
    g=[s for s in und if s["split"]==tag]; base=np.mean([s["cls"]=="A_clean" for s in g]) if g else np.nan
    sel=[s for s in g if s["F1"]["net_prog"]>0 and s["F1"]["close_below_L"]>0]
    if sel:
        pA=np.mean([s["cls"]=="A_clean" for s in sel]); pB=np.mean([s["cls"]=="B_newhi_then_mid" for s in sel])
        rem=np.median([s["F1"]["remaining"] for s in sel])
        print(f"  {tag}: n{len(sel)} P(A)={pA:.3f} (base {base:.3f}, lift {pA-base:+.3f}) P(B)={pB:.3f} medRemain={rem:.1f}p")
    else: print(f"  {tag}: n0")

# addendum full class table for the 3 sub-populations (compact)
print("\n=== ADDENDUM CLASS TABLE (N | A | B | C | D | P(mid) | P(low) | medRemain) ===")
from collections import Counter
for rows,name in ((rowsF,"F/AsiaHigh"),(rowsLAH,"L/AsiaHigh"),(rowsLPL,"L/PreLondonHigh")):
    N=len(rows); cc=Counter(r["cls"] for r in rows)
    print(f"  {name:16}: N{N} A{cc['A_clean']/N:.3f} B{cc['B_newhi_then_mid']/N:.3f} C{cc['C_continuation']/N:.3f} D{cc['D_stalled']/N:.3f} "
          f"mid{np.mean([r['reach_mid'] for r in rows]):.3f} low{np.mean([r['reach_low'] for r in rows]):.3f} rem{np.median([r['remaining'] for r in rows]):.0f}p")
