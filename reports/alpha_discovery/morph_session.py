"""morph_session.py — CAUSAL MORPHOLOGY DISCOVERY Space D: SESSION geometry (distinct representation, §3).
Per-day, decided at NY open (first bar hr>=13), using ONLY completed Asia(0-7)+London(7-13)+prior-day geometry.
Features (causal, ATR-normalized): asia net/range/close-location, london net/range/close-location, london-vs-asia
persistence, prior-day net/close-location. Cluster (KMeans K=10) fit+frozen on DISC(b0+b1), assign all eras,
stability + forward path (P +70/-50 over next 48 M15=NY+overnight). No future info in discovery. On M15 frames.
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_m15_data as m15d
from state_path_m15 import passage_m15, Pm
from morph_discover import kmeans, assign, KCL
from batch_a import _hr_day
from batch_e import _first_ny
HB=48; K=10; SEED=7
FN=["asia_net","asia_rng","asia_cloc","lon_net","lon_rng","lon_cloc","lon_vs_asia","pday_net","pday_cloc"]

def sess_feats(fr):
    hr,day,_=_hr_day(fr); n=len(fr)
    o=fr["open"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); c=fr["close"].to_numpy()
    df=pd.DataFrame({"day":day,"o":o,"h":h,"l":l,"c":c})
    asia=(hr>=0)&(hr<7); lon=(hr>=7)&(hr<13)
    ag=df[asia].groupby("day").agg(ao=("o","first"),ah=("h","max"),al=("l","min"),ac=("c","last"))
    lg=df[lon].groupby("day").agg(lo=("o","first"),lh=("h","max"),ll=("l","min"),lc=("c","last"))
    dg=df.groupby("day").agg(do=("o","first"),dh=("h","max"),dl=("l","min"),dc=("c","last"))
    aR=(ag["ah"]-ag["al"]); lR=(lg["lh"]-lg["ll"]); scale=(dg["dh"]-dg["dl"]).rolling(20).mean()
    F=pd.DataFrame(index=dg.index)
    F["asia_net"]=(ag["ac"]-ag["ao"])/scale; F["asia_rng"]=aR/scale; F["asia_cloc"]=(ag["ac"]-ag["al"])/aR.replace(0,np.nan)
    F["lon_net"]=(lg["lc"]-lg["lo"])/scale; F["lon_rng"]=lR/scale; F["lon_cloc"]=(lg["lc"]-lg["ll"])/lR.replace(0,np.nan)
    F["lon_vs_asia"]=np.sign((lg["lc"]-lg["lo"]))*np.sign((ag["ac"]-ag["ao"]))
    F["pday_net"]=((dg["dc"]-dg["do"])/scale).shift(1); F["pday_cloc"]=(((dg["dc"]-dg["dl"])/(dg["dh"]-dg["dl"])).shift(1))
    # map per-day features to the NY-open decision bar
    fny=_first_ny(fr); didx=np.where(fny)[0]; dday=day[didx]
    Xall=F.reindex(dday).to_numpy()
    X=np.full((n,len(FN)),np.nan); X[didx]=Xall
    ok=np.zeros(n,bool); ok[didx]=np.isfinite(Xall).all(1)
    return X, ok, fny

def run(tag_frames):
    hm=m15d.build(verbose=False)["M15"]; sm=sb.build_frames()["M15"]
    Xh,okh,fh=sess_feats(hm); Xs,oks,fs=sess_feats(sm)
    b0=hm["is_b0"].to_numpy(); b1=hm["is_b1"].to_numpy(); dev=sm["is_dev"].to_numpy(); cal=sm["is_cal"].to_numpy()
    disc=(b0|b1)&okh; mu=Xh[disc].mean(0); sd=Xh[disc].std(0)+1e-9
    C=kmeans((Xh[disc]-mu)/sd, K)
    Lh=np.full(len(hm),-1); Lh[okh]=assign((Xh[okh]-mu)/sd,C)
    Ls=np.full(len(sm),-1); Ls[oks]=assign((Xs[oks]-mu)/sd,C)
    eras=[("b0",hm,b0&okh,Lh),("b1",hm,b1&okh,Lh),("DEV",sm,dev&oks,Ls),("CAL",sm,cal&oks,Ls)]
    PSG={"h":passage_m15(hm,Hmax=HB),"s":passage_m15(sm,Hmax=HB)}; PS={"b0":"h","b1":"h","DEV":"s","CAL":"s"}
    occ={tag:np.bincount(L[m],minlength=K)/max(m.sum(),1) for tag,fr,m,L in eras}
    print(f"\n===== MORPHOLOGY Space D (SESSION geometry, NY-open decision). K={K} fit DISC(b0+b1), frozen. HB={HB}. =====")
    print("-- archetype | top session-descriptors | occ b0/b1/DEV/CAL | asym70 b0/b1/DEV/CAL --")
    surv=0
    for k in range(K):
        order=np.argsort(-np.abs(C[k])); tops=", ".join(f"{FN[i]}{C[k][i]:+.1f}" for i in order[:3])
        occs="/".join(f"{occ[t][k]*100:.1f}" for t in ["b0","b1","DEV","CAL"])
        asyms=[]
        for tag,fr,m,L in eras:
            ou,od,mfe,mae=PSG[PS[tag]]; mask=m&(L==k); idx=np.where(mask)[0]; idx=idx[idx<len(fr)-1]
            if len(idx)<40: asyms.append("na"); continue
            mm=np.zeros(len(fr),bool); mm[idx]=True
            a=Pm(ou,od,70,50,'L',HB,mm)[0]-Pm(ou,od,70,50,'S',HB,mm)[0]; asyms.append(f"{a:+.2f}")
        nums=[float(a) for a in asyms if a!="na"]; rec=min(occ[t][k] for t in ["b0","b1","DEV","CAL"])>0.01
        stable=len(nums)>=3 and (all(x>=0.05 for x in nums) or all(x<=-0.05 for x in nums))
        flag=" <== RECURRENT+MATERIAL+STABLE" if (rec and stable) else ""
        if rec and stable: surv+=1
        print(f"  D{k:02d} [{tops}] | occ {occs} | asym70 {'/'.join(asyms)}{flag}")
    print(f"  -> {surv} recurrent+material+stable session archetypes")

if __name__=="__main__":
    run(None)
