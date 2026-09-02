"""sc_L1_exact.py — EXACT replication of frozen Statistician L1 (STAT_L1_LONDON_FROZEN_SPEC_V1, SPEC_HASH b2bc79c6..., DATASET cbb6eebe...).
L1 = every M5 bar with UTC hour in {8,9,10,11,12} (no DST); baseline = complement. Headline T1 = P(+100p before -80p) over t+1..t+288
from close[t], ties->adverse(0), unresolved->excluded. Day-clustered SE on the L1 group. Native governed M5. No optimization.
"""
import sys, os, math, hashlib, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC
PIP=0.10; H=288
M5PATH=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\data\market\OANDA_XAUUSD_M5.csv"
EXPECT_DATA="cbb6eebe1a189ebb20972318a8d98a36bfa461d2cd030bbaa7ba5430cc9f3814"

def hit_level(h,l,c,X,side,horizon=H):
    n=len(c); tgt=c+side*X*PIP; hit=np.full(n,np.inf)
    for j in range(1,horizon+1):
        if side>0: aj=np.concatenate([h[j:],np.full(j,np.nan)]); now=(aj>=tgt)&np.isinf(hit)
        else:      aj=np.concatenate([l[j:],np.full(j,np.nan)]); now=(aj<=tgt)&np.isinf(hit)
        hit=np.where(now,j,hit)
    return hit

def race(hu,hd):
    out=np.where(hu<hd,1.0,np.where(hd<=hu,0.0,np.nan)); out=np.where(np.isinf(hu)&np.isinf(hd),np.nan,out); return out

def cl(mask,y,day,sub):
    ok=mask&np.isfinite(y)&sub; bm=(~mask)&np.isfinite(y)&sub
    if ok.sum()<100 or bm.sum()<100: return None
    yy=y[ok]; dd=day[ok]; mu=yy.mean(); base=y[bm].mean()
    g=pd.DataFrame({"d":dd,"y":yy}).groupby("d")["y"].agg(["sum","count"]); G=len(g); N=len(yy)
    resid=g["sum"].to_numpy()-g["count"].to_numpy()*mu
    se=math.sqrt(max((resid**2).sum()/N**2*(G/max(G-1,1)),1e-18))
    return dict(N=int(N),days=int(G),val=float(mu),base=float(base),lift=float(mu-base),z=float((mu-base)/se if se>0 else 0))

def binom_z(y_sel, base_p):
    yy=y_sel[np.isfinite(y_sel)]; N=len(yy)
    if N<30: return None
    p=yy.mean(); se=math.sqrt(base_p*(1-base_p)/N); return dict(N=N,p=float(p),lift=float(p-base_p),z=float((p-base_p)/se if se>0 else 0))

