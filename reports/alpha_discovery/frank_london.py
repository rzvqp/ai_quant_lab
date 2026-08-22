"""ALPHA-XAUUSD-FRANKFURT-LONDON-FALSE-DRIVE-SHORT-001 (+addendum 4-class labels).
Two SEPARATE families: F (Frankfurt/early-Europe Asia-High sweep, London-local 07-08 & Asia complete),
L (London-open sweep of Asia-High and Pre-London-High, London-local 08-10). DST-aware (Europe/London,
Europe/Berlin). Native M5 primary. Parent sweep = HIGH>L (strict). 4 future classes A/B/C/D (labels only).
Primary target P(A CLEAN) vs P(B NEW_HIGH_FIRST). Same-parent controls, DISC/CONF, remaining reward.
NO execution. Price-only, DEV-only. No CALIB/V1/2025+/N4."""
import sys, os, numpy as np, pandas as pd
DST=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DST not in sys.path: sys.path.insert(0,DST)
import m5_data as D
PIP=0.10; HOR=48  # frozen outcome horizon = 48 M5 bars (4h), same-day
tfs,_=D.build()
# --- Asia range from M15 (canonical 00-07 UTC), levels per day ---
M=tfs["M15"]; mh=M["high"].to_numpy();ml=M["low"].to_numpy()
mdt=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True); muh=mdt.hour.to_numpy()
mday=mdt.floor("D").astype("int64").to_numpy()
asia={}
for d in np.unique(mday):
    m=(mday==d)&(muh>=0)&(muh<7)&np.isfinite(M["atr"].to_numpy())
    if m.sum()<12: continue
    hi=mh[m].max();lo=ml[m].min();asia[d]=(hi,lo,(hi+lo)/2)
# --- native M5 arrays + DST-aware session hours ---
F=tfs["M5"]; o=F["open"].to_numpy();h=F["high"].to_numpy();l=F["low"].to_numpy();c=F["close"].to_numpy()
dt=pd.to_datetime(F["time"].to_numpy(),unit="s",utc=True); uh=dt.hour.to_numpy()
lon=dt.tz_convert("Europe/London").hour.to_numpy(); ber=dt.tz_convert("Europe/Berlin").hour.to_numpy()
uday=dt.floor("D").astype("int64").to_numpy(); yr=dt.year.to_numpy(); n=len(o)
devmask = dt<=pd.Timestamp("2023-12-29 21:55",tz="UTC")
print(f"native M5 DEV bars={int(devmask.sum())} range {dt[devmask].min()}..{dt[devmask].max()}")
print(f"session anchor: FAMILY F = London-local[7,8) & utc>=7 (Berlin[8,9)); FAMILY L = London-local[8,10)")

# --- Pre-London High: max M5 high over London-local [7,8) same day (causal, known by London open) ---
plh={}
for d in np.unique(uday):
    m=(uday==d)&(lon>=7)&(lon<8)&(uh>=7)
    if m.sum()>0: plh[d]=h[m].max()

# --- parent sweep detection: first M5 HIGH>L in window, utc>=7, DEV ---
def sweeps(level_fn, win_fn, tag):
    out=[]
    for d in np.unique(uday):
        if d not in asia: continue
        L=level_fn(d)
        if L is None or not np.isfinite(L): continue
        idx=np.where((uday==d)&win_fn(d)&(uh>=7)&np.isfinite(h))[0]
        for i in idx:
            if h[i]>L and devmask[i]:
                out.append(dict(day=int(d),i=int(i),L=float(L),tag=tag,
                                ah=asia[d][0],al=asia[d][1],amid=asia[d][2],yr=int(yr[i]),
                                lonh=int(lon[i]),berh=int(ber[i]))); break
    return out
FAM_F  = sweeps(lambda d:asia[d][0], lambda d:(lon>=7)&(lon<8), "F_AsiaHigh")
FAM_LAH= sweeps(lambda d:asia[d][0], lambda d:(lon>=8)&(lon<10),"L_AsiaHigh")
FAM_LPL= sweeps(lambda d:plh.get(d,np.nan), lambda d:(lon>=8)&(lon<10),"L_PreLondonHigh")
# event ownership: F and L windows disjoint (London 07-08 vs 08-10); L_AH vs L_PLH may share a day -> separate identities (S19)
print(f"\nPARENT SWEEPS: FAMILY F/AsiaHigh={len(FAM_F)} | FAMILY L/AsiaHigh={len(FAM_LAH)} | FAMILY L/PreLondonHigh={len(FAM_LPL)}")

