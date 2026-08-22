"""Diagnostic + deepening for the H1-M5 survivors. Validate the low WR (R-distribution buckets),
mandatory H1-COARSE vs M5-TRIGGER value delta, tail best5/10, temporal, CALIB, RR neighborhood."""
import sys, os, json
import numpy as np, pandas as pd
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import h1m5_campaign as C   # re-runs the 28-ID campaign (~1s) and exposes engine + edge fns
RT = C.RT; PIP = C.PIP

def rdist(rows, rr, scen="STRESS"):
    r=[x for x in rows if x["is_dev"]]
    if not r: return dict(n=0)
    R=np.array([(x["dir"]*(x["ex"]-x["entry"])-RT[scen])/x["risk"] for x in r])
    n=len(R)
    at_target=float((R>=rr-0.05).mean()); at_stop=float((R<=-0.98).mean())
    te_pos=float(((R>-0.98)&(R<rr-0.05)&(R>0)).mean()); te_neg=float(((R>-0.98)&(R<rr-0.05)&(R<=0)).mean())
    return dict(n=n, avg_R=round(float(R.mean()),4), pct_at_target=round(at_target,3), pct_at_stop=round(at_stop,3),
                pct_timeexit_pos=round(te_pos,3), pct_timeexit_neg=round(te_neg,3))

byid={h["id"]:h for h in C.REG}
TARGETS=["TU-pb-L-A2","TU-pb-L-B3","TU-pb-L-B4","TB-bo-L-B3","RG-rej-L-A2","RG-rej-L-B3"]
out={}
for hid in TARGETS:
    h=byid[hid]
    m5rows=C.run_candidate(h["edge"],h["up"],h["trig"],h["rr"],"m5")
    coarserows=C.run_candidate(h["edge"],h["up"],h["trig"],h["rr"],"coarse")
    m5=C.metrics(m5rows,h["rr"],"STRESS"); co=C.metrics(coarserows,h["rr"],"STRESS")
    m5b=C.metrics(m5rows,h["rr"],"BASE"); cal=C.metrics([x for x in m5rows if x["is_cal"]] and m5rows,h["rr"],"STRESS",dev_only=False)
    calm=C.metrics([x for x in m5rows], h["rr"],"STRESS",dev_only=False)  # placeholder
    # CALIB-only metrics
    cal_rows=[x for x in m5rows if x["is_cal"]]
    calc=C.metrics(cal_rows,h["rr"],"STRESS",dev_only=False) if cal_rows else dict(n=0)
    dist=rdist(m5rows,h["rr"])
    out[hid]=dict(regime=h["regime"],dir=("LONG" if h["up"] else "SHORT"),profile=h["profile"],rr=h["rr"],
                  M5=dict(n=m5["n"],avgR=m5["avg_R"],WR=m5["win_rate"],best5=m5["best5_rem"],best10=m5["best10_rem"],medTP=m5["med_TP_pips"],medSL=m5["med_SL_pips"],pf=m5["pf"]),
                  COARSE=dict(n=co.get("n"),avgR=co.get("avg_R"),WR=co.get("win_rate"),best5=co.get("best5_rem")),
                  M5_value_delta=dict(dAvgR=round((m5["avg_R"] or 0)-(co.get("avg_R") or 0),4), dWR=round((m5["win_rate"] or 0)-(co.get("win_rate") or 0),3), dN=(m5["n"] or 0)-(co.get("n") or 0)),
                  BASE_avgR=m5b["avg_R"], CALIB=dict(n=calc.get("n"),avgR=calc.get("avg_R")),
                  temporal=C.temporal(m5rows,h["rr"]), Rdist=dist)
    print(f"{hid} [{h['regime']}] {out[hid]['dir']} P{h['profile']} rr{h['rr']}:")
    print(f"   M5: n={m5['n']} avgR={m5['avg_R']} WR={m5['win_rate']} b5={m5['best5_rem']} b10={m5['best10_rem']} PF={m5['pf']} medTP={m5['med_TP_pips']}p")
    print(f"   COARSE: n={co.get('n')} avgR={co.get('avg_R')} WR={co.get('win_rate')} | M5 value dAvgR={out[hid]['M5_value_delta']['dAvgR']} dWR={out[hid]['M5_value_delta']['dWR']}")
    print(f"   Rdist: target={dist['pct_at_target']} stop={dist['pct_at_stop']} TEpos={dist['pct_timeexit_pos']} TEneg={dist['pct_timeexit_neg']} | CALIB n={calc.get('n')} avgR={calc.get('avg_R')} | temporal={out[hid]['temporal']}")
json.dump(out, open(os.path.join(SP,"deepen_h1m5.json"),"w"), indent=1, default=float)
