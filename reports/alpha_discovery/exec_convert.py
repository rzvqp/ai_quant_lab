"""ALPHA-EARLY-TRAP-E1-EXECUTION-CONVERSION-001. EXECUTION research on the FROZEN EARLY-TRAP-E1 v1.0.0
signal (118 canonical episodes, consumed unchanged). NO signal retuning. Entry A(immediate)/B(retest),
Stop A(sweep extreme)/B(E1 high), targets Asia-mid/Asia-low/fixed-RR. EXEC_DISCOVERY/CONFIRMATION split.
Net of STRESS cost. Path decomposition + stop-out-before-target. DEV-only. NO CALIB."""
import sys, os, numpy as np, pandas as pd
DST=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
if DST not in sys.path: sys.path.insert(0,DST)
import early_trap_e1_signal as ES
PIP=0.10; COST=2.4   # STRESS RT 0.24 USD = 2.4 project pips (net)
FLOOR=2.0            # authoritative min stop floor (pips)
HORIZON=32           # same-day forward cap (M15 bars)

tfs,_=ES.D.build(); episodes,meta=ES.evaluate(tfs)
M=tfs["M15"]; o=M["open"].to_numpy();h=M["high"].to_numpy();l=M["low"].to_numpy();c=M["close"].to_numpy()
uday=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True).floor("D").astype("int64").to_numpy()
yr=pd.to_datetime(M["time"].to_numpy(),unit="s",utc=True).year.to_numpy(); n=len(o)
print(f"FROZEN signal: {meta['n_fires']} episodes / {meta['n_unique_days']} days (impl_fp {ES.implementation_fingerprint()[:12]})")

# EXEC split (NEW, chronological over the 118 episodes; independent of the old Alpha DISC/CONF)
eps=sorted(episodes,key=lambda e:e["signal_time"]); cut=eps[int(len(eps)*0.6)]["signal_time"]
for e in eps: e["exec_split"]="EXEC_DISC" if e["signal_time"]<cut else "EXEC_CONF"
print(f"EXEC split: DISC={sum(e['exec_split']=='EXEC_DISC' for e in eps)} CONF={sum(e['exec_split']=='EXEC_CONF' for e in eps)} (cut {pd.to_datetime(cut,unit='s',utc=True).date()})")

# ---- geometry per episode ----
def geom(e):
    sw=e["sweep_index"]; e1=e["e1_index"]; entry_i=e1+1
    if entry_i>=n: return None
    entry=o[entry_i]
    sweep_hi=h[sw:e1+1].max()                 # frozen sweep extreme (through E1)
    e1_hi=h[e1]                               # E1 structural high
    return dict(entry_i=entry_i,entry=entry,sweep_hi=sweep_hi,e1_hi=e1_hi,mid=e["asia_mid"],lo=e["asia_low"],
                day=e["day"],sess=e["session"],split=e["exec_split"],yr=int(yr[entry_i]))

# ---- path decomposition (S22): relative to sweep_hi (STOP-A level) and mid ----
def path_class(g):
    sw_hi=g["sweep_hi"]; mid=g["mid"]; ei=g["entry_i"]; newhi=False; reachmid=False; mid_after_newhi=False
    for j in range(ei,min(ei+HORIZON,n)):
        if uday[j]!=g["day"]: break
        if h[j]>sw_hi: newhi=True
        if l[j]<=mid:
            reachmid=True; mid_after_newhi=newhi; break
    if reachmid and not newhi: return "A_mid_no_newhi"
    if reachmid and mid_after_newhi: return "B_newhi_then_mid"
    if newhi and not reachmid: return "C_newhi_never_mid"
    return "D_nonewhi_never_mid"

