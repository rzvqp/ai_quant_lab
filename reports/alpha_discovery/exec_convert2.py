"""Phase 2: ENTRY-B (Asia-High retest) + larger-target diagnostics + partial/runner + tails/session/year.
Same FROZEN EARLY-TRAP-E1 signal. Decide mean-reversion vs continuation vs not-executable."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import exec_convert as X   # reuse frozen episodes, arrays, geom, sim, rstats
gs=X.gs; o=X.o;h=X.h;l=X.l;c=X.c;uday=X.uday;n=X.n; PIP=X.PIP; COST=X.COST; FLOOR=X.FLOOR; HORIZON=X.HORIZON
rstats=X.rstats

# ---- ENTRY-B: Asia-High retest (frozen semantics) ----
# After E1: over next K bars, if high>=asia_high (retest liquidity) BEFORE low<=mid and BEFORE high>=sweep_hi,
# FILL short at asia_high (limit) on that bar. Stop=sweep_hi+floor. Then resolve target mid/low.
RETEST_K=8
def entryB(g, target, asia_high):
    ei=g["entry_i"]; sw_hi=g["sweep_hi"]; mid=g["mid"]; fill_i=None
    for j in range(ei,min(ei+RETEST_K,n)):
        if uday[j]!=g["day"]: break
        if h[j]>=sw_hi: return ("no_fill_invalid",None)     # invalidated before retest
        if l[j]<=mid: return ("no_fill_missed",None)        # reached mid before retest (missed winner)
        if h[j]>=asia_high: fill_i=j; break                 # retest fill
    if fill_i is None: return ("no_fill_timeout",None)
    entry=asia_high; stop=sw_hi+FLOOR*PIP; risk=(stop-entry)/PIP
    if risk<FLOOR: risk=FLOOR; stop=entry+risk*PIP
    tgt=mid if target=="mid" else (g["lo"] if target=="low" else entry-target[1]*risk*PIP)
    R=None
    for j in range(fill_i,min(ei+HORIZON,n)):
        if uday[j]!=g["day"]: break
        hs=h[j]>=stop; ht=l[j]<=tgt
        if hs and ht: R=-1.0; break
        if hs: R=-1.0; break
        if ht: R=(entry-tgt)/PIP/risk; break
    if R is None: R=((entry-c[min(ei+HORIZON-1,n-1)])/PIP)/risk
    return ("fill", R-COST/risk)

# need asia_high per episode -> recover from geom source (episodes carry it)
eps={ (e["day"]):e for e in X.eps}
def ah(g): return eps[g["day"]]["asia_high"]

print("=== ENTRY-B (Asia-High retest, K=8) vs ENTRY-A — same frozen signal ===")
for tname,tgt in (("mid","mid"),("low","low")):
    fills=[];Rs=[];fillsplit={"EXEC_DISC":[],"EXEC_CONF":[]};outcome={}
    for g in gs:
        st,R=entryB(g,tgt,ah(g))
        outcome[st]=outcome.get(st,0)+1
        if st=="fill": Rs.append(R); fillsplit[g["split"]].append(R)
    fr=len([1 for g in gs if True]); nfill=len(Rs)
    st=rstats(Rs); d=rstats(fillsplit["EXEC_DISC"]); cf=rstats(fillsplit["EXEC_CONF"])
    print(f"  target={tname}: fill_rate={nfill}/{len(gs)}={nfill/len(gs):.2f} outcomes={outcome}")
    if st: print(f"     ALL fills: n{st['n']} wr{st['wr']} avg{st['avg']:+.3f} med{st['med']:+.3f} b10{st['b10']:+.3f} top10%{st['top10']}")
    if d and cf: print(f"     DISC n{d['n']} avg{d['avg']:+.3f} med{d['med']:+.3f} | CONF n{cf['n']} avg{cf['avg']:+.3f} med{cf['med']:+.3f}")

# ---- larger-target diagnostics (S16): MFE down from ENTRY-A entry ----
print("\n=== LARGER DOWNSIDE DIAGNOSTIC (S16): MFE below ENTRY-A entry, same-day ===")
mfes=[]
for g in gs:
    ei=g["entry_i"]; mfe=0
    for j in range(ei,min(ei+HORIZON,n)):
        if uday[j]!=g["day"]: break
        mfe=max(mfe,(g["entry"]-l[j])/PIP)
    mfes.append(mfe)
mfes=np.array(mfes)
for t in (20,30,50,80,100,150,200):
    print(f"  P(MFE>={t}p)={np.mean(mfes>=t):.3f}", end="")
print(f"\n  median MFE={np.median(mfes):.1f}p  P75={np.percentile(mfes,75):.1f}p  P90={np.percentile(mfes,90):.1f}p")

# ---- partial+runner (S19): 50% at mid, 50% at Asia low, stop=sweep_hi (one predeclared split) ----
print("\n=== PARTIAL+RUNNER (50% mid / 50% Asia-low, stop=sweep_hi) — same frozen signal ===")
def pr(g):
    entry=g["entry"]; stop=g["sweep_hi"]+FLOOR*PIP; risk=(stop-entry)/PIP
    if risk<FLOOR: risk=FLOOR; stop=entry+risk*PIP
    ei=g["entry_i"]; got_mid=False; R=0.0; closed=False
    for j in range(ei,min(ei+HORIZON,n)):
        if uday[j]!=g["day"]: break
        if h[j]>=stop:
            R+= -0.5 if got_mid else -1.0                    # runner (or full) stopped
            closed=True; break
        if not got_mid and l[j]<=g["mid"]:
            R+= 0.5*((entry-g["mid"])/PIP/risk); got_mid=True # bank half at mid; runner continues, stop to BE-ish (keep sweep_hi conservative)
        if got_mid and l[j]<=g["lo"]:
            R+= 0.5*((entry-g["lo"])/PIP/risk); closed=True; break
    if not closed: R+=(0.5 if got_mid else 1.0)*((entry-c[min(ei+HORIZON-1,n-1)])/PIP)/risk
    return R-COST/risk
Rs=[pr(g) for g in gs]; d=rstats([pr(g) for g in gs if g["split"]=="EXEC_DISC"]); cf=rstats([pr(g) for g in gs if g["split"]=="EXEC_CONF"])
st=rstats(Rs)
print(f"  ALL: n{st['n']} wr{st['wr']} avg{st['avg']:+.3f} med{st['med']:+.3f} b10{st['b10']:+.3f} top10%{st['top10']}")
print(f"  DISC avg{d['avg']:+.3f} med{d['med']:+.3f} | CONF avg{cf['avg']:+.3f} med{cf['med']:+.3f}")

# ---- session + year attribution for the least-bad simple policy (EA-SA_sweep-low) ----
print("\n=== SESSION + YEAR ATTRIBUTION (EA-SA_sweep-low, diagnostic) ===")
def polR(g):
    R,_,_,_=X.sim(g,g["sweep_hi"],"low"); return R
for key,grp in (("LONDON",lambda g:g["sess"]=="LONDON"),("OVERLAP",lambda g:g["sess"]=="OVERLAP")):
    r=rstats([polR(g) for g in gs if grp(g)]);
    if r: print(f"  {key:8}: n{r['n']} avg{r['avg']:+.3f} med{r['med']:+.3f} b10{r['b10']:+.3f}")
for y in (2021,2022,2023):
    r=rstats([polR(g) for g in gs if g["yr"]==y])
    if r: print(f"  {y}: n{r['n']} avg{r['avg']:+.3f} med{r['med']:+.3f}")
