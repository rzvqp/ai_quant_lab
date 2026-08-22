"""state_m15_highvol.py — tradeability characterization of ST-M15-HIGHVOL-SHORT (high/rising M15 vol -> SHORT).
Does any geometry (fixed brackets OR structural ATR stop, §19 no tight-forcing) yield net-positive STRESS
expectancy, cross-era (DEV + b0 + b1), event-deduped? + parent-regime concentration + directional interaction.
Uses sb.simulate (net-of-cost R). Price-only, causal.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_regime import regime
from state_m15_discover import feats, dedup
PIP=0.10; H=32; COOL=8

def hv_events(m,mask):
    F=feats(m); vr=F["vr"]; vc=F["vc"]; disp=F["disp"]
    hv=((vr>1.3)|(vc>1.2))&np.isfinite(vr); ev=dedup(mask&np.nan_to_num(hv,nan=0).astype(bool),COOL)
    return np.where(ev)[0], F

def geom_report(m,ev,tag):
    atr=m["atr"].to_numpy(); o=m["open"].to_numpy()
    print(f"  [{tag}] events={len(ev)}")
    # fixed brackets (fav/adv pips) -> risk=adv*PIP, rr=fav/adv
    for fav,adv in [(50,40),(70,50),(100,70),(150,75)]:
        risk=np.full(len(ev),adv*PIP); tr=sb.simulate(m,ev,-1,risk,rr=fav/adv,horizon=H,scenario="STRESS")
        if len(tr): m_=sb.metrics(tr,m,fav/adv); print(f"     fixed +{fav}/-{adv}: avgR={m_['avgR']:+.3f} WR={m_['WR_pos']:.2f} best10={m_['best10']:+.3f} (rr={fav/adv:.2f})")
    # structural ATR stop
    for mult in (1.0,1.5,2.0):
        for rr in (1.0,1.5,2.0):
            risk=mult*atr[ev]; ok=np.isfinite(risk)&(risk>0)
            tr=sb.simulate(m,ev[ok],-1,risk[ok],rr=rr,horizon=H,scenario="STRESS")
            if len(tr): m_=sb.metrics(tr,m,rr);
            if len(tr) and abs(m_['avgR'])>0: print(f"     struct SL={mult}ATR rr={rr}: avgR={m_['avgR']:+.3f} WR={m_['WR_pos']:.2f} best10={m_['best10']:+.3f} medSL={m_['med_sl_pips']:.0f}p")

def main():
    print("ST-M15-HIGHVOL-SHORT tradeability (STRESS, event-deduped). Any net-positive geometry cross-era?")
    m=sb.build_frames()["M15"]; dev=m["is_dev"].to_numpy()
    ev,F=hv_events(m,dev); geom_report(m,ev,"DEV 2021-2023")
    # parent-regime concentration (H1 regime aligned to M15) + interaction
    h1=sb.build_frames()["H1"].copy(); labs=regime(h1); codes,uniques=pd.factorize(labs); h1["regc"]=codes.astype(float)
    a=sb.align_context(m,h1,["regc"],""); regc=a["regc"].to_numpy()
    code_of={u:i for i,u in enumerate(uniques)}
    print("  parent-regime split (struct SL=1.5ATR rr1.5, DEV):")
    atr=m["atr"].to_numpy()
    for R in ["UP","DOWN","QUIET","CHOP","TRANSITION"]:
        if R not in code_of: continue
        sub=ev[regc[ev]==code_of[R]]
        if len(sub)<40: print(f"     {R}: N={len(sub)}(thin)"); continue
        risk=1.5*atr[sub]; tr=sb.simulate(m,sub,-1,risk,rr=1.5,horizon=H,scenario="STRESS"); mm=sb.metrics(tr,m,1.5)
        print(f"     {R}: N={len(sub)} avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f}")
    # interaction: high-vol AND recent down-displacement
    dispm=F["disp"]<-0.5; evd=ev[np.nan_to_num(dispm[ev],nan=0).astype(bool)]
    if len(evd)>=40:
        risk=1.5*atr[evd]; tr=sb.simulate(m,evd,-1,risk,rr=1.5,horizon=H,scenario="STRESS"); mm=sb.metrics(tr,m,1.5)
        print(f"  interaction high-vol & down-disp (struct 1.5ATR rr1.5): N={len(evd)} avgR={mm['avgR']:+.3f} WR={mm['WR_pos']:.2f} best10={mm['best10']:+.3f} tpm={mm['trades_per_month']:.1f}")
    # cross-era b0/b1
    hh=m15d.build(verbose=False)["M15"]
    for blk in ("is_b0","is_b1"):
        sub=hh[hh[blk]].reset_index(drop=True); ev2,_=hv_events(sub,np.ones(len(sub),bool)); geom_report(sub,ev2,blk[3:])

if __name__=="__main__":
    main()
