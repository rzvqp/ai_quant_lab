"""Deepen the HTF-risk M5-entry winners (TU-pb-L). CALIB confirmation, temporal, tail, entry-price
attribution (is M5 value from price or from confirmation-filtering?), full geometry. A vs B throughout."""
import sys, os, json, numpy as np, pandas as pd
SP = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, SP)
import m5entry_htfrisk as H
C=H.C; PIP=H.PIP
def tail(trades, dev=True):
    r=[x for x in trades if (x["is_dev"] if dev else x["is_cal"])]
    if not r: return {}
    R=np.sort(np.array([x["R"] for x in r]))[::-1]; n=len(R)
    return dict(best5_rem=round(float(R[max(1,int(n*.05)):].mean()),4), best10_rem=round(float(R[max(1,int(n*.10)):].mean()),4))
def temporal(trades):
    r=[x for x in trades if x["is_dev"]]; yr={}
    for x in r: yr.setdefault(pd.to_datetime(x["t"],unit="s",utc=True).year,[]).append(x["R"])
    return {int(y):round(float(np.mean(v)),3) for y,v in sorted(yr.items())}
def entry_attr(res):
    b=[x for x in res["B"] if x["is_dev"]]
    if not b: return {}
    ee=np.array([x["entry_edge"]/PIP for x in b])  # +ve = M5 entered BETTER price than coarse
    own=np.array([x["R_own"] for x in b])
    return dict(mean_entry_edge_pips=round(float(ee.mean()),1), pct_better_entry=round(float((ee>0).mean()),3),
                B_ownRR_avgR=round(float(own.mean()),4))

out={}
for hid,rr,up,edge,trig in [("HR-TU-pb-L-rr1.5",1.5,True,C.edge_trend_pullback,"breakout"),
                            ("HR-TU-pb-L-rr2",2.0,True,C.edge_trend_pullback,"breakout"),
                            ("HR-TU-pb-L-rr3",3.0,True,C.edge_trend_pullback,"breakout")]:
    dev=H.run(edge,up,trig,rr,"dev"); cal=H.run(edge,up,trig,rr,"cal")
    A=H.summ(dev["A"],rr); B=H.summ(dev["B"],rr)
    Ac=H.summ(cal["A"],rr,dev=False); Bc=H.summ(cal["B"],rr,dev=False)
    out[hid]=dict(rr=rr,
        DEV_A=dict(n=A["n"],WR=A["WR"],avgR=A["avg_R"],pf=A["pf"],maxDD=A["maxDD"],medSL=A["med_SL_pips"],medTP=A["med_TP_pips"],medMAE=A["med_MAE_pips"],medMFE=A["med_MFE_pips"]),
        DEV_B=dict(n=B["n"],WR=B["WR"],avgR=B["avg_R"],pf=B["pf"],maxDD=B["maxDD"],medSL=B["med_SL_pips"],medTP=B["med_TP_pips"],pctTP70=B["pct_TP70"],pctTP80=B["pct_TP80"],pctTP100=B["pct_TP100"],medMAE=B["med_MAE_pips"],medMFE=B["med_MFE_pips"]),
        dWR=round((B["WR"] or 0)-(A["WR"] or 0),3), dAvgR=round((B["avg_R"] or 0)-(A["avg_R"] or 0),4),
        CALIB_A=dict(n=Ac.get("n"),WR=Ac.get("WR"),avgR=Ac.get("avg_R")), CALIB_B=dict(n=Bc.get("n"),WR=Bc.get("WR"),avgR=Bc.get("avg_R")),
        tail_B=tail(dev["B"]), temporal_B=temporal(dev["B"]), entry_attr=entry_attr(dev), missed_A_wins_byB=dev["missed_A_wins"])
    o=out[hid]
    print(f"== {hid} (rr{rr}) ==")
    print(f"  DEV  A: n={A['n']} WR={A['WR']} avgR={A['avg_R']} PF={A['pf']} maxDD={A['maxDD']} | B(M5): n={B['n']} WR={B['WR']} avgR={B['avg_R']} PF={B['pf']} maxDD={B['maxDD']}")
    print(f"       dWR={o['dWR']} dAvgR={o['dAvgR']} | medSL={B['med_SL_pips']}p medTP={B['med_TP_pips']}p %TP>=70={B['pct_TP70']} >=80={B['pct_TP80']} >=100={B['pct_TP100']} | MAE={B['med_MAE_pips']}p MFE={B['med_MFE_pips']}p")
    print(f"  CALIB A: n={Ac.get('n')} WR={Ac.get('WR')} avgR={Ac.get('avg_R')} | B: n={Bc.get('n')} WR={Bc.get('WR')} avgR={Bc.get('avg_R')}")
    print(f"  tail_B={o['tail_B']} temporal_B={o['temporal_B']}")
    print(f"  entry_attr={o['entry_attr']} (mean_entry_edge>0 => M5 better price; <0 => M5 pays for confirmation) missedWins={o['missed_A_wins_byB']}")
json.dump(out, open(os.path.join(SP,"deepen_htfrisk.json"),"w"), indent=1, default=float)
