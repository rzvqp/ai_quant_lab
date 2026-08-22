"""ALPHA-XAUUSD-LONDON-PLH-CAUSAL-FEATURE-MAP-001. Strictly-causal event-level feature MAP for the London /
Pre-London-High sweep family (parent recovered UNCHANGED from frank_london.py / commit 50b099d, N~133).
Univariate only (NO classifier per S28). Discriminate A(clean) vs B+C, DISC/CONF, year, POSITION CONTROLS,
timeliness. Price-only, DEV-only. NO thresholds/volume/execution."""
import sys, os, numpy as np, pandas as pd
DSTp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DSTp not in sys.path: sys.path.insert(0,DSTp)
import frank_london as FL
h=FL.h;l=FL.l;c=FL.c;o=FL.o;uday=FL.uday;lon=FL.lon;n=FL.n;PIP=FL.PIP;yr=FL.yr
rows=FL.rowsLPL   # 133 canonical parents with 4-class labels (Asia-mid objective), UNCHANGED
# causal ATR from M5 (rolling14 TR, value at bar before event)
tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
atr=pd.Series(tr).rolling(14).mean().to_numpy()
# pre-London low per day (London 07-08) for PLH range
pll={}
for d in np.unique(uday):
    m=(uday==d)&(lon>=7)&(lon<8)&(FL.uh>=7)
    if m.sum()>0: pll[d]=l[m].min()
print(f"PARENT (recovered UNCHANGED from 50b099d): N={len(rows)} unique_days={len(set(r['day'] for r in rows))}")
from collections import Counter
cc=Counter(r["cls"] for r in rows); N=len(rows)
print(f"4-class balance: A{cc['A_clean']/N:.3f} B{cc['B_newhi_then_mid']/N:.3f} C{cc['C_continuation']/N:.3f} D{cc['D_stalled']/N:.3f}")

# DISC/CONF chronological split (frozen before ranking)
rows=sorted(rows,key=lambda r:r["i"]); cut=rows[int(len(rows)*0.6)]["i"]
for r in rows: r["split"]="DISC" if r["i"]<cut else "CONF"
print(f"split: DISC {sum(r['split']=='DISC' for r in rows)} | CONF {sum(r['split']=='CONF' for r in rows)} (cut {pd.to_datetime(FL.uday[cut] if False else cut,unit='s',utc=True) if False else '~2023'})")

def rng(i): return max(h[i]-l[i],1e-9)
def build_feats(r):
    i=r["i"]; P=r["L"]; sh=r["sweep_hi"]; A=atr[i-1] if i>=1 and np.isfinite(atr[i-1]) else np.nan
    d=r["day"]; ah=r["ah"]; amid=r["amid"]; al=r["al"]; e1=i+1
    F={}
    # --- E0 spatial context (S9,S17) ---
    F["plh_minus_asiahigh"]=(P-ah)/PIP                       # PLH-AsiaHigh separation (KEY S17)
    F["sweep_excursion"]=(sh-P)/PIP
    F["prelondon_range"]=((P-pll[d])/PIP) if d in pll else np.nan
    F["dist_close_plh_E0"]=(c[i]-P)/PIP
    F["dist_asia_mid"]=(c[i]-amid)/PIP
    # --- E0 anatomy (S11) ---
    F["upper_wick_ratio"]=(h[i]-max(o[i],c[i]))/rng(i)
    F["body_ratio"]=abs(c[i]-o[i])/rng(i)
    F["close_loc"]=(c[i]-l[i])/rng(i)
    F["bear_body_E0"]=(o[i]-c[i])/PIP
    recent=[rng(j) for j in range(max(0,i-6),i)]
    F["range_expansion_E0"]=rng(i)/(np.mean(recent) if recent else rng(i))
    # --- approach velocity (pre-sweep, causal S12) ---
    for m,b in (("5m",1),("10m",2),("15m",3),("30m",6)):
        F[f"disp_{m}"]=(c[i]-c[i-b])/PIP if i>=b else np.nan
    path=sum(abs(c[j]-c[j-1]) for j in range(max(1,i-6),i+1)); net=abs(c[i]-c[max(0,i-6)])
    F["approach_eff"]=net/path if path>0 else np.nan
    # --- normalized versions (raw + ATR-normalized, S10) ---
    F["sweep_excursion_atr"]=F["sweep_excursion"]*PIP/A if A==A and A>0 else np.nan
    F["plh_minus_asiahigh_atr"]=F["plh_minus_asiahigh"]*PIP/A if A==A and A>0 else np.nan
    # --- E1/E2/E3 path (causal, only bars completed by landmark; S13-S16,S19) ---
    for k in (1,2,3):
        seg=list(range(e1,e1+k))
        if seg and seg[-1]<n and all(uday[j]==d for j in seg):
            hi=max(h[j] for j in seg); lo=min(l[j] for j in seg); cl=c[seg[-1]]
            F[f"net_downside_E{k}"]=(c[i]-cl)/PIP
            F[f"max_downside_E{k}"]=(c[i]-lo)/PIP
            F[f"extend_beyond_sweep_E{k}"]=(hi-sh)/PIP
            F[f"failed_ext_E{k}"]=float(hi<sh)
            F[f"dist_below_sweep_E{k}"]=(sh-hi)/PIP
            F[f"closes_above_plh_E{k}"]=float(sum(c[j]>P for j in seg))   # time-above (completed bars only, S14)
            F[f"bear_close_cnt_E{k}"]=float(sum(c[j]<c[j-1] for j in seg))
            F[f"last_bear_E{k}"]=(o[seg[-1]]-c[seg[-1]])/PIP
            up=(hi-c[i]); dn=(c[i]-lo); F[f"dn_up_ratio_E{k}"]=dn/(up+PIP)
            F[f"resolved_E{k}"]=("newhi" if hi>sh else ("mid" if lo<=amid else "undecided"))
            F[f"remaining_E{k}"]=(cl-amid)/PIP
    return F