# --- 4-class labels (addendum): frozen sweep_hi=high[E0]; objective=Asia mid; from E1 fwd same-day <=HOR ---
def classify(s):
    i=s["i"]; sweep_hi=h[i]; mid=s["amid"]; low=s["al"]; day=s["day"]
    e1=i+1
    if e1>=n: return None
    newhi=False; reach_mid=None; reach_low=None
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        if h[j]>sweep_hi: newhi=True
        if reach_mid is None and l[j]<=mid: reach_mid=j
        if reach_low is None and l[j]<=low: reach_low=j
        if reach_mid is not None and (newhi or j==min(e1+HOR,n)-1): pass
    # class assignment
    if reach_mid is not None:
        # did new high occur strictly before mid?
        nh_before=False
        for j in range(e1,reach_mid+1):
            if uday[j]!=day: break
            if h[j]>sweep_hi and j<reach_mid: nh_before=True; break
        cls="A_clean" if not nh_before else "B_newhi_then_mid"
    else:
        cls="C_continuation" if newhi else "D_stalled"
    remaining=(c[e1]-mid)/PIP if e1<n else np.nan
    mfe=0.0; mae=0.0
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        mfe=max(mfe,(c[e1]-l[j])/PIP); mae=max(mae,(h[j]-c[e1])/PIP)
    return dict(cls=cls, reach_mid=reach_mid is not None, reach_low=reach_low is not None,
                newhi=newhi, remaining=remaining, mfe=mfe, mae=mae, sweep_hi=sweep_hi)

def famstats(fam, name):
    rows=[]
    for s in fam:
        lab=classify(s)
        if lab: rows.append({**s,**lab})
    if not rows: print(f"\n{name}: no rows"); return rows
    days=len(set(r["day"] for r in rows)); N=len(rows)
    from collections import Counter
    cc=Counter(r["cls"] for r in rows)
    pA=cc["A_clean"]/N; pB=cc["B_newhi_then_mid"]/N; pC=cc["C_continuation"]/N; pD=cc["D_stalled"]/N
    pmid=np.mean([r["reach_mid"] for r in rows]); plow=np.mean([r["reach_low"] for r in rows]); pnh=np.mean([r["newhi"] for r in rows])
    print(f"\n=== {name}: N={N} unique_days={days} ===")
    print(f"  P(A clean)={pA:.3f} P(B newhi->mid)={pB:.3f} P(C continuation)={pC:.3f} P(D stalled)={pD:.3f}")
    print(f"  P(eventual mid)={pmid:.3f} P(Asia low)={plow:.3f} P(new-high-first-ish newhi)={pnh:.3f}")
    print(f"  median remaining to mid at E1={np.median([r['remaining'] for r in rows]):.1f}p | median MFE={np.median([r['mfe'] for r in rows]):.1f}p MAE={np.median([r['mae'] for r in rows]):.1f}p")
    mfes=np.array([r["mfe"] for r in rows])
    print("  downside MFE: "+" ".join(f">={t}p:{np.mean(mfes>=t):.2f}" for t in (20,30,50,80,100,150)))
    for y in (2021,2022,2023):
        ry=[r for r in rows if r["yr"]==y]
        if ry: print(f"    {y}: n={len(ry)} P(A)={np.mean([r['cls']=='A_clean' for r in ry]):.3f} P(B)={np.mean([r['cls']=='B_newhi_then_mid' for r in ry]):.3f} P(mid)={np.mean([r['reach_mid'] for r in ry]):.3f}")
    return rows
rowsF=famstats(FAM_F,"FAMILY F / Asia-High (Frankfurt/early-Europe)")
rowsLAH=famstats(FAM_LAH,"FAMILY L / Asia-High (London open)")
rowsLPL=famstats(FAM_LPL,"FAMILY L / Pre-London-High (London open)")

# --- same-parent control (S11/S20): failed-acceptance (close<L by E2) vs sustained-acceptance, P(A) ---
def failed_accept(s):
    i=s["i"]
    for k in (i,i+1,i+2):
        if k<n and uday[k]==s["day"] and c[k]<s["L"]: return True
    return False
print("\n=== SAME-PARENT CONTROL: failed-acceptance vs sustained-acceptance -> P(A clean) ===")
for rows,name in ((rowsF,"F/AsiaHigh"),(rowsLAH,"L/AsiaHigh"),(rowsLPL,"L/PreLondonHigh")):
    if not rows: continue
    fa=[r for r in rows if failed_accept(r)]; su=[r for r in rows if not failed_accept(r)]
    pAfa=np.mean([r["cls"]=="A_clean" for r in fa]) if fa else np.nan
    pAsu=np.mean([r["cls"]=="A_clean" for r in su]) if su else np.nan
    print(f"  {name:16}: failed-accept n{len(fa)} P(A)={pAfa:.3f} | sustained n{len(su)} P(A)={pAsu:.3f} | incr {pAfa-pAsu:+.3f}")
