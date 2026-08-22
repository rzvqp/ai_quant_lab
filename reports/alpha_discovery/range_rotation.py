"""ALPHA-XAUUSD-RANGE-BOUNDARY-FAILED-BREAK-ROTATION-001. RANGE v4.4 (FROZEN, config 23d98c07) CONFIRMED
boundaries (from build_v44_alpha.py, consumed unchanged) -> boundary-attack clean-rotation on native M5.
FAMILY U (upper->SHORT) + FAMILY L (lower->LONG), SEPARATE. 4-class A/B/C/D. Primary endpoint = range MIDPOINT.
Position controls. DISC/CONF. NO MI retuning. NO execution. Price-only, DEV-only."""
import sys, os, json, numpy as np, pandas as pd
DSTp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DSTp not in sys.path: sys.path.insert(0,DSTp)
import m5_data as D
PIP=0.10; HOR=48   # frozen horizon: 48 M5 bars (4h), same-day, same-range-episode
V=json.load(open(os.path.join(DSTp,"v44_alpha.json")))
print(f"RANGE v4.4 boundaries: config={V['config_id'][:12]} contract={V['contract_version']} alpha_confirmed_bars={V['alpha_confirmed_bars']} collect={V['collect_from']}..{V['collect_to']}")
conf={int(r["ts"]):(r["upper"],r["lower"],r["mid"],r["macro_id"]) for r in V["confirmed"] if r["upper"] is not None and r["lower"] is not None}
# native M5 (Alpha gated)
tfs,_=D.build(); F=tfs["M5"]
o=F["open"].to_numpy();h=F["high"].to_numpy();l=F["low"].to_numpy();c=F["close"].to_numpy()
t=F["time"].to_numpy().astype("int64"); dt=pd.to_datetime(t,unit="s",utc=True)
uday=dt.floor("D").astype("int64").to_numpy(); yr=dt.year.to_numpy(); n=len(o)
dev=dt<=pd.Timestamp("2023-12-29 21:55",tz="UTC")
# causal boundary per M5 bar = last COMPLETED M15 confirmed bar = conf[(t//900)*900 - 900]
def bnd(i):
    O=(t[i]//900)*900; return conf.get(int(O-900))   # prev completed M15 bar's confirmed boundary
print(f"M5 DEV bars={int(dev.sum())} | M5 bars with active confirmed boundary={sum(1 for i in range(n) if dev[i] and bnd(i))}")

# --- parent attacks (first per macro_id per side, ownership S7) ---
def attacks(side):
    out=[]; seen=set()
    for i in range(n):
        if not dev[i]: continue
        b=bnd(i)
        if not b: continue
        up,lo,mid,mid_id=b
        key=(mid_id,side)
        if side=="U" and h[i]>up and key not in seen:
            seen.add(key); out.append(dict(i=i,up=up,lo=lo,mid=mid,mid_id=mid_id,side="U"))
        if side=="L" and l[i]<lo and key not in seen:
            seen.add(key); out.append(dict(i=i,up=up,lo=lo,mid=mid,mid_id=mid_id,side="L"))
    return out
AU=attacks("U"); AL=attacks("L")
print(f"\nPARENT ATTACKS: FAMILY U (upper/SHORT)={len(AU)} unique_ranges={len(set(a['mid_id'] for a in AU))} | FAMILY L (lower/LONG)={len(AL)} unique_ranges={len(set(a['mid_id'] for a in AL))}")

# --- 4-class: primary endpoint = range MIDPOINT; frozen sweep extreme=high[E0](U)/low[E0](L); horizon HOR same-day same-range ---
def classify(a):
    i=a["i"]; e1=i+1
    if e1>=n: return None
    day=uday[i]; mid=a["mid"]; mid_id=a["mid_id"]
    if a["side"]=="U":
        sweep_ext=h[i]; obj=mid; new_ext=False; reach=None
        for j in range(e1,min(e1+HOR,n)):
            if uday[j]!=day: break
            bj=bnd(j)
            if bj and bj[3]!=mid_id: break     # range episode changed
            if h[j]>sweep_ext: new_ext=True
            if reach is None and l[j]<=obj: reach=j; break
        newext_flag=new_ext
    else:
        sweep_ext=l[i]; obj=mid; new_ext=False; reach=None
        for j in range(e1,min(e1+HOR,n)):
            if uday[j]!=day: break
            bj=bnd(j)
            if bj and bj[3]!=mid_id: break
            if l[j]<sweep_ext: new_ext=True
            if reach is None and h[j]>=obj: reach=j; break
        newext_flag=new_ext
    if reach is not None:
        # new adverse extreme strictly before reaching objective?
        nb=False
        for j in range(e1,reach):
            if uday[j]!=day: break
            if (a["side"]=="U" and h[j]>sweep_ext) or (a["side"]=="L" and l[j]<sweep_ext): nb=True; break
        cls="A_clean" if not nb else "B_newext_then_rot"
    else:
        cls="C_breakout" if newext_flag else "D_stalled"
    # MFE/MAE toward objective + remaining
    ref=c[i]; mfe=0.0; mae=0.0
    for j in range(e1,min(e1+HOR,n)):
        if uday[j]!=day: break
        bj=bnd(j)
        if bj and bj[3]!=mid_id: break
        if a["side"]=="U": mfe=max(mfe,(ref-l[j])/PIP); mae=max(mae,(h[j]-ref)/PIP)
        else: mfe=max(mfe,(h[j]-ref)/PIP); mae=max(mae,(ref-l[j])/PIP)
    remaining=abs(ref-mid)/PIP
    return dict(cls=cls,mfe=mfe,mae=mae,sweep_ext=sweep_ext,ref=ref,remaining=remaining,
                width=(a["up"]-a["lo"])/PIP,excursion=(h[i]-a["up"])/PIP if a["side"]=="U" else (a["lo"]-l[i])/PIP)
from collections import Counter
def famstats(fam,name):
    rows=[{**a,**classify(a)} for a in fam if classify(a)]
    if not rows: print(f"\n{name}: no rows"); return rows
    N=len(rows); cc=Counter(r["cls"] for r in rows); f=lambda k:cc[k]/N
    print(f"\n=== {name}: N={N} unique_ranges={len(set(r['mid_id'] for r in rows))} ===")
    print(f"  P(A clean_rotation)={f('A_clean'):.3f} P(B new_ext_first)={f('B_newext_then_rot'):.3f} P(C breakout)={f('C_breakout'):.3f} P(D stalled)={f('D_stalled'):.3f}")
    print(f"  median range width={np.median([r['width'] for r in rows]):.0f}p | median remaining to mid={np.median([r['remaining'] for r in rows]):.1f}p | median MFE={np.median([r['mfe'] for r in rows]):.1f}p")
    mfes=np.array([r["mfe"] for r in rows]); print("  MFE: "+" ".join(f">={x}p:{np.mean(mfes>=x):.2f}" for x in (20,30,50,80,100)))
    for y in (2021,2022,2023):
        ry=[r for r in rows if yr[r["i"]]==y]
        if ry: print(f"    {y}: n={len(ry)} P(A)={np.mean([r['cls']=='A_clean' for r in ry]):.3f} P(B)={np.mean([r['cls']=='B_newext_then_rot' for r in ry]):.3f}")
    return rows
rowsU=famstats(AU,"FAMILY U / upper boundary -> SHORT rotation")
rowsL=famstats(AL,"FAMILY L / lower boundary -> LONG rotation")

# same-parent control: failed-acceptance (close back inside by E2) vs sustained-acceptance -> P(A)
def failed_accept(r):
    i=r["i"]
    for k in (i,i+1,i+2):
        if k<n and uday[k]==uday[i]:
            if (r["side"]=="U" and c[k]<r["up"]) or (r["side"]=="L" and c[k]>r["lo"]): return True
    return False
print("\n=== SAME-PARENT CONTROL: failed-acceptance vs sustained -> P(A clean) ===")
for rows,name in ((rowsU,"U/upper"),(rowsL,"L/lower")):
    if not rows: continue
    fa=[r for r in rows if failed_accept(r)]; su=[r for r in rows if not failed_accept(r)]
    pf=np.mean([r["cls"]=="A_clean" for r in fa]) if fa else np.nan; ps=np.mean([r["cls"]=="A_clean" for r in su]) if su else np.nan
    print(f"  {name:8}: failed-accept n{len(fa)} P(A)={pf:.3f} | sustained n{len(su)} P(A)={ps:.3f} | incr {pf-ps:+.3f}")
import pickle; pickle.dump(dict(rowsU=rowsU,rowsL=rowsL),open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"_rot_rows.pkl"),"wb"))
