"""Deepen the H4 SHORT breakout-continuation cluster (the interim campaign standout) + H1-hllh-S.
Deep tail (best5/10% removed), within-block year concentration, execution degradation (+1 bar entry,
1.5x stop floor), CALIB (block2 out-of-DEV), param neighborhood (breakout lb). DEVELOPMENT b0+b1."""
import sys, os, json
import numpy as np, pandas as pd
from collections import defaultdict
WP5B = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b"
if os.path.join(WP5B, "code") not in sys.path: sys.path.insert(0, os.path.join(WP5B, "code"))
import mstrat
SP = os.path.dirname(os.path.abspath(__file__)); TICK = mstrat.TICK; MKT = os.path.join(WP5B, "data", "market"); PIP = 0.10
BLOCKS = {"b0": (1311697800, 1380300300), "b1": (1452502800, 1523015550), "calib": (1597128300, 1630844100)}
CM = json.load(open(r"C:\Users\MEDION GAMING\ai_quant_lab-research-main\AI_TRADER_SHADOW_COST_MODEL_v1.json"))
RT = {"BASE": CM["base_ratified"]["round_trip_total"], "STRESS": CM["stress_ratified"]["round_trip_total"]}
def load_tf(kind):
    if kind == "M15": d = mstrat.load()[["time","open","high","low","close","m_atr"]].copy()
    else:
        f = {"H1":"OANDA_XAUUSD_H1_from_M15_v2.csv","H4":"OANDA_XAUUSD_H4_from_M15_v2.csv"}[kind]; d = pd.read_csv(os.path.join(MKT,f))
        tr = np.maximum(d["high"]-d["low"], np.maximum((d["high"]-d["close"].shift(1)).abs(),(d["low"]-d["close"].shift(1)).abs())); d["m_atr"]=tr.rolling(14).mean()
    d = d.sort_values("time").reset_index(drop=True)
    coarser = {"M15":"OANDA_XAUUSD_H4_from_M15_v2.csv","H1":"OANDA_XAUUSD_H4_from_M15_v2.csv","H4":"OANDA_XAUUSD_D1_from_M15_v2.csv"}[kind]
    x = pd.read_csv(os.path.join(MKT,coarser)).sort_values("time"); e20=x["close"].ewm(span=20,adjust=True).mean(); e50=x["close"].ewm(span=50,adjust=True).mean(); x["trend_up"]=(e20>e50).astype(float)
    return pd.merge_asof(d, x[["time","trend_up"]].rename(columns={"time":"av"}), left_on="time", right_on="av", direction="backward").drop(columns="av")
def slices(kind):
    d=load_tf(kind); t=d["time"].astype("int64").to_numpy(); return {bn: d[(t>=s)&(t<=e)].reset_index(drop=True) for bn,(s,e) in BLOCKS.items()}
def rmax(a,w): return pd.Series(a).rolling(w).max().shift(1).to_numpy()
def rmin(a,w): return pd.Series(a).rolling(w).min().shift(1).to_numpy()
def _arr(sl): return sl["open"].to_numpy(),sl["high"].to_numpy(),sl["low"].to_numpy(),sl["close"].to_numpy(),sl["m_atr"].to_numpy()

def gen_breakout_short(lb, accept):
    def g(sl):
        o,hi,lo,cl,atr=_arr(sl); L=rmin(lo,lb); out=[]
        for i in range(lb+2,len(sl)-2):
            if not (np.isfinite(L[i]) and cl[i]<L[i]): continue
            if accept:
                if i+1<len(sl) and cl[i+1]<cl[i]: out.append((i+1,L[i]))
            else: out.append((i,L[i]))
        return out
    return g
def gen_eff_short(lb):
    def g(sl):
        o,hi,lo,cl,atr=_arr(sl); net=cl-pd.Series(cl).shift(lb).to_numpy(); path=pd.Series(np.abs(np.diff(cl,prepend=cl[0]))).rolling(lb).sum().shift(1).to_numpy(); out=[]
        for i in range(lb+1,len(sl)-1):
            if np.isfinite(net[i]) and np.isfinite(path[i]) and path[i]>0 and net[i]/path[i]<-0.4: out.append((i, cl[i]+1.2*atr[i] if atr[i]==atr[i] else cl[i]+1))
        return out
    return g
def gen_hllh_short():
    def g(sl):
        o,hi,lo,cl,atr=_arr(sl); out=[]
        for i in range(4,len(sl)-1):
            if hi[i-1]<hi[i-2]<hi[i-3] and cl[i]<lo[i-1]: out.append((i, hi[i-1]))
        return out
    return g

