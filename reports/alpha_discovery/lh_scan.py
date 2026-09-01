"""lh_scan.py — LONG_HORIZON_EVENT_REVEALED_DIRECTION_V1. Native M15 (2011-2026). Horizon 24h=96 bars. Direction EVENT-REVEALED.
5 families (event->response->future path), matched displacement-ALONE control, independent episodes (>=96-bar spacing), pre/post-2021,
positive control, outliers. Directional race P(+R in revealed dir before -R) + signed excursion. cur_data M15. No optimization.
"""
import sys, math, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import cur_data as CD
PIP=0.10; H=96; W=16; A=4; Dth=1.0

def load():
    m=CD.load_m15().reset_index(drop=True)
    return dict(o=m["open"].to_numpy(float),h=m["high"].to_numpy(float),l=m["low"].to_numpy(float),
                c=m["close"].to_numpy(float),atr=m["atr"].to_numpy(float),yr=m["dt"].dt.year.to_numpy(),
                day=m["dt"].dt.floor("D").astype("int64").to_numpy(),n=len(m))

def hit_level(h,l,c,X,side,horizon=H):
    n=len(c); tgt=c+side*X*PIP; hit=np.full(n,np.inf)
    for j in range(1,horizon+1):
        aj=(np.concatenate([h[j:],np.full(j,np.nan)]) if side>0 else np.concatenate([l[j:],np.full(j,np.nan)]))
        now=((aj>=tgt) if side>0 else (aj<=tgt))&np.isinf(hit); hit=np.where(now,j,hit)
    return hit

def indep(entries, gap=H):
    e=np.sort(np.asarray(entries)); keep=[]; last=-10**9
    for x in e:
        if x-last>=gap: keep.append(x); last=x
    return np.array(keep,dtype=int)

