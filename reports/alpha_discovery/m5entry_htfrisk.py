"""ALPHA-XAUUSD-M5-ENTRY-ONLY-HTF-RISK-001 correction study.
Corrects the prior campaign: M5 is ENTRY/TIMING ONLY. STOP + TARGET are on the PARENT (H1) timeframe
(HTF STRUCTURAL SL = H1 swing; HTF economic TP = RR off the HTF risk). Control experiment:
  A = parent H1 setup + coarse next-H1-open entry + HTF SL + HTF TP
  B = SAME setup + SAME HTF SL + SAME HTF TP + M5-timed entry (only entry timing differs)
Answer: does M5 entry timing improve H1 strategies when SL/TP stay on the parent TF?
Gated M5 evidence only (via h1m5_campaign -> edge_research._common.load). NO M5 stop/target. NO N4. NO 2025+.
Cost tick 0.01, STRESS RT 0.24. <=30 IDs. Preserve prior TU-pb-L (M5-tight-stop) as historical."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import h1m5_campaign as C   # firewall-clean data layer + H1 edge generators (reused, unchanged)
PIP = C.PIP; RT = C.RT
h1 = C.h1; m5t = C.m5t; m5o = C.m5o; m5h = C.m5h; m5l = C.m5l; m5c = C.m5c; n5 = C.n5
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP,"htfrisk.log"),"a").write(f"{int(time.time())} {m}\n")

TRIG_WIN = 36        # M5 bars (3 H1) to find the entry trigger after the H1 signal
MAXHOLD_M5 = 576     # 48 H1 bars (2 trading days) max hold on the M5 walk
KSTRUCT = 6          # H1 bars back for the structural swing that defines HTF invalidation

def htf_stop_price(i, up):
    """HTF (H1) STRUCTURAL invalidation: swing low/high over the last KSTRUCT H1 bars +/- 0.10 ATR_H1."""
    a = h1["atr"][i]; a = a if a==a else 0.5
    lo = np.min(h1["low"][max(0,i-KSTRUCT):i+1]); hi = np.max(h1["high"][max(0,i-KSTRUCT):i+1])
    return (lo - 0.10*a) if up else (hi + 0.10*a)

def m5_entry_idx(T, direction, level, kind):
    """first M5 index (entry bar) after H1 signal time T where the trigger fires; None if no trigger in window."""
    j0 = int(np.searchsorted(m5t, T, side="right"))
    if j0<=1 or j0>=n5-2: return None
    end = min(j0+TRIG_WIN, n5-2)
    for j in range(j0, end):
        if kind=="breakout": trg = (m5h[j] > level) if direction>0 else (m5l[j] < level)
        elif kind=="accept": trg = (m5c[j] > level and m5c[j] > m5o[j]) if direction>0 else (m5c[j] < level and m5c[j] < m5o[j])
        elif kind=="retest": trg = (m5l[j] <= level <= m5h[j] and m5c[j] > level) if direction>0 else (m5l[j] <= level <= m5h[j] and m5c[j] < level)
        else: trg=False
        if trg and j+1 < n5-1: return j+1
    return None

def walk(entry_j, direction, stop_px, tgt_px):
    """walk M5 from entry_j to stop/target/maxhold (conservative stop-first). Returns (entry, exit, mae, mfe)."""
    if entry_j<=0 or entry_j>=n5-1: return None
    entry = m5o[entry_j]; end = min(entry_j+MAXHOLD_M5, n5); ex=None; mae=0.0; mfe=0.0
    for j in range(entry_j, end):
        mfe = max(mfe, (m5h[j]-entry) if direction>0 else (entry-m5l[j]))
        mae = max(mae, (entry-m5l[j]) if direction>0 else (m5h[j]-entry))
        if direction>0:
            if m5l[j] <= stop_px: ex=stop_px; break
            if m5h[j] >= tgt_px: ex=tgt_px; break
        else:
            if m5h[j] >= stop_px: ex=stop_px; break
            if m5l[j] <= tgt_px: ex=tgt_px; break
    if ex is None: ex = m5c[end-1]
    return entry, ex, mae, mfe

def run(edge_fn, up, trig_kind, rr, split="dev"):
    """returns dict with A (coarse) and B (M5) trade lists. SL/TP fixed on the parent TF (same prices for A and B)."""
    C._SPLIT = split
    sigs = edge_fn(up); d = 1 if up else -1
    A=[]; B=[]; a_win_missed_by_B=0
    lastA=-1; lastB=-1
    for (i, direction, level) in sigs:
        T = h1["close_time"][i]
        j_ref = int(np.searchsorted(m5t, T, side="right"))       # coarse entry bar (~next H1 open)
        if j_ref<=0 or j_ref>=n5-1: continue
        stop_px = htf_stop_price(i, up); entry_ref = m5o[j_ref]
        risk_ref = abs(entry_ref - stop_px)
        if not (risk_ref>0) or (up and stop_px>=entry_ref) or ((not up) and stop_px<=entry_ref): continue
        tgt_px = entry_ref + d*rr*risk_ref                        # HTF economic TP (RR off HTF risk), FIXED price
        # A: coarse entry
        wa = walk(j_ref, direction, stop_px, tgt_px)
        a_hit=None
        if wa is not None and m5t[j_ref] > lastA:
            entry,ex,mae,mfe = wa; lastA = m5t[min(j_ref+MAXHOLD_M5,n5-1)]
            Ra = (d*(ex-entry) - RT["STRESS"])/risk_ref
            a_hit = abs(ex-tgt_px)<1e-6
            A.append(dict(i=int(i), entry=entry, ex=ex, risk_ref=risk_ref, mae=mae, mfe=mfe, R=Ra, win=a_hit,
                          is_dev=bool(h1["is_dev"][i]), is_cal=bool(h1["is_cal"][i]), t=int(m5t[j_ref])))
        # B: M5-timed entry, SAME stop_px + SAME tgt_px, risk still in risk_ref units
        ej = m5_entry_idx(T, direction, level, trig_kind)
        if ej is not None and m5t[ej] > lastB:
            wb = walk(ej, direction, stop_px, tgt_px)
            if wb is not None:
                entry_b,exb,maeb,mfeb = wb; lastB = m5t[min(ej+MAXHOLD_M5,n5-1)]
                risk_b = abs(entry_b - stop_px)
                if risk_b>0 and not((up and stop_px>=entry_b) or ((not up) and stop_px<=entry_b)):
                    Rb = (d*(exb-entry_b) - RT["STRESS"])/risk_ref     # parent-risk units (comparable to A)
                    Rb_own = (d*(exb-entry_b) - RT["STRESS"])/risk_b   # B's own realized-RR units
                    B.append(dict(i=int(i), entry=entry_b, ex=exb, risk_ref=risk_ref, risk_own=risk_b, mae=maeb, mfe=mfeb,
                                  R=Rb, R_own=Rb_own, win=abs(exb-tgt_px)<1e-6, entry_edge=d*(entry_ref-entry_b),
                                  is_dev=bool(h1["is_dev"][i]), is_cal=bool(h1["is_cal"][i]), t=int(m5t[ej])))
        elif ej is None and a_hit:
            a_win_missed_by_B += 1
    return dict(A=A, B=B, missed_A_wins=a_win_missed_by_B)

def summ(trades, rr, dev=True, own=False):
    r=[x for x in trades if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return dict(n=0)
    R=np.array([(x["R_own"] if own and "R_own" in x else x["R"]) for x in r])
    wins=np.array([x["win"] for x in r]); n=len(R)
    sl=np.array([x["risk_ref"]/PIP for x in r]); tp=rr*sl
    mae=np.array([x["mae"]/PIP for x in r]); mfe=np.array([x["mfe"]/PIP for x in r])
    eq=np.cumsum(R); dd=float((np.maximum.accumulate(eq)-eq).max()) if n else 0
    l=R[R<=0]; w=R[R>0]
    ee=dict(n=n, WR=round(float(wins.mean()),3), avg_R=round(float(R.mean()),4), med_R=round(float(np.median(R)),3),
            pf=round(float(w.sum()/-l.sum()),3) if l.sum()<0 else None, maxDD=round(dd,2),
            med_SL_pips=round(float(np.median(sl)),1), med_TP_pips=round(float(np.median(tp)),1),
            pct_TP70=round(float((tp>=70).mean()),3), pct_TP80=round(float((tp>=80).mean()),3), pct_TP100=round(float((tp>=100).mean()),3),
            med_MAE_pips=round(float(np.median(mae)),1), med_MFE_pips=round(float(np.median(mfe)),1))
    return ee

# ---- curated candidate set (<=30 IDs): strongest + distinct mechanisms, HTF structural risk ----
E=C  # edge fns live on the campaign module
CANDS=[]
def add(cid, regime, fam, up, edge, trig, rr): CANDS.append(dict(id=cid, regime=regime, fam=fam, up=up, edge=edge, trig=trig, rr=rr))
for rr in (1.5,2.0,3.0,4.0):
    add(f"HR-TU-pb-L-rr{rr:g}","TREND_UP","trend_pullback",True,E.edge_trend_pullback,"breakout",rr)
for rr in (1.5,2.0,3.0):
    add(f"HR-TB-bo-L-rr{rr:g}","TREND_UP","trend_breakout",True,E.edge_trend_breakout,"accept",rr)
    add(f"HR-RG-rej-L-rr{rr:g}","RANGE","range_reject",True,E.edge_range_reject,"retest",rr)
for rr in (2.0,3.0):
    add(f"HR-RG-sweep-L-rr{rr:g}","RANGE","range_sweep",True,E.edge_range_sweep,"accept",rr)
    add(f"HR-TR-bo-L-rr{rr:g}","TRANSITION","transition_breakout",True,E.edge_transition_breakout,"accept",rr)
    add(f"HR-RI-disp-L-rr{rr:g}","REGIME_INDEPENDENT","ri_displacement",True,E.edge_regindep_disp,"breakout",rr)
    add(f"HR-TU-pb-S-rr{rr:g}","TREND_DOWN","trend_pullback",False,E.edge_trend_pullback,"breakout",rr)
    add(f"HR-TB-bo-S-rr{rr:g}","TREND_DOWN","trend_breakout",False,E.edge_trend_breakout,"accept",rr)

log(f"HTF-RISK CORRECTION START ids={len(CANDS)}")
records=[]
for h in CANDS:
    res = run(h["edge"], h["up"], h["trig"], h["rr"], "dev")
    A=summ(res["A"],h["rr"]); B=summ(res["B"],h["rr"]); Bown=summ(res["B"],h["rr"],own=True)
    dWR = (B.get("WR") or 0)-(A.get("WR") or 0); dAvg=(B.get("avg_R") or 0)-(A.get("avg_R") or 0)
    m5_helps = (dAvg>0) and (B.get("avg_R") or -9)>0
    rec=dict(id=h["id"], regime=h["regime"], family=h["fam"], direction="LONG" if h["up"] else "SHORT", rr=h["rr"],
             A_coarse=A, B_m5=B, B_m5_ownRR=dict(avg_R=Bown.get("avg_R"), WR=Bown.get("WR")),
             dWR_m5=round(dWR,3), dAvgR_m5=round(dAvg,4), missed_A_wins_byB=res["missed_A_wins"], M5_improves=bool(m5_helps))
    records.append(rec)
    log(f"{h['id']} [{h['regime']}] {rec['direction']} rr{h['rr']}: "
        f"A(n={A.get('n')},WR={A.get('WR')},avgR={A.get('avg_R')}) B(n={B.get('n')},WR={B.get('WR')},avgR={B.get('avg_R')}) "
        f"dWR={rec['dWR_m5']} dAvgR={rec['dAvgR_m5']} medSL={A.get('med_SL_pips')}p medTP={A.get('med_TP_pips')}p missedWins={res['missed_A_wins']} M5+={rec['M5_improves']}")
json.dump(records, open(os.path.join(SP,"htfrisk_records.json"),"w"), indent=1, default=float)
log(f"HTF-RISK CORRECTION COMPLETE ids={len(records)}")