# ---- trade sim: short entry, stop above `stop_lvl`, target: 'mid'|'low'|('rr',x) ----
def sim(g, stop_lvl, target):
    entry=g["entry"]; risk=(stop_lvl-entry)/PIP
    if risk<FLOOR: risk=FLOOR; stop_lvl=entry+risk*PIP
    if target=="mid": tgt=g["mid"]
    elif target=="low": tgt=g["lo"]
    else: tgt=entry-target[1]*risk*PIP        # fixed RR
    ei=g["entry_i"]; R=None; stopped_then_mid=False
    for j in range(ei,min(ei+HORIZON,n)):
        if uday[j]!=g["day"]: break
        hit_stop=h[j]>=stop_lvl; hit_tgt=l[j]<=tgt
        if hit_stop and hit_tgt: R=-1.0; break          # same-bar ambiguity -> STOP first (conservative)
        if hit_stop:
            R=-1.0
            for k in range(j,min(ei+HORIZON,n)):        # did mid come later? (right-signal/wrong-geometry)
                if uday[k]!=g["day"]: break
                if l[k]<=g["mid"]: stopped_then_mid=True; break
            break
        if hit_tgt:
            R=(entry-tgt)/PIP/risk; break
    if R is None: R=((entry-c[min(ei+HORIZON-1,n-1)])/PIP)/risk   # time-out mark-to-close
    R=R-COST/risk
    return R, risk, (tgt if target in("mid","low") else tgt), stopped_then_mid

def rstats(Rs):
    Rs=np.array(Rs)
    if len(Rs)==0: return None
    s=np.sort(Rs)[::-1]; br=lambda p:(s[int(len(s)*p):].mean() if int(len(s)*p)<len(s) else np.nan)
    top10=s[:max(1,int(len(s)*.1))].sum(); tot=Rs.sum()
    return dict(n=len(Rs),wr=round(float((Rs>0).mean()),3),avg=round(float(Rs.mean()),3),med=round(float(np.median(Rs)),3),
                b5=round(float(br(.05)),3),b10=round(float(br(.10)),3),top10=round(float(top10/tot),3) if tot>0 else None)

gs=[geom(e) for e in eps]; gs=[g for g in gs if g]
# path decomposition
from collections import Counter
pc=Counter(path_class(g) for g in gs)
print(f"\n=== PATH DECOMPOSITION (S22), n={len(gs)} ===")
for k in ("A_mid_no_newhi","B_newhi_then_mid","C_newhi_never_mid","D_nonewhi_never_mid"):
    print(f"  {k:22}: {pc[k]:3d} ({pc[k]/len(gs)*100:.1f}%)")
print(f"  => P(reach mid)={ (pc['A_mid_no_newhi']+pc['B_newhi_then_mid'])/len(gs):.3f}  P(new high)={ (pc['B_newhi_then_mid']+pc['C_newhi_never_mid'])/len(gs):.3f}")

# ---- policy grid: ENTRY-A x {STOP-A sweep, STOP-B e1hi} x {mid, low, RR1.0/1.5/2.0} ----
POLICIES=[]
for sname,slvl in (("SA_sweep",lambda g:g["sweep_hi"]),("SB_e1hi",lambda g:g["e1_hi"])):
    for tname,tgt in (("mid","mid"),("low","low"),("RR1.0",("rr",1.0)),("RR1.5",("rr",1.5)),("RR2.0",("rr",2.0))):
        POLICIES.append((f"EA-{sname}-{tname}",slvl,tgt))
print(f"\n=== EXECUTION POLICIES (ENTRY-A; net STRESS) — EXEC_DISC | EXEC_CONF ===")
print(f"{'policy':22} | DISC n/wr/avg/med/b10 | CONF n/wr/avg/med/b10 | %stop->mid")
survivors=[]
for pid,slvl,tgt in POLICIES:
    byD=[];byC=[];smD=0;smN=0
    for g in gs:
        R,risk,_,stm=sim(g,slvl(g),tgt)
        (byD if g["split"]=="EXEC_DISC" else byC).append(R)
        if R<0: smN+=1; smD+=int(stm)
    d=rstats(byD); cf=rstats(byC)
    smpct=round(smD/smN,2) if smN else None
    flag=""
    if d and cf and d["avg"]>0 and cf["avg"]>0 and cf["med"]>-0.5: flag="  <== survives"
    if d and cf:
        print(f"{pid:22} | D n{d['n']} {d['wr']}/{d['avg']:+.3f}/{d['med']:+.3f}/{d['b10']:+.3f} | C n{cf['n']} {cf['wr']}/{cf['avg']:+.3f}/{cf['med']:+.3f}/{cf['b10']:+.3f} | {smpct}{flag}")
    if flag: survivors.append(pid)
print(f"\nEXEC_DISC->CONF survivors (both avg>0): {survivors}")
