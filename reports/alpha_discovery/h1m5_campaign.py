"""ALPHA-XAUUSD-H1-M5-MULTIREGIME-DISCOVERY-001 campaign.
H1 EDGE (setup identified at H1 close) -> M5 TRIGGER (causal entry within the next window) -> structural M5 SL
-> economic TP (RR). Multi-regime (TREND_UP/DOWN, RANGE, TRANSITION, REGIME_INDEPENDENT), both directions,
Profiles A (RR 1.5/2) and B (RR 3/4). Gated M5 only (m5_data.build). Cost tick 0.01, STRESS RT 0.24.
Also computes the H1-COARSE entry counterfactual for the M5-value delta. Checkpoint every 25 IDs."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict, Counter
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import m5_data as D
PIP = 0.10; TICK = D.TICK
RT = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.24}
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP,"h1m5.log"),"a").write(f"{int(time.time())} {m}\n")

tfs, META = D.build()
H1 = tfs["H1"]; M5 = tfs["M5"]
m5t = M5["time"].to_numpy(); m5o=M5["open"].to_numpy(); m5h=M5["high"].to_numpy(); m5l=M5["low"].to_numpy(); m5c=M5["close"].to_numpy()
m5atr = M5["atr"].to_numpy(); n5 = len(M5)
h1 = {k: H1[k].to_numpy() for k in ("time","close_time","open","high","low","close","atr","ema20","ema50","hh20","ll20","hh50","ll50","effic","regime","is_dev","is_cal")}
nH = len(H1)
TRIG_WIN = 36     # M5 bars (3 H1 hours) to find the trigger after the H1 signal
MAXHOLD = 288     # M5 bars (24h) max hold
SWING = 6         # M5 bars back for structural swing stop

def m5_after(T):
    j = int(np.searchsorted(m5t, T, side="right"));  return j

def simulate_m5(entry_j, direction, stop, tp):
    """walk M5 from entry_j (entry at m5o[entry_j]); conservative stop-first within bar; time-exit at MAXHOLD."""
    if entry_j <= 0 or entry_j >= n5-1: return None
    entry = m5o[entry_j]; risk = abs(entry-stop)
    if not (risk>0): return None
    end = min(entry_j+MAXHOLD, n5)
    ex=None
    for j in range(entry_j, end):
        if direction>0:
            if m5l[j] <= stop: ex=stop; break
            if m5h[j] >= tp: ex=tp; break
        else:
            if m5h[j] >= stop: ex=stop; break
            if m5l[j] <= tp: ex=tp; break
    if ex is None: ex = m5c[end-1]
    return entry, risk, ex

def trigger_entry(T, direction, level, kind):
    """find M5 trigger after H1 signal time T. kind in {breakout,retest,accept}. Returns (entry_j, stop_raw) or None.
    level = H1 signal reference (breakout level). structural stop from M5 swing near entry."""
    j0 = m5_after(T)
    if j0<=SWING or j0>=n5-2: return None
    end = min(j0+TRIG_WIN, n5-2)
    for j in range(j0, end):
        trg=False
        if kind=="breakout":
            trg = (m5h[j] > level) if direction>0 else (m5l[j] < level)
        elif kind=="accept":
            trg = (m5c[j] > level and m5c[j] > m5o[j]) if direction>0 else (m5c[j] < level and m5c[j] < m5o[j])
        elif kind=="retest":
            # price returns to level and closes back in trade direction
            trg = (m5l[j] <= level <= m5h[j] and m5c[j] > level) if direction>0 else (m5l[j] <= level <= m5h[j] and m5c[j] < level)
        if trg:
            ej = j+1
            if ej>=n5-1: return None
            lo = m5l[max(0,ej-SWING):ej+1]; hi = m5h[max(0,ej-SWING):ej+1]
            a = m5atr[j] if m5atr[j]==m5atr[j] else 0.5
            stop = (lo.min()-0.10*a) if direction>0 else (hi.max()+0.10*a)
            return ej, stop
    return None

# ---------- H1 EDGE generators: yield (i, direction, level) for DEV bars in the required regime ----------
_SPLIT = "dev"   # 'dev' (selection) or 'cal' (frozen-mechanism CALIB confirmation only)
def dev_idx(regime=None):
    mask = h1["is_cal"] if _SPLIT == "cal" else h1["is_dev"]
    idx = np.where(mask)[0]
    if regime: idx = idx[h1["regime"][idx]==regime]
    return idx
def edge_trend_pullback(up):
    reg="TREND_UP" if up else "TREND_DOWN"; d=1 if up else -1; out=[]
    for i in dev_idx(reg):
        if i<2: continue
        # pullback: prior bar pierced ema20 against trend, current bar resumes; level = prior H1 high/low
        if up and h1["low"][i-1] < h1["ema20"][i-1] and h1["close"][i] > h1["close"][i-1]: out.append((i,d,h1["high"][i]))
        elif (not up) and h1["high"][i-1] > h1["ema20"][i-1] and h1["close"][i] < h1["close"][i-1]: out.append((i,d,h1["low"][i]))
    return out
def edge_trend_breakout(up):
    reg="TREND_UP" if up else "TREND_DOWN"; d=1 if up else -1; out=[]
    for i in dev_idx(reg):
        lvl=h1["hh20"][i] if up else h1["ll20"][i]
        if not np.isfinite(lvl): continue
        if (h1["close"][i]>lvl) if up else (h1["close"][i]<lvl): out.append((i,d,h1["high"][i] if up else h1["low"][i]))
    return out
def edge_range_reject(up):
    # RANGE mean-reversion: price at lower boundary -> LONG (up=True); at upper boundary -> SHORT (up=False)
    d=1 if up else -1; out=[]
    for i in dev_idx("RANGE"):
        if up and np.isfinite(h1["ll50"][i]) and h1["low"][i] <= h1["ll50"][i]*1.001: out.append((i,d,h1["high"][i]))
        elif (not up) and np.isfinite(h1["hh50"][i]) and h1["high"][i] >= h1["hh50"][i]*0.999: out.append((i,d,h1["low"][i]))
    return out
def edge_range_failbreak(up):
    # failed range breakout -> reversion. up=True: failed downside break -> long
    d=1 if up else -1; out=[]
    for i in dev_idx("RANGE"):
        if i<1: continue
        if up and np.isfinite(h1["ll50"][i]) and h1["low"][i]<h1["ll50"][i] and h1["close"][i]>h1["ll50"][i]: out.append((i,d,h1["high"][i]))
        elif (not up) and np.isfinite(h1["hh50"][i]) and h1["high"][i]>h1["hh50"][i] and h1["close"][i]<h1["hh50"][i]: out.append((i,d,h1["low"][i]))
    return out
def edge_transition_breakout(up):
    d=1 if up else -1; out=[]
    for i in dev_idx("TRANSITION"):
        lvl=h1["hh50"][i] if up else h1["ll50"][i]
        if not np.isfinite(lvl): continue
        if (h1["close"][i]>lvl) if up else (h1["close"][i]<lvl): out.append((i,d,h1["high"][i] if up else h1["low"][i]))
    return out
def edge_regindep_disp(up):
    # displacement+acceptance regardless of regime: large body then continuation
    d=1 if up else -1; out=[]
    for i in dev_idx(None):
        a=h1["atr"][i]
        if a!=a: continue
        body=h1["close"][i]-h1["open"][i]
        if up and body>1.0*a: out.append((i,d,h1["high"][i]))
        elif (not up) and body<-1.0*a: out.append((i,d,h1["low"][i]))
    return out
def edge_regindep_momentum(up):
    d=1 if up else -1; out=[]
    for i in dev_idx(None):
        if i<3: continue
        if up and h1["close"][i]>h1["close"][i-1]>h1["close"][i-2]>h1["close"][i-3]: out.append((i,d,h1["high"][i]))
        elif (not up) and h1["close"][i]<h1["close"][i-1]<h1["close"][i-2]<h1["close"][i-3]: out.append((i,d,h1["low"][i]))
    return out
def edge_range_sweep(up):
    # sweep-reversal (Profile-A shot): RANGE, H1 wicks beyond ll50/hh50 but CLOSES back inside -> mean-revert.
    # level = the boundary that was swept; M5 'accept' trigger = M5 closes back through it in trade direction.
    d=1 if up else -1; out=[]
    for i in dev_idx("RANGE"):
        if up and np.isfinite(h1["ll50"][i]) and h1["low"][i] < h1["ll50"][i] and h1["close"][i] > h1["ll50"][i]:
            out.append((i,d,h1["ll50"][i]))
        elif (not up) and np.isfinite(h1["hh50"][i]) and h1["high"][i] > h1["hh50"][i] and h1["close"][i] < h1["hh50"][i]:
            out.append((i,d,h1["hh50"][i]))
    return out

def run_candidate(edge_fn, up, trig_kind, rr, entry_mode="m5"):
    """entry_mode 'm5' (M5 trigger) or 'coarse' (next H1 open, H1 structural stop). Returns per-trade list."""
    sigs = edge_fn(up); d = 1 if up else -1; rows=[]
    last_entry_t = -1
    for (i, direction, level) in sigs:
        T = h1["close_time"][i]
        if entry_mode=="m5":
            tr = trigger_entry(T, direction, level, trig_kind)
            if tr is None: continue
            ej, stop = tr
            if m5t[ej] <= last_entry_t: continue  # serialize (no overlap)
            entry = m5o[ej]; risk=abs(entry-stop)
            fl = max(0.10*(m5atr[ej-1] if m5atr[ej-1]==m5atr[ej-1] else 0.5), 5*TICK)
            if risk<fl: risk=fl; stop = entry - d*risk
            if risk<=0: continue
            tp = entry + d*rr*risk
            sim = simulate_m5(ej, direction, stop, tp)
            if sim is None: continue
            entry, risk, ex = sim
            last_entry_t = m5t[min(ej+MAXHOLD, n5-1)]
            rows.append(dict(t=int(m5t[ej]), entry=entry, risk=risk, ex=ex, dir=direction,
                             is_dev=bool(h1["is_dev"][i]), is_cal=bool(h1["is_cal"][i])))
        else:  # coarse H1 entry = first M5 after the signal H1 bar closes (== next H1 open), H1-structural stop
            ej = m5_after(h1["close_time"][i])
            if ej<=0 or ej>=n5-1: continue
            a=h1["atr"][i]; entry=m5o[ej]
            stop = (h1["low"][i]-0.10*a) if up else (h1["high"][i]+0.10*a)
            risk=abs(entry-stop)
            if not(risk>0): continue
            tp=entry+d*rr*risk
            sim = simulate_m5(ej, direction, stop, tp)
            if sim is None: continue
            entry,risk,ex=sim
            rows.append(dict(t=int(m5t[ej]), entry=entry, risk=risk, ex=ex, dir=direction,
                             is_dev=bool(h1["is_dev"][i]), is_cal=bool(h1["is_cal"][i])))
    return rows

def metrics(rows, rr, scen="STRESS", dev_only=True):
    r = [x for x in rows if (x["is_dev"] if dev_only else True)]
    if not r: return dict(n=0)
    R=[]; tp_pips=[]; sl_pips=[]
    for x in r:
        Rv = (x["dir"]*(x["ex"]-x["entry"]) - RT[scen])/x["risk"]
        R.append(Rv); sl_pips.append(x["risk"]/PIP); tp_pips.append(rr*x["risk"]/PIP)
    R=np.array(R); n=len(R); wins=R[R>0]
    Rs=np.sort(R)[::-1]; best1=float(Rs[max(1,int(n*0.01)):].mean()); best5=float(Rs[max(1,int(n*0.05)):].mean()); best10=float(Rs[max(1,int(n*0.10)):].mean())
    wr=float((R>=rr-0.05).mean())  # reached ~target
    return dict(n=n, avg_R=round(float(R.mean()),4), win_rate=round(wr,3), median_R=round(float(np.median(R)),4),
                pf=round(float(wins.sum()/-R[R<=0].sum()),3) if R[R<=0].sum()<0 else None,
                best1_rem=round(best1,4), best5_rem=round(best5,4), best10_rem=round(best10,4),
                med_TP_pips=round(float(np.median(tp_pips)),1), med_SL_pips=round(float(np.median(sl_pips)),1),
                pct_TP70=round(float((np.array(tp_pips)>=70).mean()),3), pct_TP80=round(float((np.array(tp_pips)>=80).mean()),3), pct_TP100=round(float((np.array(tp_pips)>=100).mean()),3))

def temporal(rows, rr):
    r=[x for x in rows if x["is_dev"]]
    if not r: return {}
    yr=defaultdict(list)
    for x in r:
        y=pd.to_datetime(x["t"],unit="s",utc=True).year
        yr[y].append((x["dir"]*(x["ex"]-x["entry"])-RT["STRESS"])/x["risk"])
    return {int(y): round(float(np.mean(v)),3) for y,v in sorted(yr.items())}

# ---------------- REGISTRY ----------------
REG=[]
def add(hid, regime, fam, up, edge, trig, profile, rr):
    REG.append(dict(id=hid, regime=regime, family=fam, up=up, edge=edge, trig=trig, profile=profile, rr=rr))
for up in (True,False):
    D_="L" if up else "S"
    for rr in (1.5,2.0,3.0,4.0):   # sanctioned RR neighborhood: A={1.5,2.0}, B={3.0,4.0}
        p="A" if rr<2.5 else "B"; rt=f"{rr:g}"
        add(f"TU-pb-{D_}-{p}{rt}","TREND_UP" if up else "TREND_DOWN","trend_pullback",up,edge_trend_pullback,"breakout",p,rr)
        add(f"TB-bo-{D_}-{p}{rt}","TREND_UP" if up else "TREND_DOWN","trend_breakout",up,edge_trend_breakout,"accept",p,rr)
        add(f"RG-rej-{D_}-{p}{rt}","RANGE","range_reject",up,edge_range_reject,"retest",p,rr)
        add(f"RG-sweep-{D_}-{p}{rt}","RANGE","range_sweep",up,edge_range_sweep,"accept",p,rr)
        add(f"RG-fb-{D_}-{p}{rt}","RANGE","range_failbreak",up,edge_range_failbreak,"accept",p,rr)
        add(f"TR-bo-{D_}-{p}{rt}","TRANSITION","transition_breakout",up,edge_transition_breakout,"accept",p,rr)
        add(f"RI-disp-{D_}-{p}{rt}","REGIME_INDEPENDENT","ri_displacement",up,edge_regindep_disp,"breakout",p,rr)
        add(f"RI-mom-{D_}-{p}{rt}","REGIME_INDEPENDENT","ri_momentum",up,edge_regindep_momentum,"accept",p,rr)

def falsify(m):
    if m.get("n",0)<30: return "EVENT_SPARSE"
    if m.get("n",0)<50: return "INSUFFICIENT"
    if (m.get("avg_R") or -9)<=0: return "FAIL"
    if (m.get("best5_rem") or -9)<=0: return "TAIL_FRAGILE"
    return "SURVIVE"

records=[]
log(f"H1M5 CAMPAIGN START registry={len(REG)} (DEV H1 bars={int(h1['is_dev'].sum())})")
for k,h in enumerate(REG):
    try:
        rows = run_candidate(h["edge"], h["up"], h["trig"], h["rr"], "m5")
        m = metrics(rows, h["rr"], "STRESS"); mb = metrics(rows, h["rr"], "BASE")
        st = falsify(m)
        rec = dict(id=h["id"], regime=h["regime"], family=h["family"], direction="LONG" if h["up"] else "SHORT",
                   profile=h["profile"], intended_RR=f"1:{h['rr']}", trig=h["trig"], status=st,
                   STRESS=m, BASE_avg=mb.get("avg_R"), temporal=temporal(rows,h["rr"]) if st=="SURVIVE" else None)
        records.append(rec)
        log(f"{h['id']} [{h['regime']}] {rec['direction']} P{h['profile']} rr{h['rr']}: n={m.get('n')} WR={m.get('win_rate')} avgR={m.get('avg_R')} b5rem={m.get('best5_rem')} medTP={m.get('med_TP_pips')}p medSL={m.get('med_SL_pips')}p -> {st}")
    except Exception as e:
        records.append(dict(id=h["id"], status="ERROR", err=str(e)[:150])); log(f"{h['id']} ERR {str(e)[:150]}")
    if (k+1)%25==0:
        json.dump(records, open(os.path.join(SP,f"h1m5_ck_{k+1}.json"),"w"), indent=1, default=float)
        surv=[r['id'] for r in records if r.get('status')=='SURVIVE']; log(f"CHECKPOINT {k+1}: surv={surv}")
surv=[r for r in records if r.get('status')=='SURVIVE']
json.dump(dict(records=records, survivors=[r['id'] for r in surv]), open(os.path.join(SP,"h1m5_records.json"),"w"), indent=1, default=float)
log(f"H1M5_COMPLETE tested={len(records)} survivors={[r['id'] for r in surv]}")
