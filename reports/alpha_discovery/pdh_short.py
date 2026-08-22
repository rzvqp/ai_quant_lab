"""ALPHA-XAUUSD-PDH-LIQUIDITY-TRAP-CLEAN-SHORT-001. NEW independent family: Previous-Day-High sweep clean
SHORT. FAMILY L (London) + FAMILY N (New York), SEPARATE. Primary clean-path objective = >=80 project pips
bearish BEFORE any new high above frozen sweep_hi (4-class A/B/C/D). Native M5, DST-aware, DEV-only.
FROZEN PDH convention: trading day = UTC calendar day; PDH(D)=max M5 high of the immediately preceding day
with data; no current/future bars. NO execution. Price-only. No CALIB/V1/2025+/N4."""
import sys, os, numpy as np, pandas as pd
DSTp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DSTp not in sys.path: sys.path.insert(0,DSTp)
import m5_data as D
PIP=0.10; OBJ=80.0; HOR=96   # frozen: 80-pip clean objective, 96 M5 bars (8h) same-UTC-day horizon
tfs,_=D.build()
F=tfs["M5"]; o=F["open"].to_numpy();h=F["high"].to_numpy();l=F["low"].to_numpy();c=F["close"].to_numpy()
dt=pd.to_datetime(F["time"].to_numpy(),unit="s",utc=True); uh=dt.hour.to_numpy()
lon=dt.tz_convert("Europe/London").hour.to_numpy(); ny=dt.tz_convert("America/New_York").hour.to_numpy()
uday=dt.floor("D").astype("int64").to_numpy(); yr=dt.year.to_numpy(); n=len(o)
dev=dt<=pd.Timestamp("2023-12-29 21:55",tz="UTC")
print(f"native M5 DEV bars={int(dev.sum())} range {dt[dev].min().date()}..{dt[dev].max().date()}")

# --- FROZEN PDH: per UTC day, max high of the immediately preceding day with >=100 M5 bars ---
udays=np.unique(uday); daymax={}; daycnt={}
for d in udays:
    m=(uday==d); daycnt[d]=int(m.sum()); daymax[d]=float(h[m].max())
elig=[d for d in udays if daycnt[d]>=100]
pdh={}
for i,d in enumerate(udays):
    prev=[p for p in elig if p<d]
    if prev: pdh[d]=daymax[max(prev)]
print(f"PDH days defined={len(pdh)} (UTC-day convention, prev eligible day max high)")

# --- parent sweeps: first M5 high>PDH in window, DEV ---
def sweeps(win_fn, tag):
    out=[]
    for d in udays:
        if d not in pdh: continue
        P=pdh[d]; idx=np.where((uday==d)&win_fn()&np.isfinite(h))[0]
        # prior same-day attacks on frozen PDH before the window sweep (S21, correct: after PDH frozen at day start)
        for i in idx:
            if h[i]>P and dev[i]:
                pa=int(np.sum(h[(uday==d)&(np.arange(n)<i)]>P))
                out.append(dict(day=int(d),i=int(i),P=float(P),tag=tag,yr=int(yr[i]),
                                dow=int(pd.Timestamp(d,tz='UTC').dayofweek),prior_attacks=pa)); break
    return out
FAM_L=sweeps(lambda:(lon>=8)&(lon<10),"L")          # London 08:00-10:00 local
FAM_N=sweeps(lambda:(ny>=8)&(ny<11),"N")            # New York 08:00-11:00 local
print(f"\nPARENT PDH SWEEPS: FAMILY L (London)={len(FAM_L)} unique_days={len(set(s['day'] for s in FAM_L))} | FAMILY N (NY)={len(FAM_N)} unique_days={len(set(s['day'] for s in FAM_N))}")

# --- 4-class labels: reference=close[E0]; CLEAN=reach ref-80p BEFORE any high>sweep_hi; horizon HOR same-day ---
def classify(s):
    i=s["i"]; e1=i+1
    if e1>=n: return None
    sweep_hi=h[i]; ref=c[i]; obj=ref-OBJ*PIP; day=s["day"]
    newhi_before=False; reach_obj=None; newhi_any=False
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        if h[j]>sweep_hi: newhi_any=True
        if reach_obj is None and l[j]<=obj:
            reach_obj=j
            # was there a new high strictly before reaching obj?
            newhi_before=any(h[k]>sweep_hi for k in range(e1,j))
            break
    if reach_obj is not None:
        cls="A_clean" if not newhi_before else "B_newhi_then_obj"
    else:
        cls="C_continuation" if newhi_any else "D_stalled"
    # secondary MFE + remaining
    mfe=0.0; mae=0.0
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        mfe=max(mfe,(ref-l[j])/PIP); mae=max(mae,(h[j]-ref)/PIP)
    return dict(cls=cls,mfe=mfe,mae=mae,sweep_hi=sweep_hi,ref=ref,excursion=(sweep_hi-s["P"])/PIP,
                remaining80=OBJ)  # remaining to 80p from ref = 80p at E0 (full room by construction)

