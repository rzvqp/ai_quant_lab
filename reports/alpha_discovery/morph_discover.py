"""morph_discover.py — CAUSAL MORPHOLOGY DISCOVERY (Space A: intraday M15 short structure).
Pipeline (firewall-respecting): (1) causal features (morph_features, NO future info); (2) fit z-norm + KMeans on the
DISC era only (b0+b1 2011-2018); (3) FREEZE centroids+norm; (4) assign ALL eras to frozen archetypes; (5) Phase-6
stability (occupancy per era) BEFORE outcomes; (6) interpret each archetype centroid (novelty gate §7); (7) ONLY THEN
forward path P(+70/-50) L/S asym per era (cross-era §11). Reproducible numpy KMeans (seed 7). No P&L in discovery.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from morph_features import feats, NAMES
KCL=12; HB=48; SEED=7

def kmeans(Z,K,iters=60,seed=SEED):
    rng=np.random.default_rng(seed); C=Z[rng.choice(len(Z),K,replace=False)].copy()
    for _ in range(iters):
        D=np.empty((len(Z),K))
        for k in range(K): D[:,k]=((Z-C[k])**2).sum(1)
        lab=D.argmin(1)
        newC=np.array([Z[lab==k].mean(0) if (lab==k).any() else C[k] for k in range(K)])
        if np.allclose(newC,C,atol=1e-6): break
        C=newC
    return C

def assign(Z,C):
    D=np.empty((len(Z),len(C)))
    for k in range(len(C)): D[:,k]=((Z-C[k])**2).sum(1)
    return D.argmin(1)

def interp(cvec):  # centroid in z-space -> top descriptors -> heuristic family label
    order=np.argsort(-np.abs(cvec)); top=[(NAMES[i],cvec[i]) for i in order[:3]]
    d=dict(zip(NAMES,cvec))
    if d["effic"]>0.8: fam="TREND_UP(persist)"
    elif d["effic"]<-0.8: fam="TREND_DN(persist)"
    elif d["vol_state"]<-0.6 and d["rng_trend"]<0: fam="COMPRESSION"
    elif d["rng_trend"]>0.8 and d["disp"]>0.5: fam="EXPANSION_UP"
    elif d["rng_trend"]>0.8 and d["disp"]<-0.5: fam="EXPANSION_DN"
    elif d["alternation"]>0.6: fam="CHOP/ROTATION"
    elif d["retr"]>0.8: fam="DEEP_RETRACE"
    elif abs(d["effic"])<0.3 and abs(d["disp"])<0.3: fam="NEUTRAL/RANGE"
    else: fam="MIXED"
    return fam, ", ".join(f"{n}{v:+.1f}" for n,v in top)

def main():
    print(f"MORPHOLOGY DISCOVERY Space A (M15 short structure). K={KCL} archetypes fit on DISC(b0+b1), frozen, assigned all eras. Firewall: NO future info in discovery.")
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    Xh,okh=feats(hm); Xs,oks=feats(sm)
    b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy(); dev=sm["is_dev"].to_numpy(); cal=sm["is_cal"].to_numpy()
    disc=(b0|b1)&okh
    mu=Xh[disc].mean(0); sd=Xh[disc].std(0)+1e-9
    C=kmeans((Xh[disc]-mu)/sd, KCL)   # FROZEN centroids
    print(f"DISC fit n={int(disc.sum())} centroids frozen (z-space).")
    # assign each era
    Lh=assign((Xh-mu)/sd, C); Ls=assign((Xs-mu)/sd, C)
    eras=[("b0",hm,b0&okh,Lh),("b1",hm,b1&okh,Lh),("DEV",sm,dev&oks,Ls),("CAL",sm,cal&oks,Ls)]
    PSG={"h":passage_m15(hm,Hmax=HB),"s":passage_m15(sm,Hmax=HB)}
    PS={"b0":"h","b1":"h","DEV":"s","CAL":"s"}
    # Phase 6: occupancy per era (stability, BEFORE outcomes)
    occ={tag:np.bincount(L[m],minlength=KCL)/max(m.sum(),1) for tag,fr,m,L in eras}
    print("\n-- archetype | interp | occupancy b0/b1/DEV/CAL | asym70 b0/b1/DEV/CAL --")
    for k in range(KCL):
        fam,tops=interp(C[k])
        occs="/".join(f"{occ[t][k]*100:.1f}" for t in ["b0","b1","DEV","CAL"])
        asyms=[]
        for tag,fr,m,L in eras:
            ou,od,mfe,mae=PSG[PS[tag]]; mask=m&(L==k); idx=np.where(mask)[0]; idx=idx[idx<len(fr)-1]
            if len(idx)<40: asyms.append("na"); continue
            mm=np.zeros(len(fr),bool); mm[idx]=True
            a=Pm(ou,od,70,50,'L',HB,mm)[0]-Pm(ou,od,70,50,'S',HB,mm)[0]; asyms.append(f"{a:+.2f}")
        # stability + material+stable flag
        vals=[occ[t][k] for t in ["b0","b1","DEV","CAL"]]; recurrent = min(vals)>0.01
        na=[a for a in asyms if a!="na"]; nums=[float(a) for a in na]
        stable = len(nums)>=3 and (all(x>=0.05 for x in nums) or all(x<=-0.05 for x in nums))
        flag=" <== RECURRENT+MATERIAL+STABLE" if (recurrent and stable) else (" [recurrent]" if recurrent else "")
        print(f"  A{k:02d} {fam:16s} [{tops}] | occ {occs} | asym70 {'/'.join(asyms)}{flag}")

if __name__=="__main__":
    main()
