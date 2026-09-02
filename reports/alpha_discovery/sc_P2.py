"""sc_P2.py — INDEPENDENT ALPHA REPLICATION of Statistician Scout-V1 lead P2 (bottom-of-24h-range downside continuation). EXACT spec.
State = S_loc<0.1 where S_loc=(c-lo288)/(hi288-lo288), 288-bar causal 24h range. Target T3=P(+300p before -150p) over t+1..t+288 (ties->0).
speed=(c-c12)/ATR14 (fast-down = speed<-1.5). Reproduce headline, then GATE1 overlap (§3) + GATE2 trend/location confound (§5).
Native governed M5. Day-clustered z (Statistician cl). No optimization.
"""
import sys, os, math, hashlib, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC
PIP=0.10; H=288

def spec_hash():
    s="P2: S_loc=(c-lo288)/(hi288-lo288) 288-bar shift1; state=S_loc<0.1; T3=P(+300p before -150p) t+1..t+288 ties->0; speed=(c-c12)/atr14; DEV<=2024-06-30"
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def barriers(h,l,c,up_p,dn_p,horizon=H):
    n=len(c); U=c+up_p*PIP; D=c-dn_p*PIP; hu=np.full(n,np.inf); hd=np.full(n,np.inf)
    for j in range(1,horizon+1):
        hj=np.concatenate([h[j:],np.full(j,np.nan)]); lj=np.concatenate([l[j:],np.full(j,np.nan)])
        hu=np.where((hj>=U)&np.isinf(hu),j,hu); hd=np.where((lj<=D)&np.isinf(hd),j,hd)
    out=np.where(hu<hd,1.0,np.where(hd<=hu,0.0,np.nan)); out=np.where(np.isinf(hu)&np.isinf(hd),np.nan,out)
    return out

def cl(mask,y,day,sub):
    ok=mask&np.isfinite(y)&sub; bm=(~mask)&np.isfinite(y)&sub
    if ok.sum()<100 or bm.sum()<100: return None
    yy=y[ok]; dd=day[ok]; mu=yy.mean(); base=y[bm].mean()
    g=pd.DataFrame({"d":dd,"y":yy}).groupby("d")["y"].agg(["sum","count"]); G=len(g); N=len(yy)
    resid=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((resid**2).sum()/N**2*(G/max(G-1,1)),1e-18))
    return dict(N=int(N),days=int(G),val=float(mu),base=float(base),lift=float(mu-base),z=float((mu-base)/se if se>0 else 0))

def binom_z(sel_y, base_p):
    yy=sel_y[np.isfinite(sel_y)]; N=len(yy)
    if N<30: return None
    p=yy.mean(); se=math.sqrt(base_p*(1-base_p)/N)
    return dict(N=N,p=float(p),lift=float(p-base_p),z=float((p-base_p)/se if se>0 else 0))

def main():
    M=MC.load(); h=M["h"];l=M["l"];c=M["c"];n=M["n"]; t=M["t"]
    dt=pd.to_datetime(t,unit='s',utc=True); day=dt.floor("D").astype("int64").to_numpy(); yr=M["yr"]
    DEV=np.asarray(dt<=pd.Timestamp("2024-06-30",tz="UTC"))
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=pd.Series(tr).rolling(14).mean().to_numpy()
    hi288=pd.Series(h).rolling(288).max().shift(1).to_numpy(); lo288=pd.Series(l).rolling(288).min().shift(1).to_numpy()
    S_loc=(c-lo288)/np.maximum(hi288-lo288,1e-9); c12=pd.Series(c).shift(12).to_numpy(); S_speed=(c-c12)/atr
    state=S_loc<0.1
    print("computing T3 (+300/-150 race, 288 bars)..."); T3=barriers(h,l,c,300,150)
    print(f"P2_SPEC_HASH={spec_hash()}")
    # HEADLINE
    rD=cl(state,T3,day,DEV); rO=cl(state,T3,day,~DEV)
    print("\n== HEADLINE T3=P(+300 before -150) (lift<0 = downside continuation) ==")
    print(f"DEV: cond={rD['val']:.4f} base={rD['base']:.4f} lift={rD['lift']:+.4f} z={rD['z']:+.2f} N={rD['N']} days={rD['days']}")
    print(f"OOS: cond={rO['val']:.4f} base={rO['base']:.4f} lift={rO['lift']:+.4f} z={rO['z']:+.2f} N={rO['N']}")
    ri=cl(state&(S_speed<-1.5),T3,day,DEV); print(f"INTERACTION (loc<0.1 & speed<-1.5) DEV: lift={ri['lift']:+.4f} z={ri['z']:+.2f} N={ri['N']}")
    signs=[]
    for y in sorted(set(yr.tolist())):
        r=cl(state,T3,day,yr==y)
        if r: signs.append(np.sign(r['lift']))
    print(f"per-year same-sign: {sum(1 for s in signs if s==signs[0])}/{len(signs)}")
    base_dev=rD['base']
    # ===== GATE 1: OVERLAP (§3) =====
    print("\n== GATE 1: OVERLAP ROBUSTNESS (§3) ==")
    idx=np.where(state&np.isfinite(T3)&DEV)[0]
    # B/E: episode = maximal run of consecutive P2 bars (one visit to range-low); take first bar per episode
    ep=[]; prev=-10
    for i in idx:
        if i-prev>1: ep.append(i)
        prev=i
    ep=np.array(ep); ez=binom_z(T3[ep], base_dev)
    print(f"  A overlapping (day-clustered)      : lift={rD['lift']:+.4f} z={rD['z']:+.2f} N={rD['N']}")
    print(f"  B episode-first (per range-low visit): lift={ez['lift']:+.4f} z={ez['z']:+.2f} N_episodes={ez['N']}")
    # C one per day
    seen=set(); perday=[i for i in idx if not (day[i] in seen or seen.add(day[i]))]
    cz=binom_z(T3[np.array(perday)], base_dev); print(f"  C one-per-day                       : lift={cz['lift']:+.4f} z={cz['z']:+.2f} N={cz['N']}")
    # E non-overlapping >=288 bars apart (greedy)
    keep=[]; last=-10**9
    for i in idx:
        if i-last>=H: keep.append(i); last=i
    ez2=binom_z(T3[np.array(keep)], base_dev); print(f"  E non-overlap >=288 bars apart      : lift={ez2['lift']:+.4f} z={ez2['z']:+.2f} N={ez2['N']}")
    print("  [independence unit = one visit to the range-low; consecutive loc<0.1 bars share ~same 288-bar forward window]")
    # ===== GATE 2: TREND/LOCATION CONFOUND (§5) =====
    print("\n== GATE 2: TREND/LOCATION CONFOUND (§5) — within trailing-return(speed) strata, DEV ==")
    sp=S_speed.copy(); qs=np.nanquantile(sp[DEV&np.isfinite(sp)], [0.2,0.4,0.6,0.8])
    def spb(x): return np.digitize(x,qs)
    wl=0.0; wsum=0
    for b in range(5):
        sub=DEV&(spb(sp)==b); r=cl(state,T3,day,sub)
        if r: print(f"  speed-bucket {b}: lift={r['lift']:+.4f} z={r['z']:+.2f} N={r['N']}"); wl+=r['lift']*r['N']; wsum+=r['N']
    print(f"  N-weighted WITHIN-SPEED lift = {wl/max(wsum,1):+.4f}  (vs unconditional {rD['lift']:+.4f}); if ~0 => subsumed by recent-return")

if __name__=="__main__":
    main()
