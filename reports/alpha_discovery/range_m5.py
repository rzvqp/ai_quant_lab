"""ALPHA-XAUUSD-H1-RANGE-M5-DISCOVERY-001.
H1 owns the RANGE thesis (boundaries/SL/TP/invalidation); M5 = ENTRY TIMING ONLY (NO M5 stop/target).
LONG near H1 range LOW, SHORT near H1 range HIGH, via causal M5 confirmation. Control A(coarse H1 entry)
vs B(same H1 SL+TP+M5 confirmation entry). Gated M5 evidence only (via m5_data -> edge_research._common.load).
NO N4, NO 2025+, NO raw read_csv. Cost tick 0.01, STRESS RT 0.24. <=50 IDs, checkpoint 25."""
import sys, os, json, time
import numpy as np, pandas as pd
from collections import defaultdict
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import m5_data as D
PIP = 0.10
RT = {"GROSS": 0.0, "BASE": 0.05, "STRESS": 0.24}
def log(m): print(f"[{int(time.time())}] {m}", flush=True); open(os.path.join(SP,"range.log"),"a").write(f"{int(time.time())} {m}\n")

tfs, META = D.build()
H1 = tfs["H1"]; M5 = tfs["M5"]
m5t=M5["time"].to_numpy(); m5o=M5["open"].to_numpy(); m5h=M5["high"].to_numpy(); m5l=M5["low"].to_numpy(); m5c=M5["close"].to_numpy(); n5=len(M5)
h1o=H1["open"].to_numpy(); h1h=H1["high"].to_numpy(); h1l=H1["low"].to_numpy(); h1c=H1["close"].to_numpy()
h1atr=H1["atr"].to_numpy(); h1ct=H1["close_time"].to_numpy(); h1dev=H1["is_dev"].to_numpy(); h1cal=H1["is_cal"].to_numpy()
nH=len(H1)

# ---------- causal H1 RANGE detection ----------
W = 24  # lookback (1 day of H1)
rhi = pd.Series(h1h).rolling(W).max().shift(1).to_numpy()
rlo = pd.Series(h1l).rolling(W).min().shift(1).to_numpy()
width = rhi - rlo
# efficiency over W (causal): net/path
net = h1c - pd.Series(h1c).shift(W).to_numpy()
path = pd.Series(np.abs(np.diff(h1c, prepend=h1c[0]))).rolling(W).sum().shift(1).to_numpy()
eff = np.where(path>0, net/path, np.nan)
# boundary-touch counts within window (alternation/quality): touches near hi and lo
def touches():
    thi=np.zeros(nH); tlo=np.zeros(nH)
    for i in range(W+1,nH):
        seg_h=h1h[i-W:i]; seg_l=h1l[i-W:i]; hi=rhi[i]; lo=rlo[i]; w=width[i]
        if not (w>0): continue
        thi[i]=int(np.sum(seg_h >= hi-0.10*w)); tlo[i]=int(np.sum(seg_l <= lo+0.10*w))
    return thi,tlo
touch_hi,touch_lo = touches()
MINW = 40*PIP; MAXW = 600*PIP
in_range = (np.abs(eff) < 0.35) & (width>=MINW) & (width<=MAXW) & (touch_hi>=2) & (touch_lo>=2)
rmid = (rhi+rlo)/2
log(f"H1 RANGE bars: DEV={int((in_range & h1dev).sum())} CALIB={int((in_range & h1cal).sum())} of DEV H1={int(h1dev.sum())}")

def m5_after(T): return int(np.searchsorted(m5t, T, side="right"))
TRIG_WIN=48; MAXHOLD=576

