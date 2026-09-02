"""sess_scan.py — SESSION_SPECIALIST_FACTORY_V1 first-pass scan of 6 mechanism families (causal, next-open entry, 2R, conservative).
Families: A Asia->London expansion; B Asia false-break->London reversal; C London overextension->NY reversal;
D London trend->NY continuation; E NY displacement->second leg; F late-NY continuation/exhaustion. Bull & short separate. S5 excluded.
"""
import sys, numpy as np
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import sess_core as SC
from tsm_core import independent_episodes

def per_date_idx(D):
    from collections import defaultdict
    lon=defaultdict(list); ny=defaultdict(list)
    dates=D["dates"]
    for i in range(D["n"]):
        if D["london"][i]: lon[dates[i]].append(i)
        if D["ny"][i]: ny[dates[i]].append(i)
    return lon,ny

def trades_A(D,lon):
    o=D["o"];h=D["h"];l=D["l"];c=D["c"];S=D["S"]; out=[]
    for d,idxs in lon.items():
        r=S.get(d,{});
        if "AH" not in r or not idxs: continue
        AH,AL=r["AH"],r["AL"]
        for j,i in enumerate(idxs[:-1]):
            if c[i]>AH: out.append((i+1,+1,AL)); break
            if c[i]<AL: out.append((i+1,-1,AH)); break
    return out

def trades_B(D,lon):
    o=D["o"];h=D["h"];l=D["l"];c=D["c"];S=D["S"]; out=[]
    for d,idxs in lon.items():
        r=S.get(d,{})
        if "AH" not in r or not idxs: continue
        AH,AL=r["AH"],r["AL"]
        for i in idxs[:-1]:
            if h[i]>AH and c[i]<AH: out.append((i+1,-1,h[i])); break     # false break up -> short
            if l[i]<AL and c[i]>AL: out.append((i+1,+1,l[i])); break     # false break down -> long
    return out

def trades_C(D,ny):
    o=D["o"];atr=D["atr"];S=D["S"]; out=[]
    for d,idxs in ny.items():
        r=S.get(d,{})
        if "LH" not in r or not idxs: continue
        ns=idxs[0]; a=atr[ns]; LR=r["LH"]-r["LL"]; ldir=np.sign(r["LC"]-r["LO"])
        near_ext = (r["LC"]>=r["LH"]-0.25*LR) if ldir>0 else (r["LC"]<=r["LL"]+0.25*LR)
        if LR>1.5*a and near_ext:
            if ldir>0: out.append((ns,-1,r["LH"]))       # London up-strong -> fade short at NY
            elif ldir<0: out.append((ns,+1,r["LL"]))
    return out

def trades_D(D,ny):
    o=D["o"];atr=D["atr"];S=D["S"]; out=[]
    for d,idxs in ny.items():
        r=S.get(d,{})
        if "LH" not in r or not idxs: continue
        ns=idxs[0]; a=atr[ns]; move=r["LC"]-r["LO"]
        if move>1.0*a: out.append((ns,+1,r["LL"]))       # London trend up -> NY continuation long
        elif move<-1.0*a: out.append((ns,-1,r["LH"]))
    return out

def trades_E(D,ny):
    o=D["o"];h=D["h"];l=D["l"];c=D["c"];atr=D["atr"]; out=[]
    for d,idxs in ny.items():
        if len(idxs)<8: continue
        ns=idxs[0]; a=atr[ns]; NO=o[ns]
        k4=idxs[3]; disp=c[k4]-NO; ddir=np.sign(disp)
        if abs(disp)<1.0*a: continue                      # need initial displacement
        # after bar k4, wait for pullback (retrace >=40% of disp) then re-acceptance close in ddir
        hi=max(h[ns:k4+1]); lo=min(l[ns:k4+1]); pulled=False
        for i in idxs[4:-1]:
            if not pulled:
                if ddir>0 and l[i]<=c[k4]-0.4*disp: pulled=True; pv=l[i]
                if ddir<0 and h[i]>=c[k4]-0.4*disp: pulled=True; pv=h[i]
            else:
                if ddir>0 and c[i]>o[i] and c[i]>c[k4]-0.2*disp: out.append((i+1,+1,pv)); break
                if ddir<0 and c[i]<o[i] and c[i]<c[k4]-0.2*disp: out.append((i+1,-1,pv)); break
    return out

def trades_F(D,ny,mode="cont"):
    o=D["o"];c=D["c"];atr=D["atr"];S=D["S"]; out=[]
    for d,idxs in ny.items():
        r=S.get(d,{})
        if "NO" not in r or len(idxs)<10: continue
        # late-NY decision bar = idxs[len-4] (~last hour); day move from Asia open (or NO) to decision
        db=idxs[-4]; a=atr[db]; base=r.get("AO",r["NO"]); mv=c[db]-base; d_dir=np.sign(mv)
        if abs(mv)<2.0*a: continue
        if mode=="cont":
            side=int(d_dir); stop=c[db]-side*1.5*a
        else:  # fade/exhaustion
            side=-int(d_dir); stop=c[db]+int(d_dir)*1.5*a
        out.append((db+1,side,stop))
    return out

def summ(D,trades,label):
    rows=[]
    for eb,side,stop in trades:
        r=SC.resolve_entry(D,eb,side,stop,2.0)
        if r: r["y"]=D["yr"][eb]; r["side"]=side; rows.append(r)
    if len(rows)<30: print(f"{label:34s} N={len(rows)} small"); return None
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); y=np.array([r["y"] for r in rows])
    era=np.array([SC.era_of(v) for v in y]); k=np.array([r["k"] for r in rows])
    def me(x): return net[era==x].mean() if (era==x).sum()>0 else float('nan')
    ie=len(independent_episodes(k,H=48))
    print(f"{label:34s} N={len(net):5d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} D={me('D'):+.3f} C={me('C'):+.3f} O={me('O'):+.3f}")
    return dict(rows=rows,net=net.mean())

def main():
    D=SC.build(); lon,ny=per_date_idx(D)
    print(f"session-days: london={len(lon)} ny={len(ny)}")
    summ(D,trades_A(D,lon),"A.Asia->London expansion")
    summ(D,trades_B(D,lon),"B.Asia false-break->London rev")
    summ(D,trades_C(D,ny),"C.London overext->NY reversal")
    summ(D,trades_D(D,ny),"D.London trend->NY continuation")
    summ(D,trades_E(D,ny),"E.NY displacement->second leg")
    summ(D,trades_F(D,ny,"cont"),"F.late-NY continuation")
    summ(D,trades_F(D,ny,"fade"),"F.late-NY exhaustion/fade")

if __name__=="__main__":
    main()
