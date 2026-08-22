"""ALPHA-XAUUSD-LONDON-PLH-FIXED80-CLEAN-PATH-001. Relabel the UNCHANGED London/Pre-London-High parent
(recovered from frank_london.py / 50b099d, N~133) with a POSITION-INDEPENDENT fixed-80-project-pip clean-path
target. LABEL RECONSTRUCTION + BASE-RATE ONLY (no feature mining / classifier / execution).
Frozen: E0 reference = sweep-bar close; objective = ref - 80p; sweep_high = high[E0]; horizon = 96 M5 (8h)
same-UTC-day. Same-bar (new-high AND objective) = AMBIGUOUS, reported separately (no optimistic CLEAN)."""
import sys, os, numpy as np
DSTp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DSTp not in sys.path: sys.path.insert(0,DSTp)
import frank_london as FL
h=FL.h;l=FL.l;c=FL.c;o=FL.o;uday=FL.uday;n=FL.n;PIP=FL.PIP;yr=FL.yr
P=FL.FAM_LPL   # 133 canonical parents (UNCHANGED), each: day,i,L(PLH),ah,al,amid,yr,lonh...
HOR=96  # frozen: 96 M5 bars (8h) OR same-UTC-day, whichever first
print(f"PARENT (unchanged, from 50b099d): N={len(P)} unique_days={len(set(p['day'] for p in P))}")

def classify(p, dist_p):
    i=p["i"]; sweep_hi=h[i]; ref=c[i]; obj=ref-dist_p*PIP; day=p["day"]; e1=i+1
    if e1>=n: return None
    new_high=False; cls=None; amb=False
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        hh=h[j]>sweep_hi; ho=l[j]<=obj
        if ho and hh and not new_high:      # first resolving bar hits BOTH, no prior new high -> ambiguous
            amb=True; cls="AMB"; break
        if ho: cls="A_clean" if not new_high else "B_newhi_then_obj"; break
        if hh: new_high=True
    if cls is None: cls="C_continuation" if new_high else "D_stalled"
    return cls

# eventual MFE (max downside from ref, same-day 96) + time-to-80p
def diag(p):
    i=p["i"]; ref=c[i]; day=p["day"]; e1=i+1; mfe=0.0; t80=None
    for k,j in enumerate(range(e1,min(e1+HOR,n))):
        if uday[j]!=day: break
        d=(ref-l[j])/PIP; mfe=max(mfe,d)
        if t80 is None and d>=80: t80=k+1
    return mfe,t80

rows=[]
for p in P:
    cls=classify(p,80.0)
    if cls is None: continue
    mfe,t80=diag(p)
    rows.append({**p, "cls":cls, "mfe":mfe, "t80":t80})
from collections import Counter
N=len(rows); cc=Counter(r["cls"] for r in rows); f=lambda k:cc[k]/N
print(f"\n=== FIXED-80p CLEAN-PATH BASE RATES (E0=sweep close, obj=ref-80p, sweep_hi=high[E0], HOR=96 M5/8h same-day) ===")
print(f"  N={N}  P(A CLEAN_80)={f('A_clean'):.3f}  P(B new-high-first->80)={f('B_newhi_then_obj'):.3f}  P(C continuation)={f('C_continuation'):.3f}  P(D stalled)={f('D_stalled'):.3f}  P(AMB same-bar)={f('AMB'):.3f}")
print(f"  eventual MFE>=80p (any path) = {np.mean([r['mfe']>=80 for r in rows]):.3f}  (distinguishes TARGET-NOT-AVAILABLE from RIGHT-DIR/BAD-PATH)")

print("\n=== SECONDARY MAGNITUDE DIAGNOSTICS (clean-before-new-high rate at each distance; 80p PRIMARY) ===")
for dP in (30,50,80,100,150):
    cA=np.mean([classify(p,float(dP))=="A_clean" for p in P if classify(p,float(dP)) is not None])
    mfe_ok=np.mean([diag(p)[0]>=dP for p in P])
    print(f"  {dP:3d}p: P(clean_before_newhigh)={cA:.3f} | eventual MFE>={dP}p={mfe_ok:.3f}")

print("\n=== YEAR-BY-YEAR (fixed80) ===")
for y in (2021,2022,2023):
    ry=[r for r in rows if yr[r["i"]]==y]
    if ry:
        m=len(ry); g=lambda k:sum(r["cls"]==k for r in ry)/m
        print(f"  {y}: N={m} A={g('A_clean'):.3f} B={g('B_newhi_then_obj'):.3f} C={g('C_continuation'):.3f} D={g('D_stalled'):.3f} AMB={g('AMB'):.3f} | MFE>=80p={np.mean([r['mfe']>=80 for r in ry]):.3f}")