# ---------- M5 confirmation (reversal-appropriate) ----------
def m5_confirm(T, side, level, kind):
    """side +1 long / -1 short. level = boundary. FAIR confirmations that enter INTO the range interior
    (do NOT require re-breaching the boundary -> avoids confounding with the coarse stop).
    kind: mom (first momentum bar toward interior), mbos (micro-BOS toward interior over M5 swing),
    reclaim (sweep beyond then close back -- only for the sweep mechanism, where the sweep is the setup)."""
    j0=m5_after(T)
    if j0<=3 or j0>=n5-2: return None
    end=min(j0+TRIG_WIN, n5-2); swept=False
    for j in range(j0,end):
        if kind=="mom":       # momentum toward range interior: down-close for short, up-close for long
            if side>0 and m5c[j] > m5o[j] and m5c[j] > m5c[j-1]: return j+1
            if side<0 and m5c[j] < m5o[j] and m5c[j] < m5c[j-1]: return j+1
        elif kind=="mbos":    # micro break of the last 3 M5 bars toward interior
            if side>0 and m5c[j] > max(m5h[j-1],m5h[j-2],m5h[j-3]): return j+1
            if side<0 and m5c[j] < min(m5l[j-1],m5l[j-2],m5l[j-3]): return j+1
        elif kind=="reclaim":
            if side>0:
                if m5l[j] < level: swept=True
                if swept and m5c[j] > level: return j+1
            else:
                if m5h[j] > level: swept=True
                if swept and m5c[j] < level: return j+1
    return None

def walk(entry_j, side, stop_px, tgt_px):
    if entry_j<=0 or entry_j>=n5-1: return None
    entry=m5o[entry_j]; end=min(entry_j+MAXHOLD,n5); ex=None; mae=0.0; mfe=0.0
    for j in range(entry_j,end):
        mfe=max(mfe,(m5h[j]-entry) if side>0 else (entry-m5l[j])); mae=max(mae,(entry-m5l[j]) if side>0 else (m5h[j]-entry))
        if side>0:
            if m5l[j]<=stop_px: ex=stop_px; break
            if m5h[j]>=tgt_px: ex=tgt_px; break
        else:
            if m5h[j]>=stop_px: ex=stop_px; break
            if m5l[j]<=tgt_px: ex=tgt_px; break
    if ex is None: ex=m5c[end-1]
    return entry,ex,mae,mfe

# ---------- H1 RANGE setups (sided). return list of (i, side, boundary_level) ----------
TOL=0.0015
def sig_reject(long):
    s=1 if long else -1; out=[]
    for i in range(W+1,nH):
        if not in_range[i] or not (width[i]>0): continue
        if long and h1l[i] <= rlo[i] + TOL*rlo[i] and h1c[i] > rlo[i]: out.append((i,s,rlo[i]))
        elif (not long) and h1h[i] >= rhi[i] - TOL*rhi[i] and h1c[i] < rhi[i]: out.append((i,s,rhi[i]))
    return out
def sig_sweep(long):
    s=1 if long else -1; out=[]
    for i in range(W+1,nH):
        if not in_range[i] or not (width[i]>0): continue
        if long and h1l[i] < rlo[i] and h1c[i] > rlo[i]: out.append((i,s,rlo[i]))      # swept low, closed back in
        elif (not long) and h1h[i] > rhi[i] and h1c[i] < rhi[i]: out.append((i,s,rhi[i]))
    return out
# lagged range reference (as of 4 bars ago) so the break bars are NOT in the range definition
rhi4 = pd.Series(h1h).rolling(W).max().shift(4).to_numpy()
rlo4 = pd.Series(h1l).rolling(W).min().shift(4).to_numpy()
def sig_failbreak(long):
    # failed breakout(short)/breakdown(long): price broke the (lagged) boundary in last 3 bars, now closes back inside
    s=1 if long else -1; out=[]
    for i in range(W+5,nH):
        if not (width[i]>0): continue
        if long and np.isfinite(rlo4[i]) and np.min(h1l[i-2:i+1]) < rlo4[i] and h1c[i] > rlo4[i]: out.append((i,s,rlo4[i]))
        elif (not long) and np.isfinite(rhi4[i]) and np.max(h1h[i-2:i+1]) > rhi4[i] and h1c[i] < rhi4[i]: out.append((i,s,rhi4[i]))
    return out
def sig_exhaustion(long):
    # repeated-test exhaustion: >=3 tests of the boundary within the window, current bar tests + rejects
    s=1 if long else -1; out=[]
    for i in range(W+1,nH):
        if not in_range[i] or not (width[i]>0): continue
        nt = touch_lo[i] if long else touch_hi[i]
        if nt < 3: continue
        if long and h1l[i] <= rlo[i] + TOL*rlo[i] and h1c[i] > rlo[i]: out.append((i,s,rlo[i]))
        elif (not long) and h1h[i] >= rhi[i] - TOL*rhi[i] and h1c[i] < rhi[i]: out.append((i,s,rhi[i]))
    return out

