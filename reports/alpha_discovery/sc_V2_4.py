"""sc_V2_4.py — INDEPENDENT ALPHA REPLICATION of Statistician frozen lead V2-4 (RANGE COILED). EXACT spec from scout_v2/v2_scan.py+targets.
V2-4 state = w48p<0.2 where w48=(rolling48 H-L)/ATR14, w48p=trailing-2000 pct rank shift(1). Target A1 = hours to first +-100p (H=288).
Reproduce information + resolve the SESSION CONFOUND (does coiled add info AFTER controlling for hour/session?). Direction test via B2.
Native governed M5, causal, day-clustered z (Statistician's cl). No optimization.
"""
import sys, os, math, hashlib, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC
PIP=0.10; H=288

def load():
    M=MC.load(); return M
def spec_hash():
    s="V2-4: w48=(roll48 H-L)/ATR14; w48p=roll2000 pct rank shift1; state=w48p<0.2; A1=hrs to first +-100p H=288; base=~state; DEV<=2024-06-30"
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def first_touch(h,l,c,up_p,dn_p,horizon=H):
    n=len(c); U=c+up_p*PIP; D=c-dn_p*PIP; hu=np.full(n,np.inf); hd=np.full(n,np.inf)
    for j in range(1,horizon+1):
        hj=np.concatenate([h[j:],np.full(j,np.nan)]); lj=np.concatenate([l[j:],np.full(j,np.nan)])
        hu=np.where((hj>=U)&np.isinf(hu),j,hu); hd=np.where((lj<=D)&np.isinf(hd),j,hd)
    return hu,hd

def cl(mask,y,day,sub):
    ok=mask&np.isfinite(y)&sub; bm=(~mask)&np.isfinite(y)&sub
    if ok.sum()<200 or bm.sum()<200: return None
    yy=y[ok]; dd=day[ok]; mu=yy.mean(); base=y[bm].mean()
    g=pd.DataFrame({"d":dd,"y":yy}).groupby("d")["y"].agg(["sum","count"]); G=len(g); N=len(yy)
    resid=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((resid**2).sum()/N**2*(G/max(G-1,1)),1e-18))
    return dict(N=int(N),days=int(G),val=float(mu),base=float(base),lift=float(mu-base),z=float((mu-base)/se if se>0 else 0))

def main():
    M=load(); h=M["h"];l=M["l"];c=M["c"];n=M["n"]; t=M["t"]
    dt=pd.to_datetime(t,unit='s',utc=True); day=dt.floor("D").astype("int64").to_numpy(); yr=M["yr"]; hr=M["hr"]
    DEV=np.asarray(dt<=pd.Timestamp("2024-06-30",tz="UTC"))
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=pd.Series(tr).rolling(14).mean().to_numpy()
    hi48=pd.Series(h).rolling(48).max().shift(1).to_numpy(); lo48=pd.Series(l).rolling(48).min().shift(1).to_numpy()
    w48=(hi48-lo48)/np.maximum(atr,1e-9); w48p=pd.Series(w48).rolling(2000).rank(pct=True).shift(1).to_numpy()
    state=w48p<0.2
    u100,d100=first_touch(h,l,c,100,100); A1=np.fmin(u100,d100); A1=np.where(np.isinf(A1),np.nan,A1)*5/60.0
    B2=np.where(u100<d100,1.0,np.where(d100<=u100,0.0,np.nan)); B2[np.isinf(u100)&np.isinf(d100)]=np.nan
    print(f"V2_4_SPEC_HASH={spec_hash()}  state events(all)={int(np.isfinite(A1)&state).sum() if False else int((state&np.isfinite(A1)).sum())}")
    # headline reproduction
    rD=cl(state,A1,day,DEV); rO=cl(state,A1,day,~DEV)
    print("\n== HEADLINE (time-to-+-100p hours; negative lift/z = coiled FASTER) ==")
    print(f"DEV: cond={rD['val']:.2f}h base={rD['base']:.2f}h lift={rD['lift']:+.2f}h z={rD['z']:+.2f} N={rD['N']} days={rD['days']}")
    print(f"OOS: cond={rO['val']:.2f}h base={rO['base']:.2f}h lift={rO['lift']:+.2f}h z={rO['z']:+.2f} N={rO['N']} days={rO['days']}")
    # 6/6 years
    print("\n== per-year lift (hours) ==")
    signs=[]
    for y in sorted(set(yr.tolist())):
        r=cl(state,A1,day,yr==y)
        if r: print(f"  {y}: lift={r['lift']:+.2f}h z={r['z']:+.2f} N={r['N']}"); signs.append(np.sign(r['lift']))
    print(f"  same-sign years: {sum(1 for s in signs if s==signs[0])}/{len(signs)}")
    # direction test
    bD=cl(state,B2,day,DEV)
    print(f"\n== DIRECTION test B2=P(+100 before -100): cond={bD['val']:.3f} base={bD['base']:.3f} lift={bD['lift']:+.3f} (~0 => TIMING not DIRECTION) ==")
    # SESSION CONFOUND: within-hour stratified lift
    print("\n== SESSION/HOUR CONFOUND (§4): within-hour coiled-vs-noncoiled lift, DEV ==")
    num=0.0; den=0; wsum=0.0; wl=0.0
    for H_ in range(24):
        sub=DEV&(hr==H_); r=cl(state,A1,day,sub)
        if r is None: continue
        wl+=r['lift']*r['N']; wsum+=r['N']
    print(f"  N-weighted WITHIN-HOUR lift = {wl/max(wsum,1):+.2f}h  (vs unconditional DEV lift {rD['lift']:+.2f}h)")
    # per broad session
    def sess(H_): return "AS" if H_<7 else ("LN" if H_<12 else ("NY" if H_<17 else "LT"))
    print("  by session:")
    for s in ("AS","LN","NY","LT"):
        mask=np.array([sess(x)==s for x in hr]); r=cl(state,A1,day,DEV&mask)
        if r: print(f"    {s}: lift={r['lift']:+.2f}h z={r['z']:+.2f} N={r['N']}")
    # non-overlap: one coiled event per day (first per day), re-test
    firstperday={}
    idx=np.where(state&np.isfinite(A1))[0]
    keep=[]; seen=set()
    for i in idx:
        d=day[i]
        if d not in seen: seen.add(d); keep.append(i)
    km=np.zeros(n,bool); km[keep]=True
    rNO=cl(km,A1,day,DEV)
    print(f"\n== NON-OVERLAP (1 coiled event/day) DEV: lift={rNO['lift']:+.2f}h z={rNO['z']:+.2f} N={rNO['N']} ==")

if __name__=="__main__":
    main()