def main():
    M=load(); o=M["o"];h=M["h"];l=M["l"];c=M["c"];atr=M["atr"];n=M["n"];yr=M["yr"]
    print(f"M15 rows={n} 2011-2026; horizon 24h=96 bars")
    print("precomputing forward directional hit arrays (100/200/300/500p)...")
    HU={R:hit_level(h,l,c,R,+1) for R in (100,200,300,500)}
    HD={R:hit_level(h,l,c,R,-1) for R in (100,200,300,500)}
    fwd=np.concatenate([c[H:],np.full(H,np.nan)])-c        # signed 24h forward return (price)

    def metrics(ev):  # ev = list of (entry, dir); returns dict on INDEPENDENT episodes
        if len(ev)<40: return None
        E=np.array([e for e,d in ev]); Dr=np.array([d for e,d in ev])
        keep=indep(E); mask=np.isin(E,keep); E=E[mask]; Dr=Dr[mask]
        # directional race P(+100 in dir before -100 in dir) among resolved
        cont=[]; sret=[]; mfe=[]; mae=[]; p1=[];p2=[];p3=[];p5=[]
        for e,d in zip(E,Dr):
            hu=HU[100][e]; hd=HD[100][e]
            up_first = (hu<hd); dn_first=(hd<=hu)
            if np.isinf(hu) and np.isinf(hd): pass
            cont.append(1.0 if (up_first if d>0 else dn_first) else (0.0 if (not np.isinf(hu) or not np.isinf(hd)) else np.nan))
            sret.append(d*fwd[e])
            # MFE/MAE in dir
            fav = HU[100][e] if d>0 else HD[100][e]
            for R,arr in ((100,p1),(200,p2),(300,p3),(500,p5)):
                reached = (HU[R][e] if d>0 else HD[R][e]); arr.append(0.0 if np.isinf(reached) else 1.0)
        cont=np.array(cont,float); sret=np.array(sret,float)
        yE=yr[E]; dev=yE<=2019; pre=yE<2021
        def mn(a,msk): a=np.asarray(a); return float(np.nanmean(a[msk])) if msk.sum()>0 else float('nan')
        return dict(N=len(E), cont=float(np.nanmean(cont)), sret_pip=float(np.nanmean(sret)/PIP),
                    dev=mn(cont,dev), oos=mn(cont,~dev), pre=mn(cont,pre), post=mn(cont,~pre),
                    p100=float(np.mean(p1)),p200=float(np.mean(p2)),p300=float(np.mean(p3)),p500=float(np.mean(p5)),
                    sret_top1=float(np.sort(sret)[-max(1,len(sret)//100):].sum()/np.nansum(sret)) if np.nansum(sret)>0 else float('nan'),
                    sret_drop5=float(np.sort(sret)[:int(len(sret)*0.95)].mean()/PIP))

    # ---- events ----
    def disp_events():  # initial displacement (control): (bar i, dir) where |net over W| >= Dth*ATR
        ev=[]
        for i in range(W+2, n-H-A-2):
            if not (np.isfinite(atr[i]) and atr[i]>0): continue
            net=c[i]-c[i-W]
            if abs(net)>=Dth*atr[i]: ev.append((i, int(np.sign(net))))
        return ev
    DISP=disp_events()
    def famA():  # displacement -> acceptance (A closes beyond c[i] in dir) -> entry i+A
        ev=[]
        for i,d in DISP:
            if all((c[i+a]-c[i])*d>0 for a in range(1,A+1)): ev.append((i+A, d))
        return ev
    def famB():  # displacement -> failure (close back through origin c[i-W] within 8) -> reversal
        ev=[]
        for i,d in DISP:
            for j in range(i+1,min(i+9,n-H)):
                if (c[j]-c[i-W])*d<0: ev.append((j, -d)); break
        return ev
    def famC():  # displacement -> shallow retrace(<50%) -> renewed close beyond c[i] in dir
        ev=[]
        for i,d in DISP:
            ext=c[i]; pulled=False
            for j in range(i+1,min(i+16,n-H)):
                if not pulled and (c[j]-c[i])*d < -0.5*abs(c[i]-c[i-W]): pulled=True
                elif pulled and (c[j]-c[i])*d>0: ev.append((j,d)); break
        return ev
    def famE():  # range escape (close beyond 32-bar extreme) -> persist P=4 outside -> continuation
        hi32=pd.Series(h).rolling(32).max().shift(1).to_numpy(); lo32=pd.Series(l).rolling(32).min().shift(1).to_numpy()
        ev=[]
        for i in range(34,n-H-6):
            if not(np.isfinite(atr[i])and atr[i]>0): continue
            d=0
            if c[i]>hi32[i]: d=1
            elif c[i]<lo32[i]: d=-1
            if d==0: continue
            if all((c[i+p]-(hi32[i] if d>0 else lo32[i]))*d>0 for p in range(1,4)): ev.append((i+3,d))
        return ev

    print("\n== POSITIVE CONTROL — engine must recover a known directional effect ==")
    # (1) mechanical: revealed dir = race winner (+/-100 first) -> P(continue) must be ~1.0 by construction
    pcw=[(i, (1 if HU[100][i]<HD[100][i] else -1)) for i in range(W+2,n-H,20)
         if not (np.isinf(HU[100][i]) and np.isinf(HD[100][i]))]
    rw=metrics(pcw)
    # (2) leaky net-return dir -> should lift P(continue) far above the ~0.5 baseline
    pc=[(i, int(np.sign(fwd[i]))) for i in range(W+2,n-H,20) if np.isfinite(fwd[i]) and fwd[i]!=0]
    rn=metrics(pc)
    PASS = rw['cont']>0.97 and rn['cont']>0.75
    print(f"  (1) race-winner dir  P(continue)={rw['cont']:.3f} (expect ~1.0)  N={rw['N']}")
    print(f"  (2) net-return dir   P(continue)={rn['cont']:.3f} vs ~0.50 baseline (expect >>0.5)  N={rn['N']}")
    print(f"  POSITIVE_CONTROL = {'PASS' if PASS else 'FAIL'}  (engine recovers known directional effects)")

    print("\n== FAMILIES: P(continue@100) on INDEPENDENT episodes; control = displacement-ALONE ==")
    ctrl=metrics([(i,d) for i,d in DISP])
    print(f"  CONTROL disp-alone     : cont={ctrl['cont']:.3f} sret={ctrl['sret_pip']:+.0f}p pre={ctrl['pre']:.3f} post={ctrl['post']:.3f} N={ctrl['N']}")
    for nm,fn in (("A disp->accept->cont",famA),("B disp->fail->reversal",famB),("C disp->shallow->renew",famC),("E range-escape->persist",famE)):
        r=metrics(fn())
        if r is None: print(f"  {nm}: too few"); continue
        print(f"  {nm:24s}: cont={r['cont']:.3f} (vs ctrl {ctrl['cont']:.3f}, +{r['cont']-ctrl['cont']:+.3f}) sret={r['sret_pip']:+.0f}p "
              f"DEV={r['dev']:.3f} OOS={r['oos']:.3f} PRE={r['pre']:.3f} POST={r['post']:.3f} "
              f"P200={r['p200']:.2f} P300={r['p300']:.2f} drop5%sret={r['sret_drop5']:+.0f}p top1%={r['sret_top1']:.2f} N={r['N']}")

if __name__=="__main__":
    main()
