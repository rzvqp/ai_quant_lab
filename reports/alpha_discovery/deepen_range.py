"""Deepen + scrutinize the RANGE short survivors. Decompose M5 value into FILTERING (A_all vs A|B) and
TIMING (A|B vs B) with matched signals. Temporal, CALIB, tail, R-buckets, entry-location, example trades."""
import sys, os, json, numpy as np, pandas as pd
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import range_m5 as R
PIP=R.PIP; RT=R.RT

def rbuckets(tr):
    r=[x for x in tr if x["is_dev"]]
    if not r: return {}
    R_=np.array([x["R"] for x in r]); n=len(R_); win=np.array([x["win"] for x in r])
    at_stop=float((R_<=-0.98).mean()); at_tgt=float(win.mean())
    tepos=float(((~win)&(R_>-0.98)&(R_>0)).mean()); teneg=float(((~win)&(R_>-0.98)&(R_<=0)).mean())
    return dict(pct_target=round(at_tgt,3), pct_stop=round(at_stop,3), pct_TEpos=round(tepos,3), pct_TEneg=round(teneg,3))
def tailtemporal(tr):
    r=[x for x in tr if x["is_dev"]]
    if not r: return {},{}
    R_=np.sort(np.array([x["R"] for x in r]))[::-1]; n=len(R_)
    tail=dict(best1=round(float(R_[max(1,int(n*.01)):].mean()),4), best5=round(float(R_[max(1,int(n*.05)):].mean()),4), best10=round(float(R_[max(1,int(n*.1)):].mean()),4))
    yr={}
    for x in r: yr.setdefault(pd.to_datetime(x["t"],unit="s",utc=True).year,[]).append(x["R"])
    return tail, {int(y):round(float(np.mean(v)),3) for y,v in sorted(yr.items())}

CANDS=[("RM-reject-S-mid",R.sig_reject,False,"reject","mid"),("RM-reject-S-opp",R.sig_reject,False,"reject","opp")]
for cid,fn,long,m5,tp in CANDS:
    dev=R.run(fn,long,m5,tp,"dev"); cal=R.run(fn,long,m5,tp,"cal")
    A=dev["A"]; B=dev["B"]; Bsig=set(x["i"] for x in B)
    A_onB=[a for a in A if a["i"] in Bsig]   # matched: coarse entry on the SAME signals M5 fired
    sA=R.summ(A); sAonB=R.summ(A_onB); sB=R.summ(B); sBc=R.summ(cal["B"],dev=False); sAc=R.summ(cal["A"],dev=False)
    tail,temp=tailtemporal(B)
    # entry-location concentration (B): profit by loc bucket (dist from boundary)
    b=[x for x in B if x["is_dev"]]; loc=np.array([x["loc"] for x in b]); Rb=np.array([x["R"] for x in b])
    within={f"<={t}": (round(float(Rb[loc<=t].mean()),3), int((loc<=t).sum())) for t in (0.10,0.20,0.25)}
    print(f"\n===== {cid} (tp={tp}) =====")
    print(f"  A_all : n={sA['n']} WR={sA['WR']} avgR={sA['avg_R']} pf={sA['pf']}")
    print(f"  A|B   : n={sAonB['n']} WR={sAonB['WR']} avgR={sAonB['avg_R']} pf={sAonB['pf']}   (matched coarse)")
    print(f"  B(M5) : n={sB['n']} WR={sB['WR']} avgR={sB['avg_R']} pf={sB['pf']} rr={sB['rr_eff']} medTP={sB['med_TP_pips']}p medSL={sB['med_SL_pips']}p maxDD={sB['maxDD']}")
    print(f"  => FILTERING value (A|B - A_all): dAvg={round((sAonB['avg_R'] or 0)-(sA['avg_R'] or 0),4)}  |  TIMING value (B - A|B): dAvg={round((sB['avg_R'] or 0)-(sAonB['avg_R'] or 0),4)} dWR={round((sB['WR'] or 0)-(sAonB['WR'] or 0),3)}")
    print(f"  Rbuckets(B)={rbuckets(B)}  tail(B)={tail}")
    print(f"  temporal(B)={temp}  CALIB B: n={sBc.get('n')} WR={sBc.get('WR')} avgR={sBc.get('avg_R')} | A: n={sAc.get('n')} avgR={sAc.get('avg_R')}")
    print(f"  entry within X of boundary (avgR,n): {within}")
    # example trades
    print("  examples (entry, stop_implied, R, win):")
    for x in b[:6]:
        print(f"    i={x['i']} entry={x['entry']:.2f} riskref={x['risk_ref']:.2f} rr_eff={x['rr_eff']:.2f} R={x['R']:.3f} win={x['win']} loc={x['loc']:.3f} width={x['width']:.1f}")