for r in rows: r["F"]=build_feats(r)

def auc(y,x):
    y=np.array(y);x=np.array(x,float);m=np.isfinite(x);y=y[m];x=x[m];n1=y.sum();n0=len(y)-n1
    if n1==0 or n0==0: return np.nan
    rk=np.argsort(np.argsort(x))+1; return (rk[y==1].sum()-n1*(n1+1)/2)/(n1*n0)
def lab(r): return 1 if r["cls"]=="A_clean" else (0 if r["cls"] in ("B_newhi_then_mid","C_continuation") else -1)

E0F=["plh_minus_asiahigh","plh_minus_asiahigh_atr","sweep_excursion","sweep_excursion_atr","prelondon_range",
     "dist_asia_mid","upper_wick_ratio","body_ratio","close_loc","bear_body_E0","range_expansion_E0",
     "disp_5m","disp_10m","disp_15m","disp_30m","approach_eff"]
print("\n=== E0 STATIC FEATURE MAP: A(clean) vs B+C, univariate AUC (DISC | CONF) + years ===")
print(f"{'feature':24} {'DISC':>6} {'CONF':>6} {'stable':>7}  yr21/22/23 P(A)-corr-dir")
for f in E0F:
    D=[r for r in rows if r["split"]=="DISC" and lab(r)>=0]; C=[r for r in rows if r["split"]=="CONF" and lab(r)>=0]
    ad=auc([lab(r) for r in D],[r["F"].get(f,np.nan) for r in D]); ac=auc([lab(r) for r in C],[r["F"].get(f,np.nan) for r in C])
    stable=(np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.07 and abs(ac-.5)>.07)
    ys=[]
    for y in (2021,2022,2023):
        gy=[r for r in rows if r["yr"]==y and lab(r)>=0]; ys.append(auc([lab(r) for r in gy],[r["F"].get(f,np.nan) for r in gy]))
    print(f"  {f:24} {ad:6.2f} {ac:6.2f} {'YES' if stable else '.':>7}  {ys[0]:.2f}/{ys[1]:.2f}/{ys[2]:.2f}")

print("\n=== LANDMARK PATH FEATURES E1/E2/E3: A vs B+C AUC (DISC|CONF), undecided-N, remaining, POSITION-adjusted ===")
PATHF=["net_downside","max_downside","extend_beyond_sweep","dist_below_sweep","closes_above_plh","last_bear","dn_up_ratio"]
for k in (1,2,3):
    und=[r for r in rows if r["F"].get(f"resolved_E{k}")=="undecided" and lab(r)>=0]
    d=[r for r in und if r["split"]=="DISC"]; cf=[r for r in und if r["split"]=="CONF"]
    rem=np.median([r["F"][f"remaining_E{k}"] for r in und]) if und else np.nan
    print(f"  --- E{k}: undecided n={len(und)} (DISC {len(d)}/CONF {len(cf)}) medRemain={rem:.1f}p ---")
    for f in PATHF:
        key=f"{f}_E{k}"
        ad=auc([lab(r) for r in d],[r["F"].get(key,np.nan) for r in d]); ac=auc([lab(r) for r in cf],[r["F"].get(key,np.nan) for r in cf])
        # position control: AUC within tertiles of dist_below_sweep (position proxy)
        pos=np.array([r["F"].get(f"dist_below_sweep_E{k}",np.nan) for r in und]); ql=np.nanquantile(pos,[.33,.66])
        padj=[]
        for lo,hi in ((-1e9,ql[0]),(ql[0],ql[1]),(ql[1],1e9)):
            sub=[r for r in und if lo<=r["F"].get(f"dist_below_sweep_E{k}",np.nan)<hi]
            if len(sub)>=8: padj.append(auc([lab(r) for r in sub],[r["F"].get(key,np.nan) for r in sub]))
        pa=np.nanmedian(padj) if padj else np.nan
        st="stable" if (np.isfinite(ad) and np.isfinite(ac) and (ad-.5)*(ac-.5)>0 and abs(ad-.5)>.07 and abs(ac-.5)>.07) else ""
        print(f"     {f:20} DISC{ad:.2f} CONF{ac:.2f} posadj(medTertileAUC){pa:.2f} {st}")

# KEY HYPOTHESIS distributions (S17 PLH-AsiaHigh, S18 wick) class-conditional
print("\n=== CLASS-CONDITIONAL (median) for key hypotheses ===")
for f in ("plh_minus_asiahigh","sweep_excursion","upper_wick_ratio","close_loc","approach_eff"):
    line=f"  {f:22}"
    for cl in ("A_clean","B_newhi_then_mid","C_continuation"):
        v=[r["F"].get(f,np.nan) for r in rows if r["cls"]==cl]; line+=f" {cl[:4]}={np.nanmedian(v):+.2f}"
    print(line)
