"""Deepen transition survivors: CALIB (once, frozen), temporal, tail, and CRITICAL independence check --
is rng2trend_disponly a genuine TRANSITION specialist or a clone of the existing H4 trend longs
(MT-H4-efficiency-L)? Overlap by trade-day."""
import sys, os, json, numpy as np, pandas as pd
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
import transition_campaign as TC
tfs=TC.tfs

SURV=[("TR-H4-rng2trend_disponly-L","H4","rng2trend_disponly",True,1.5),
      ("TR-H4-breakout_retest-L","H4","breakout_retest",True,1.5),
      ("TR-H4-breakout_immediate-L","H4","breakout_immediate",True,1.5),
      ("TR-H1-comp_expansion-L","H1","comp_expansion",True,2.5)]
def cls(cal):
    if cal.get("n",0)<8: return "CALIB_SMALL_N"
    ca=cal.get("avg_R") or -9
    if ca>0 and (cal.get("best5_rem") or -9)>0: return "CALIB_PASS"
    if ca>0: return "CALIB_WEAK"
    return "CALIB_FAIL"
out={}
for cid,tf,mech,long,rr in SURV:
    dev=TC.M(TC.evalc(tf,mech,long,rr,"STRESS","dev"),rr); cal=TC.M(TC.evalc(tf,mech,long,rr,"STRESS","cal"),rr)
    c=cls(cal); out[cid]=dict(tf=tf,mech=mech,DEV=dev,CALIB=cal,CALIB_class=c)
    print(f"{cid} [{tf}]:")
    print(f"   DEV  n={dev['n']} WR={dev['WR']} avgR={dev['avg_R']} PF={dev['pf']} b5={dev['best5_rem']} b10={dev['best10_rem']} medSL={dev['med_SL_pips']}p medTP={dev['med_TP_pips']}p %TP80={dev['pct_TP80']} %TP150={dev['pct_TP150']} temporal={dev['temporal']}")
    print(f"   CALIB n={cal['n']} WR={cal.get('WR')} avgR={cal.get('avg_R')} b5={cal.get('best5_rem')} -> {c}")
json.dump(out,open(os.path.join(SP,"deepen_transition.json"),"w"),indent=1,default=float)

# INDEPENDENCE (day-level): rng2trend_disponly vs the existing H4 trend longs + vs each other
def days(mech,long,tf,extra=None):
    x=tfs[tf]; msk=x["is_dev"].to_numpy(); d=set()
    if extra=="efficiency":  # replicate MT-H4-efficiency-L signal (effic>0.4)
        eff=x["effic"].to_numpy()
        for i in range(51,len(x)-1):
            if msk[i] and eff[i]==eff[i] and eff[i]>0.4: d.add(pd.Timestamp(x["dt"].iloc[i]).strftime("%Y-%m-%d"))
    elif extra=="dispaccept":  # MT-H4-dispaccept-L
        o=x["open"].to_numpy();c=x["close"].to_numpy();atr=x["atr"].to_numpy()
        for i in range(51,len(x)-1):
            if msk[i] and atr[i-1]==atr[i-1] and (c[i-1]-o[i-1])>1.0*atr[i-1] and c[i]>c[i-1]: d.add(pd.Timestamp(x["dt"].iloc[i]).strftime("%Y-%m-%d"))
    else:
        for (i,side) in TC.gen(mech,long,tf):
            if msk[i]: d.add(pd.Timestamp(x["dt"].iloc[i]).strftime("%Y-%m-%d"))
    return d
r2t=days("rng2trend_disponly",True,"H4"); bret=days("breakout_retest",True,"H4"); bimm=days("breakout_immediate",True,"H4")
eff=days(None,True,"H4",extra="efficiency"); disp=days(None,True,"H4",extra="dispaccept")
jac=lambda a,b: round(len(a&b)/max(1,len(a|b)),3)
print("\n=== INDEPENDENCE (H4 LONG day-sets) ===")
print(f"  rng2trend_disponly days={len(r2t)} | efficiency(MT-H4-eff-L)={len(eff)} disp(MT-H4-disp-L)={len(disp)} retest={len(bret)} immediate={len(bimm)}")
print(f"  rng2trend vs MT-H4-efficiency-L: Jaccard {jac(r2t,eff)}")
print(f"  rng2trend vs MT-H4-dispaccept-L: Jaccard {jac(r2t,disp)}")
print(f"  rng2trend vs breakout_retest: Jaccard {jac(r2t,bret)} | breakout_retest vs immediate: Jaccard {jac(bret,bimm)}")