from collections import Counter
def famstats(fam,name):
    rows=[]
    for s in fam:
        lab=classify(s)
        if lab: rows.append({**s,**lab})
    if not rows: print(f"\n{name}: no rows"); return rows
    N=len(rows); cc=Counter(r["cls"] for r in rows); f=lambda k:cc[k]/N
    mfes=np.array([r["mfe"] for r in rows])
    print(f"\n=== {name}: N={N} unique_days={len(set(r['day'] for r in rows))} ===")
    print(f"  P(A clean 80p)={f('A_clean'):.3f} P(B newhi-first)={f('B_newhi_then_obj'):.3f} P(C continuation)={f('C_continuation'):.3f} P(D stalled)={f('D_stalled'):.3f}")
    print(f"  P(reach 80p ever, A+B)={f('A_clean')+f('B_newhi_then_obj'):.3f} | median sweep excursion above PDH={np.median([r['excursion'] for r in rows]):.1f}p")
    print("  downside MFE: "+" ".join(f">={t}p:{np.mean(mfes>=t):.2f}" for t in (30,50,80,100,150,200)))
    for y in (2021,2022,2023):
        ry=[r for r in rows if r["yr"]==y]
        if ry: print(f"    {y}: n={len(ry)} P(A)={np.mean([r['cls']=='A_clean' for r in ry]):.3f} P(B)={np.mean([r['cls']=='B_newhi_then_obj' for r in ry]):.3f} P(C)={np.mean([r['cls']=='C_continuation' for r in ry]):.3f}")
    return rows
rowsL=famstats(FAM_L,"FAMILY L / PDH (London)")
rowsN=famstats(FAM_N,"FAMILY N / PDH (New York)")

# --- same-parent control: failed-acceptance (close<PDH by E2) vs sustained -> P(A) ---
def failed_accept(s):
    for k in (s["i"],s["i"]+1,s["i"]+2):
        if k<n and uday[k]==s["day"] and c[k]<s["P"]: return True
    return False
print("\n=== SAME-PARENT CONTROL: failed-acceptance vs sustained -> P(A clean 80p) ===")
for rows,name in ((rowsL,"L/London"),(rowsN,"N/NewYork")):
    if not rows: continue
    fa=[r for r in rows if failed_accept(r)]; su=[r for r in rows if not failed_accept(r)]
    pf=np.mean([r["cls"]=="A_clean" for r in fa]) if fa else np.nan
    ps=np.mean([r["cls"]=="A_clean" for r in su]) if su else np.nan
    print(f"  {name:12}: failed-accept n{len(fa)} P(A)={pf:.3f} | sustained n{len(su)} P(A)={ps:.3f} | incr {pf-ps:+.3f}")

# --- day-of-week + first-vs-repeat diagnostics ---
print("\n=== DAY-OF-WEEK P(A clean) (diagnostic) ===")
for rows,name in ((rowsL,"L"),(rowsN,"N")):
    if not rows: continue
    s=" ".join(f"{['Mo','Tu','We','Th','Fr'][d]}:{np.mean([r['cls']=='A_clean' for r in rows if r['dow']==d]):.2f}(n{sum(r['dow']==d for r in rows)})" for d in range(5))
    print(f"  {name}: {s}")
print("=== FIRST vs REPEAT PDH attack P(A clean) (diagnostic) ===")
for rows,name in ((rowsL,"L"),(rowsN,"N")):
    if not rows: continue
    fst=[r for r in rows if r["prior_attacks"]==0]; rep=[r for r in rows if r["prior_attacks"]>=1]
    print(f"  {name}: first n{len(fst)} P(A)={np.mean([r['cls']=='A_clean' for r in fst]) if fst else float('nan'):.3f} | repeat n{len(rep)} P(A)={np.mean([r['cls']=='A_clean' for r in rep]) if rep else float('nan'):.3f}")
