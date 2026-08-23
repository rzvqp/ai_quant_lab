"""morph_space_htf.py — CAUSAL MORPHOLOGY DISCOVERY Spaces B & C: H1-scale and H4-scale short structure (§3 multiple
temporal scales). Same firewall-respecting pipeline as morph_discover (causal features, fit+freeze on DISC b0+b1,
assign all eras, stability-before-outcome, novelty, then forward path). Reuses the frozen helpers. No future info in
discovery. hist_data provides b0/b1 (2011-2018), swing_base provides DEV/CAL (2021-2024) for H1/H4.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
from state_path_m15 import passage_m15, Pm
from morph_features import feats, NAMES
from morph_discover import kmeans, assign, interp, KCL

def run(tf, HB, label):
    print(f"\n===== MORPHOLOGY {label} ({tf}-scale). K={KCL} on DISC(b0+b1), frozen, all eras. HB={HB}bars. Firewall: no future info. =====")
    hh=hd._load(tf); ss=sb.build_frames()[tf]
    Xh,okh=feats(hh); Xs,oks=feats(ss)
    b0=hh["is_b0"].to_numpy(); b1=hh["is_b1"].to_numpy(); dev=ss["is_dev"].to_numpy(); cal=ss["is_cal"].to_numpy()
    disc=(b0|b1)&okh; mu=Xh[disc].mean(0); sd=Xh[disc].std(0)+1e-9
    C=kmeans((Xh[disc]-mu)/sd, KCL)
    Lh=assign((Xh-mu)/sd,C); Ls=assign((Xs-mu)/sd,C)
    eras=[("b0",hh,b0&okh,Lh),("b1",hh,b1&okh,Lh),("DEV",ss,dev&oks,Ls),("CAL",ss,cal&oks,Ls)]
    PSG={"h":passage_m15(hh,Hmax=HB),"s":passage_m15(ss,Hmax=HB)}; PS={"b0":"h","b1":"h","DEV":"s","CAL":"s"}
    occ={tag:np.bincount(L[m],minlength=KCL)/max(m.sum(),1) for tag,fr,m,L in eras}
    print("-- archetype | interp | occ b0/b1/DEV/CAL | asym70 b0/b1/DEV/CAL --")
    surv=0
    for k in range(KCL):
        fam,tops=interp(C[k]); occs="/".join(f"{occ[t][k]*100:.1f}" for t in ["b0","b1","DEV","CAL"])
        asyms=[]
        for tag,fr,m,L in eras:
            ou,od,mfe,mae=PSG[PS[tag]]; mask=m&(L==k); idx=np.where(mask)[0]; idx=idx[idx<len(fr)-1]
            if len(idx)<40: asyms.append("na"); continue
            mm=np.zeros(len(fr),bool); mm[idx]=True
            a=Pm(ou,od,70,50,'L',HB,mm)[0]-Pm(ou,od,70,50,'S',HB,mm)[0]; asyms.append(f"{a:+.2f}")
        vals=[occ[t][k] for t in ["b0","b1","DEV","CAL"]]; rec=min(vals)>0.01
        nums=[float(a) for a in asyms if a!="na"]; stable=len(nums)>=3 and (all(x>=0.05 for x in nums) or all(x<=-0.05 for x in nums))
        flag=" <== RECURRENT+MATERIAL+STABLE" if (rec and stable) else ""
        if rec and stable: surv+=1
        print(f"  A{k:02d} {fam:16s} [{tops}] | occ {occs} | asym70 {'/'.join(asyms)}{flag}")
    print(f"  -> {surv} recurrent+material+stable archetypes")

if __name__=="__main__":
    run("H1",24,"Space B")   # H1, forward 24 bars = 1 day
    run("H4",12,"Space C")   # H4, forward 12 bars = 2 days
