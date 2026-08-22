"""dxy_divergence_incremental.py — DXY Stage: X3 divergence (§6) + §7 incremental-over-price-only test.
X3: XAUUSD not reacting as normally expected to a DXY move (gold resilient to USD strength = bullish; gold weak
despite USD weakness = bearish). DXY-move threshold estimated on DISC only (no hindsight), frozen, applied
cross-era. §7: does persistent-DXY-direction add XAUUSD path lift CONDITIONAL on the XAUUSD parent regime, or
merely re-encode trend/vol already in price (-> REDUNDANT_EXTERNAL_INFORMATION)? Causal, event-deduped, cross-era.
"""
import numpy as np, pandas as pd
import dxy_data as dd
from state_regime import regime
from state_path_m15 import passage_m15, Pm
from state_m15_discover import dedup
COOL=6; H=24
ERAS=["b0","b1","y2123"]
STATES=["UP","DOWN","QUIET","CHOP","TRANSITION"]

def prep(m):
    ou,od,_,_=passage_m15(m,Hmax=H)
    c=m["close"].to_numpy(); xret4=c-pd.Series(c).shift(4).to_numpy()
    d4=m["d_ret4_l0"].to_numpy(); effdn=m["d_eff_l0"].to_numpy()< -0.4; effup=m["d_eff_l0"].to_numpy()>0.4
    lab=regime(m)
    return ou,od,xret4,d4,effdn,effup,lab

def main():
    frames=dd.build(verbose=False); P={era:frames[era] for era in ERAS}
    prepped={era:prep(P[era]) for era in ERAS}
    # ---- X3 divergence ----
    print("X3 DIVERGENCE: gold NOT reacting to a material DXY move. DXY threshold from DISC only. Lift vs XAUUSD base.")
    print("  div_bull = DXY up strongly & XAUUSD did NOT fall -> LONG ; div_bear = DXY down strongly & XAUUSD did NOT rise -> SHORT")
    for era in ERAS:
        m=P[era]; ou,od,xret4,d4,effdn,effup,lab=prepped[era]
        n=len(m); disc=np.zeros(n,bool); disc[:int(n*0.6)]=True
        thr=np.nanpercentile(np.abs(d4[disc]),70)  # DISC-only DXY-move threshold (frozen)
        bull=(d4>thr)&(xret4>=0); bear=(d4< -thr)&(xret4<=0)
        allm=dedup(np.ones(n,bool),COOL)
        bL=Pm(ou,od,70,50,'L',H,allm)[0]; bS=Pm(ou,od,70,50,'S',H,allm)[0]
        for nm,cond,side,base in (("div_bull",bull,'L',bL),("div_bear",bear,'S',bS)):
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool); dd_=cond&dedup(cond,COOL); nE=int(dd_.sum())
            if nE<40: print(f"   {era} {nm}->{side}: thin(n{nE})"); continue
            lift=Pm(ou,od,70,50,side,H,dd_)[0]-base
            # DISC/CONF split
            dl=Pm(ou,od,70,50,side,H,dd_&disc)[0]-Pm(ou,od,70,50,side,H,allm&disc)[0] if (dd_&disc).sum()>=25 else float('nan')
            cl=Pm(ou,od,70,50,side,H,dd_&~disc)[0]-Pm(ou,od,70,50,side,H,allm&~disc)[0] if (dd_&~disc).sum()>=25 else float('nan')
            print(f"   {era} {nm}->{side}: thr={thr:.2f}pts base={base:.2f} lift={lift:+.3f}(EffN {nE}) DISC={dl:+.3f} CONF={cl:+.3f}")
    # ---- §7 incremental test: dxyEffDn/Up within XAUUSD parent regime ----
    print("\n§7 INCREMENTAL: does persistent-DXY-direction add LONG/SHORT path lift OVER the XAUUSD parent regime?")
    print("  dxyEffDn->L incremental within each XAUUSD parent state (parent+DXY vs parent alone), per era:")
    for era in ERAS:
        m=P[era]; ou,od,xret4,d4,effdn,effup,lab=prepped[era]
        cells=[]
        for R in STATES:
            base_mask=(lab==R)&dedup(lab==R,COOL); nb=int(base_mask.sum())
            cond_mask=(lab==R)&effdn&dedup((lab==R)&effdn,COOL); nc=int(cond_mask.sum())
            if nb<40 or nc<30: cells.append(f"{R}:thin"); continue
            inc=Pm(ou,od,70,50,'L',H,cond_mask)[0]-Pm(ou,od,70,50,'L',H,base_mask)[0]
            cells.append(f"{R}:{inc:+.3f}(n{nc})")
        print(f"   {era}: "+"  ".join(cells))
    print("  dxyEffUp->S incremental within each XAUUSD parent state, per era:")
    for era in ERAS:
        m=P[era]; ou,od,xret4,d4,effdn,effup,lab=prepped[era]
        cells=[]
        for R in STATES:
            base_mask=(lab==R)&dedup(lab==R,COOL); nb=int(base_mask.sum())
            cond_mask=(lab==R)&effup&dedup((lab==R)&effup,COOL); nc=int(cond_mask.sum())
            if nb<40 or nc<30: cells.append(f"{R}:thin"); continue
            inc=Pm(ou,od,70,50,'S',H,cond_mask)[0]-Pm(ou,od,70,50,'S',H,base_mask)[0]
            cells.append(f"{R}:{inc:+.3f}(n{nc})")
        print(f"   {era}: "+"  ".join(cells))

if __name__=="__main__":
    main()
