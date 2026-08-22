"""Deepen the multi-TF survivors: CALIB (decisive gate, once, frozen), temporal, tail, geometry,
independence vs existing portfolio. Classify CALIB_PASS/WEAK/FAIL."""
import sys, os, json, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import multitf_campaign as MC
tfs=MC.tfs

SURV=[("MT-H4-efficiency-L","H4","efficiency",True,1.5),
      ("MT-H4-pullback-L","H4","pullback",True,1.5),
      ("MT-H4-dispaccept-L","H4","dispaccept",True,1.5),
      ("MT-H4-momentum-L","H4","momentum",True,1.5),
      ("MT-H1-pullback-L","H1","pullback",True,2.5),
      ("MT-H1-breakout-S","H1","breakout",False,2.5)]
def calib_class(dev_avg,cal):
    if cal.get("n",0)<8: return "CALIB_SMALL_N"
    ca=cal.get("avg_R") or -9
    if ca>0 and (cal.get("best5_rem") or -9)>0: return "CALIB_PASS"
    if ca>0: return "CALIB_WEAK"
    return "CALIB_FAIL"
out={}
for cid,tf,mech,long,rr in SURV:
    dev=MC.M(MC.eval_tf(tf,mech,long,rr,"STRESS","dev"),rr)
    cal=MC.M(MC.eval_tf(tf,mech,long,rr,"STRESS","cal"),rr)
    cls=calib_class(dev["avg_R"],cal)
    out[cid]=dict(tf=tf,mech=mech,dir=("LONG" if long else "SHORT"),rr=rr,
                  DEV=dict(n=dev["n"],WR=dev["WR"],avgR=dev["avg_R"],pf=dev["pf"],b5=dev["best5_rem"],b10=dev["best10_rem"],medSL=dev["med_SL_pips"],medTP=dev["med_TP_pips"],pctTP70=dev["pct_TP70"],pctTP80=dev["pct_TP80"],temporal=dev["temporal"]),
                  CALIB=dict(n=cal["n"],WR=cal["WR"],avgR=cal["avg_R"],b5=cal["best5_rem"]),CALIB_class=cls)
    print(f"{cid} [{tf} {out[cid]['dir']} rr{rr}]:")
    print(f"   DEV  n={dev['n']} WR={dev['WR']} avgR={dev['avg_R']} PF={dev['pf']} b5={dev['best5_rem']} b10={dev['best10_rem']} medSL={dev['med_SL_pips']}p medTP={dev['med_TP_pips']}p temporal={dev['temporal']}")
    print(f"   CALIB n={cal['n']} WR={cal.get('WR')} avgR={cal.get('avg_R')} b5={cal.get('best5_rem')} -> {cls}")
json.dump(out,open(os.path.join(SP,"deepen_multitf.json"),"w"),indent=1,default=float)

# independence: top H4 candidate day-set vs existing references (regime + overlap where computable)
print("\n=== INDEPENDENCE (top H4 candidates are LONG; H4-bo-raw-S is SHORT -> directionally independent) ===")
def daysig(tf,mech,long,rr):
    x=tfs[tf]; msk=x["is_dev"].to_numpy(); days=set()
    for (i,side) in MC.gen(mech,long,x):
        if msk[i]: days.add(pd.Timestamp(x["dt"].iloc[i]).strftime("%Y-%m-%d"))
    return days
eff=daysig("H4","efficiency",True,1.5); pb=daysig("H4","pullback",True,1.5); h1pb=daysig("H1","pullback",True,2.5)
jac=lambda a,b: round(len(a&b)/max(1,len(a|b)),3)
print(f"  H4-efficiency-L days={len(eff)} vs H4-pullback-L days={len(pb)}: Jaccard {jac(eff,pb)} (same-TF LONG mechanisms -> some overlap expected)")
print(f"  H4-efficiency-L vs H1-pullback-L: Jaccard {jac(eff,h1pb)}")
print(f"  vs HR-TU-pb-L / IR-DIR-L-mid: different TF/regime; H4-bo-raw-S is SHORT -> directionally orthogonal")