def run(SL, gen, k, scen, blocks=("b0","b1"), entry_delay=0, floor_mult=1.0):
    cfg=dict(mstrat.CFG); cfg["spread_ticks"]=0.0; cfg["slip_ticks"]=RT[scen]/(2*TICK); out=[]
    for bn in blocks:
        sl=SL[bn]; o,hi,lo,cl,atr=_arr(sl); tu=sl["trend_up"].to_numpy(); nb=len(sl); yr=pd.to_datetime(sl["time"],unit="s",utc=True).dt.year.to_numpy(); setups=[]; meta={}
        for (i,brk) in gen(sl):
            if not (0<i<nb-1) or tu[i]>0.5: continue  # short => require trend DOWN (tu<=0.5)
            ei=min(i+1+entry_delay,nb-1)
            if ei>=nb-1 or atr[i]!=atr[i]: continue
            entry=o[ei]; sl_usd=max(abs(entry-brk)+0.3*atr[i], 0.8*atr[i])*floor_mult
            if not (sl_usd>0): continue
            setups.append(dict(si=i, ei=ei, dir=-1, stop=float(entry+sl_usd), exit_kind="rr", exit_param=float(k))); meta[i]=yr[i]
        led=mstrat.simulate(sl,setups,cfg)
        for r,si in zip(led["R"],led["si"]): out.append(dict(r=float(r),block=bn,year=int(meta.get(int(si),0))))
    return out
def M(res, k=None):
    if not res: return dict(n=0)
    r=np.sort(np.array([x["r"] for x in res]))[::-1]; nn=len(r); tot=float(r.sum()); rem=lambda p: round(float(r[max(1,int(nn*p)):].mean()),4)
    byb=defaultdict(float); byy=defaultdict(float)
    for x in res: byb[x["block"]]+=x["r"]; byy[x["year"]]+=x["r"]
    pbavg={}
    for bn in ("b0","b1"):
        rr=[x["r"] for x in res if x["block"]==bn]; pbavg[bn]=round(float(np.mean(rr)),4) if rr else None
    wr=round(float((np.array([x["r"] for x in res])>= (k-0.05 if k else 0.0)).mean()),3) if k else None
    return dict(n=nn, avg=round(float(r.mean()),4), win=wr, best5_rem=rem(0.05), best10_rem=rem(0.10),
                maxYr_share=round(max(byy.values())/tot,3) if tot>0 else None, pb_avg=pbavg)

CANDS = [("H4","bo-raw-S",gen_breakout_short(20,False)), ("H4","bo-acc-S",gen_breakout_short(20,True)),
         ("H4","eff-S",gen_eff_short(8)), ("H1","hllh-S",gen_hllh_short())]
SLc = {"H4": slices("H4"), "H1": slices("H1")}
deep = {}
for tf, name, gen in CANDS:
    SL = SLc[tf]
    for k in (1.5, 2.0, 3.0, 4.0):
        base=M(run(SL,gen,k,"BASE"),k); s=M(run(SL,gen,k,"STRESS"),k)
        if s.get("n",0) < 50: continue
        cal=M(run(SL,gen,k,"STRESS",blocks=("calib",)),k)
        ed=M(run(SL,gen,k,"STRESS",entry_delay=1),k); ef=M(run(SL,gen,k,"STRESS",floor_mult=1.5),k)
        tail_ok=(s["best5_rem"] or -9)>0; conc_ok=(s["maxYr_share"] or 9)<=0.6; both=(base["pb_avg"]["b0"] or -9)>0 and (base["pb_avg"]["b1"] or -9)>0
        exec_ok=(ed["avg"] or -9)>0 and (ef["avg"] or -9)>0; calib_ok=(cal["avg"] or -9)>0
        verdict="ROBUST" if (tail_ok and conc_ok and both and exec_ok and calib_ok) else ("STRONG_PARTIAL" if (tail_ok and both and exec_ok) else "FRAGILE")
        cid=f"{tf}-{name}-rr{k}"; deep[cid]=dict(tf=tf,name=name,k=k,STRESS_avg=s["avg"],WR=s["win"],n=s["n"],best5_rem=s["best5_rem"],best10_rem=s["best10_rem"],
            maxYr=s["maxYr_share"],pb_avg=base["pb_avg"],CALIB_avg=cal["avg"],CALIB_n=cal["n"],exec_delay=ed["avg"],exec_floor=ef["avg"],
            flags=dict(tail_ok=tail_ok,conc_ok=conc_ok,both_blocks=both,exec_ok=exec_ok,calib_ok=calib_ok),verdict=verdict)
        print(f"{cid}: STRESS={s['avg']} WR={s['win']} n={s['n']} b5rem={s['best5_rem']} b10rem={s['best10_rem']} maxYr={s['maxYr_share']} pb={base['pb_avg']} CALIB={cal['avg']}(n{cal['n']}) exD={ed['avg']} exF={ef['avg']} -> {verdict}")
json.dump(deep, open(os.path.join(SP,"deepen_econ.json"),"w"), indent=1, default=float)
rob=[k for k,v in deep.items() if v["verdict"]=="ROBUST"]; sp=[k for k,v in deep.items() if v["verdict"]=="STRONG_PARTIAL"]
print(f"\nROBUST={rob}\nSTRONG_PARTIAL={sp}")