def main():
    ds=hashlib.sha256(open(M5PATH,'rb').read()).hexdigest()
    print(f"DATASET sha256 = {ds}\n  == expected cbb6eebe...: {ds==EXPECT_DATA}")
    M=MC.load(); h=M["h"];l=M["l"];c=M["c"];n=M["n"]; t=M["t"]
    dt=pd.to_datetime(t,unit='s',utc=True); hr=dt.hour.to_numpy(); day=dt.floor("D").astype("int64").to_numpy(); yr=M["yr"]
    DEV=np.asarray(dt<=pd.Timestamp("2024-06-30",tz="UTC")); ALL=np.ones(n,bool)
    L1=(hr>=8)&(hr<=12)
    print("precomputing barrier hit levels ..."); ups={}; dns={}
    for X in (80,100,150,200,300): ups[X]=hit_level(h,l,c,X,+1)
    for X in (80,100,150,200): dns[X]=hit_level(h,l,c,X,-1)
    T1=race(ups[100],dns[80]); T2=race(ups[200],dns[100]); T3=race(ups[300],dns[150])
    print(f"\nL1 events={int(L1.sum())} ({100*L1.sum()/n:.1f}%)  resolved-T1={int((L1&np.isfinite(T1)).sum())}  baseline resolved-T1={int((~L1&np.isfinite(T1)).sum())}")
    # HEADLINE (full sample, day-clustered — matches Statistician 0.4663->0.4286 z-3.59)
    r=cl(L1,T1,day,ALL)
    print(f"\n== HEADLINE T1=P(+100 before -80) full-sample ==")
    print(f"BASELINE={r['base']:.4f}  L1={r['val']:.4f}  LIFT={r['lift']:+.4f}  Z={r['z']:+.2f}  (expect 0.4663->0.4286 z-3.59)")
    rd=cl(L1,T1,day,DEV); ro=cl(L1,T1,day,~DEV); print(f"  DEV lift={rd['lift']:+.4f} z={rd['z']:+.2f} | OOS lift={ro['lift']:+.4f} z={ro['z']:+.2f}")
    # §3 per-year for T1/T2/T3
    print("\n== §3 per-year lift (which target is 6/6) ==")
    for nm,T in (("T1(100/80)",T1),("T2(200/100)",T2),("T3(300/150)",T3)):
        sg=[]
        for y in sorted(set(yr.tolist())):
            rr=cl(L1,T,day,yr==y)
            if rr: sg.append(np.sign(rr['lift']))
        full=cl(L1,T,day,ALL)
        print(f"  {nm}: full lift={full['lift']:+.4f} z={full['z']:+.2f} · same-sign {sum(1 for s in sg if s==sg[0])}/{len(sg)}")
    # §5 mirrored races (L1 lift for each)
    print("\n== §5 mirrored races (L1 lift vs baseline; up-first prob) ==")
    pairs=[("+80 b -80",race(ups[80],dns[80])),("+100 b -100",race(ups[100],dns[100])),
           ("+100 b -80",T1),("+80 b -100",race(ups[80],dns[100])),
           ("+150 b -100",race(ups[150],dns[100])),("+100 b -150",race(ups[100],dns[150])),
           ("+200 b -100",T2),("+100 b -200",race(ups[100],dns[200]))]
    for nm,R in pairs:
        rr=cl(L1,R,day,ALL); print(f"  P({nm:12s}): base={rr['base']:.4f} L1={rr['val']:.4f} lift={rr['lift']:+.4f} z={rr['z']:+.2f}")
    # §6 hour-by-hour T1 lift (descriptive)
    print("\n== §6 hour-by-hour T1 lift (is 8-12 special or smooth?) ==")
    base_all=cl(L1,T1,day,ALL)['base']
    for H_ in range(24):
        rr=binom_z(T1[hr==H_], base_all)
        if rr: mark=" <-L1" if 8<=H_<=12 else ""; print(f"  {H_:02d}h: T1={rr['p']:.4f} lift={rr['lift']:+.4f} z={rr['z']:+.2f} N={rr['N']}{mark}")
    # §7 DEPENDENCE
    print("\n== §7 DEPENDENCE robustness (T1) ==")
    idx=np.where(L1&np.isfinite(T1))[0]
    seen=set(); perday=[i for i in idx if not (day[i] in seen or seen.add(day[i]))]
    keep=[]; last=-10**9
    for i in idx:
        if i-last>=H: keep.append(i); last=i
    print(f"  A day-clustered (headline): lift={base_all and r['lift']:+.4f} z={r['z']:+.2f} N={r['N']}")
    cz=binom_z(T1[np.array(perday)],base_all); print(f"  B one-per-day (first L1 bar): lift={cz['lift']:+.4f} z={cz['z']:+.2f} N={cz['N']}")
    ez=binom_z(T1[np.array(keep)],base_all); print(f"  C non-overlap >=288 apart   : lift={ez['lift']:+.4f} z={ez['z']:+.2f} N={ez['N']}")
    # §8 price-state control: within recent-return(12-bar) & vol strata
    print("\n== §8 price-state control: within recent-return strata (does UTC-window add beyond state?) ==")
    tr=np.maximum(h-l,np.maximum(np.abs(h-np.roll(c,1)),np.abs(l-np.roll(c,1)))); tr[0]=h[0]-l[0]
    atr=pd.Series(tr).rolling(14).mean().to_numpy(); sp=(c-pd.Series(c).shift(12).to_numpy())/atr
    qs=np.nanquantile(sp[np.isfinite(sp)],[0.2,0.4,0.6,0.8]); wb=lambda x: np.digitize(x,qs)
    wl=0.0; ws=0
    for b in range(5):
        rr=cl(L1,T1,day,wb(sp)==b)
        if rr: print(f"  ret-bucket {b}: L1 lift={rr['lift']:+.4f} z={rr['z']:+.2f} N={rr['N']}"); wl+=rr['lift']*rr['N']; ws+=rr['N']
    print(f"  N-weighted within-return lift = {wl/max(ws,1):+.4f} (vs unconditional {r['lift']:+.4f})")

if __name__=="__main__":
    main()