# DISC/CONF (chronological, same structure as frank_london)
rows_s=sorted(rows,key=lambda r:r["i"]); cut=rows_s[int(len(rows_s)*0.6)]["i"]
for r in rows: r["split"]="DISC" if r["i"]<cut else "CONF"
print("\n=== DISC / CONF (fixed80) ===")
for tag in ("DISC","CONF"):
    g=[r for r in rows if r["split"]==tag]; m=len(g); ff=lambda k:sum(r["cls"]==k for r in g)/m
    print(f"  {tag}: N={m} P(A)={ff('A_clean'):.3f} P(B)={ff('B_newhi_then_obj'):.3f} P(C)={ff('C_continuation'):.3f} MFE>=80p={np.mean([r['mfe']>=80 for r in g]):.3f}")

# failed acceptance (exact prior def: close back below PLH within E0-E2) under fixed80
def failed_accept(p):
    for k in (p["i"],p["i"]+1,p["i"]+2):
        if k<n and uday[k]==p["day"] and c[k]<p["L"]: return True
    return False
print("\n=== FAILED ACCEPTANCE (prior def, unchanged) under fixed80 ===")
for lbl,cond in (("ALL",lambda r:True),("failed_acc=TRUE",lambda r:failed_accept(r)),("failed_acc=FALSE",lambda r:not failed_accept(r))):
    g=[r for r in rows if cond(r)]; m=len(g)
    if m: ff=lambda k:sum(r["cls"]==k for r in g)/m; print(f"  {lbl:16}: N={m} P(A)={ff('A_clean'):.3f} P(B)={ff('B_newhi_then_obj'):.3f} P(C)={ff('C_continuation'):.3f} P(D)={ff('D_stalled'):.3f}")

# existing-feature SANITY (no new mining): AUC(A vs B+C) under fixed80
def auc(y,x):
    y=np.array(y);x=np.array(x,float);mm=np.isfinite(x);y=y[mm];x=x[mm];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    r=np.argsort(np.argsort(x))+1; return (r[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def rng(i): return max(h[i]-l[i],1e-9)
def feat(p,name):
    i=p["i"]
    if name=="plh_minus_asiahigh": return (p["L"]-p["ah"])/PIP
    if name=="upper_wick": return (h[i]-max(o[i],c[i]))/rng(i)
    if name=="close_loc": return (c[i]-l[i])/rng(i)
    if name=="sweep_excursion": return (h[i]-p["L"])/PIP
    if name=="approach_vel": return (c[i]-c[i-3])/PIP if i>=3 else np.nan
    if name=="failed_ext": return float(h[i+1]<h[i]) if i+1<n else np.nan     # E1 fails to extend sweep high
    if name=="early_downside": return (c[i]-c[i+1])/PIP if i+1<n else np.nan  # E1 net downside
    return np.nan
lab=lambda r: 1 if r["cls"]=="A_clean" else (0 if r["cls"] in ("B_newhi_then_obj","C_continuation") else -1)
gg=[r for r in rows if lab(r)>=0]
print("\n=== EXISTING-FEATURE SANITY under fixed80 (AUC A vs B+C; overall/DISC/CONF) -- NO new mining ===")
for fn in ("plh_minus_asiahigh","upper_wick","close_loc","sweep_excursion","approach_vel","failed_ext","early_downside"):
    ao=auc([lab(r) for r in gg],[feat(r,fn) for r in gg])
    ad=auc([lab(r) for r in gg if r["split"]=="DISC"],[feat(r,fn) for r in gg if r["split"]=="DISC"])
    ac=auc([lab(r) for r in gg if r["split"]=="CONF"],[feat(r,fn) for r in gg if r["split"]=="CONF"])
    print(f"  {fn:20} AUC overall={ao:.3f} DISC={ad:.3f} CONF={ac:.3f}")

# timeliness for CLEAN_80
tt=[r["t80"] for r in rows if r["cls"]=="A_clean" and r["t80"]]
if tt: print(f"\n=== TIMELINESS (CLEAN_80): time-to-80p bars median={np.median(tt):.0f} P25={np.percentile(tt,25):.0f} P75={np.percentile(tt,75):.0f} (x5min); remaining at E0 = 80p by construction ===")