def htf_stop(i, side, level):
    a=h1atr[i]; a=a if a==a else 0.5
    return (level - 0.25*a) if side>0 else (level + 0.25*a)   # H1 structural: just outside the range boundary
def htf_target(i, side, entry_ref, tp_mode):
    if tp_mode=="mid": return rmid[i]
    if tp_mode=="opp": return (rhi[i]-0.10*width[i]) if side>0 else (rlo[i]+0.10*width[i])
    if tp_mode=="q":  # opposite quartile
        return (rlo[i]+0.75*width[i]) if side>0 else (rhi[i]-0.75*width[i])
    return entry_ref  # fallback

def run(sig_fn, long, m5kind, tp_mode, split="dev"):
    side=1 if long else -1; sigs=sig_fn(long); A=[]; B=[]; missed=0; lastA=-1; lastB=-1
    for (i,s,level) in sigs:
        is_d=bool(h1dev[i]); is_c=bool(h1cal[i])
        if split=="dev" and not is_d: continue
        if split=="cal" and not is_c: continue
        T=h1ct[i]; j_ref=m5_after(T)
        if j_ref<=0 or j_ref>=n5-1: continue
        stop_px=htf_stop(i,side,level); entry_ref=m5o[j_ref]; tgt_px=htf_target(i,side,entry_ref,tp_mode)
        risk_ref=abs(entry_ref-stop_px)
        # geometry validity: correct ordering + target beyond entry in trade dir + inside-range target
        if not (risk_ref>0): continue
        if side>0 and not (stop_px<entry_ref<tgt_px): continue
        if side<0 and not (stop_px>entry_ref>tgt_px): continue
        loc = (entry_ref-rlo[i])/width[i] if side>0 else (rhi[i]-entry_ref)/width[i]  # normalized dist from boundary
        rr_eff = abs(tgt_px-entry_ref)/risk_ref
        base=dict(i=int(i), risk_ref=risk_ref, width=width[i], loc=loc, rr_eff=rr_eff, ntest=int(touch_lo[i] if side>0 else touch_hi[i]),
                  is_dev=is_d, is_cal=is_c)
        # A coarse
        if m5t[j_ref] > lastA:
            wa=walk(j_ref,side,stop_px,tgt_px)
            if wa is not None:
                e,ex,mae,mfe=wa; lastA=m5t[min(j_ref+MAXHOLD,n5-1)]
                Ra=(side*(ex-e)-RT["STRESS"])/risk_ref
                awin=abs(ex-tgt_px)<1e-6
                A.append({**base,"entry":e,"ex":ex,"mae":mae,"mfe":mfe,"R":Ra,"win":awin,"t":int(m5t[j_ref])})
        # B M5 confirmation
        ej=m5_confirm(T,side,level,m5kind)
        if ej is not None and m5t[ej] > lastB:
            wb=walk(ej,side,stop_px,tgt_px)
            if wb is not None:
                e,ex,mae,mfe=wb; lastB=m5t[min(ej+MAXHOLD,n5-1)]
                loc_b=(e-rlo[i])/width[i] if side>0 else (rhi[i]-e)/width[i]
                Rb=(side*(ex-e)-RT["STRESS"])/risk_ref
                B.append({**base,"entry":e,"ex":ex,"mae":mae,"mfe":mfe,"R":Rb,"win":abs(ex-tgt_px)<1e-6,"loc":loc_b,
                          "entry_edge":side*(entry_ref-e),"t":int(m5t[ej])})
    return dict(A=A,B=B,missed=missed)

def summ(tr, dev=True):
    r=[x for x in tr if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return dict(n=0)
    R=np.array([x["R"] for x in r]); wins=np.array([x["win"] for x in r]); n=len(R)
    sl=np.array([x["risk_ref"]/PIP for x in r]); rr=np.array([x["rr_eff"] for x in r]); tp=sl*rr
    wid=np.array([x["width"]/PIP for x in r]); loc=np.array([x["loc"] for x in r]); mae=np.array([x["mae"]/PIP for x in r]); mfe=np.array([x["mfe"]/PIP for x in r])
    eq=np.cumsum(R); dd=float((np.maximum.accumulate(eq)-eq).max()); l=R[R<=0]; w=R[R>0]
    Rs=np.sort(R)[::-1]
    return dict(n=n, WR=round(float(wins.mean()),3), avg_R=round(float(R.mean()),4), med_R=round(float(np.median(R)),3),
                pf=round(float(w.sum()/-l.sum()),3) if l.sum()<0 else None, maxDD=round(dd,2),
                best1_rem=round(float(Rs[max(1,int(n*.01)):].mean()),4), best5_rem=round(float(Rs[max(1,int(n*.05)):].mean()),4),
                rr_eff=round(float(np.median(rr)),2), med_SL_pips=round(float(np.median(sl)),1), med_TP_pips=round(float(np.median(tp)),1),
                pct_TP70=round(float((tp>=70).mean()),3), pct_TP80=round(float((tp>=80).mean()),3), pct_TP100=round(float((tp>=100).mean()),3),
                med_width_pips=round(float(np.median(wid)),1), med_loc=round(float(np.median(loc)),3), med_MAE=round(float(np.median(mae)),1), med_MFE=round(float(np.median(mfe)),1))

# ---------- registry (<=50 IDs) ----------
MECHS=[("reject",sig_reject,"mom"),("sweep",sig_sweep,"reclaim"),("failbreak",sig_failbreak,"mom"),("exhaust",sig_exhaustion,"mom")]
REG=[]
for mname,fn,m5k in MECHS:
    for long in (True,False):
        for tp in ("mid","opp"):
            REG.append(dict(id=f"RM-{mname}-{'L' if long else 'S'}-{tp}", mech=mname, long=long, fn=fn, m5=m5k, tp=tp))
# one M5-confirmation-type variant (mbos) on the reject mechanism, both sides, tp=mid, to test M5 kind
for long in (True,False):
    REG.append(dict(id=f"RM-reject-{'L' if long else 'S'}-mid-mbos", mech="reject", long=long, fn=sig_reject, m5="mbos", tp="mid"))

def falsify(s):  # evaluate an arm (coarse OR m5) on its own robustness
    if s.get("n",0)<25: return "SPARSE"
    if (s.get("avg_R") or -9)<=0: return "FAIL"
    if (s.get("best5_rem") or -9)<=0: return "TAIL_FRAGILE"
    return "SURVIVE"

log(f"RANGE CAMPAIGN START ids={len(REG)}")
records=[]
for k,h in enumerate(REG):
    res=run(h["fn"],h["long"],h["m5"],h["tp"],"dev")
    A=summ(res["A"]); B=summ(res["B"])
    Bsig=set(x["i"] for x in res["B"]); AonB=summ([a for a in res["A"] if a["i"] in Bsig])  # matched coarse
    stA=falsify(A); stB=falsify(B)
    dWR=round((B.get("WR") or 0)-(AonB.get("WR") or 0),3); dAvg=round((B.get("avg_R") or 0)-(AonB.get("avg_R") or 0),4)  # PURE timing (matched)
    rec=dict(id=h["id"], mech=h["mech"], side=("LONG" if h["long"] else "SHORT"), tp_mode=h["tp"], m5=h["m5"],
             A_coarse=A, A_onBsig=AonB, B_m5=B, timing_dWR=dWR, timing_dAvgR=dAvg,
             status_coarse=stA, status_m5=stB)
    records.append(rec)
    log(f"{h['id']} [{rec['side']} {h['tp']} m5={h['m5']}]: coarse(n={A.get('n')},WR={A.get('WR')},avgR={A.get('avg_R')},b5={A.get('best5_rem')})->{stA} | "
        f"M5(n={B.get('n')},WR={B.get('WR')},avgR={B.get('avg_R')},b5={B.get('best5_rem')},rr={B.get('rr_eff')})->{stB} | "
        f"timing(matched) dAvg={dAvg} dWR={dWR} | medTP={A.get('med_TP_pips')}p medW={A.get('med_width_pips')}p")
    if (k+1)%25==0: json.dump(records,open(os.path.join(SP,f"range_ck_{k+1}.json"),"w"),indent=1,default=float); log(f"CHECKPOINT {k+1}")
survC=[r["id"] for r in records if r["status_coarse"]=="SURVIVE"]; survM=[r["id"] for r in records if r["status_m5"]=="SURVIVE"]
json.dump(dict(records=records,survivors_coarse=survC,survivors_m5=survM),open(os.path.join(SP,"range_records.json"),"w"),indent=1,default=float)
log(f"RANGE_COMPLETE ids={len(records)} coarse_survivors={survC} m5_survivors={survM}")
