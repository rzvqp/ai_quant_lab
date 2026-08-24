"""chrono_choch.py — test the DISTINCT decision rule the zone-reader never tried: COUNTER-BIAS on STRUCTURAL FAILURE.
Signal = a ratified MK-01 CHoCH (change-of-character) event; trade IN the CHoCH direction (CHOCH_BULL->LONG, CHOCH_BEAR->SHORT).
Compare subsets: ALL CHoCH; AGAINST-BIAS (CHOCH_BULL while N1 H4 regime is bearish, or CHOCH_BEAR while N1 bullish = structure failing
against the higher-TF bias); WITH-BIAS (aligned). Causal (breaks use confirmed swings<c). Entry=next-bar open, invalidation=prior-20
opposite extreme -/+0.2ATR, target=+2R, cooldown>=10. Full gate incl. STRESS cost 0.24 + per-era + tail + LOYO + 2x + delay + neighbor.
N1 live-memoized (no N3 needed). This tests whether a structural failure is a REVERSAL edge, especially against the prevailing bias."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
import regime_classifier as RC, market_structure as MS
from market_structure import Block
COST=0.24; HMAX=300
def axlabel(ax):
    v=getattr(ax,'value',None); return v.label if v is not None and hasattr(v,'label') else "na"
def build_blocks(t):
    g=np.where(np.diff(t)>72*3600)[0]; bs=[]; s=0
    for x in g: bs.append(Block(s,x+1)); s=x+1
    bs.append(Block(s,len(t))); return bs
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); n=len(m); tsec=m["time"].to_numpy(); yr=m["dt"].dt.year.to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    blocks=build_blocks(tsec)
    swings=MS.label_structure(MS.detect_swings(h,l,blocks)); breaks=MS.detect_breaks(c,swings,blocks); BK=MS.BreakKind
    def rs(period):
        b=(tsec//period)*period; df=pd.DataFrame({"b":b,"o":o,"h":h,"l":l,"c":c,"i":np.arange(n)}); g=df.groupby("b",sort=True)
        return (g["o"].first().to_numpy(),g["h"].max().to_numpy(),g["l"].min().to_numpy(),g["c"].last().to_numpy(),g["i"].last().to_numpy())
    O4,H4,L4,C4,CA4=rs(14400); h4_of=np.searchsorted(CA4,np.arange(n),side="right")-1; rc={}
    def N1(T):
        k=int(h4_of[T])
        if k<0: return "na"
        if k in rc: return rc[k]
        s=max(0,k-199); rg=RC.classify_regime(O4[s:k+1],H4[s:k+1],L4[s:k+1],C4[s:k+1]); rv=getattr(rg,'value',None)
        d=axlabel(rv.direction) if rv is not None else "na"; rc[k]=d; return d
    def sim(dirn,T,delay=1):
        ei=T+delay
        if ei>=n-HMAX or not np.isfinite(atr[T]) or atr[T]<=0: return None
        entry=o[ei]; inval=(p20L[T]-0.2*atr[T]) if dirn>0 else (p20H[T]+0.2*atr[T])
        if dirn>0 and inval>=entry: inval=entry-0.8*atr[T]
        if dirn<0 and inval<=entry: inval=entry+0.8*atr[T]
        risk=abs(entry-inval); tgt=entry+2*risk*dirn; seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
        if dirn>0: fs=np.where(seg_l<=inval)[0]; ft=np.where(seg_h>=tgt)[0]
        else: fs=np.where(seg_h>=inval)[0]; ft=np.where(seg_l<=tgt)[0]
        fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
        if fstop==ftgt==10**9: return None
        return 2.0 if ftgt<fstop else -1.0
    # build CHoCH signals
    bull=lambda d: d in ("up","weak_up"); bear=lambda d: d in ("down","weak_down")
    rows=[]; last=-10**9
    for b in sorted(breaks,key=lambda x:x.idx):
        if b.kind not in (BK.CHOCH_BULL,BK.CHOCH_BEAR): continue
        T=b.idx
        if T-last<10 or T<400 or T>=n-HMAX-2: continue
        dirn=1 if b.kind==BK.CHOCH_BULL else -1
        R=sim(dirn,T)
        if R is None: continue
        d=N1(T)
        against = (dirn>0 and bear(d)) or (dirn<0 and bull(d))
        withb = (dirn>0 and bull(d)) or (dirn<0 and bear(d))
        rows.append((T,yr[T],dirn,R,against,withb,d)); last=T
    if not rows: print("CHoCH: 0 signals"); return
    arr=np.array([r[3] for r in rows]); yrs=np.array([r[1] for r in rows]); ag=np.array([r[4] for r in rows]); wb=np.array([r[5] for r in rows])
    st=lambda a:(len(a),(np.mean(a>0) if len(a) else float('nan')),(np.mean(a-COST) if len(a) else float('nan')))
    def gate(a,ys,label):
        N,p2,net=st(a); print(f"\n{label}: n={N} P2R={p2:.3f} netR(STRESS {COST})={net:+.3f}")
        for lb,mk in [("DISC<=2018",ys<=2018),("CONF19-22",(ys>=2019)&(ys<=2022)),("OOS23+",ys>=2023)]:
            nn,pp,nnet=st(a[mk]); print(f"    {lb:10s} n={nn:4d} P2R={pp:.3f} netR={nnet:+.3f}")
        if len(a)>20:
            thr=np.quantile(a,0.9); print(f"    tail netR={np.mean(a[a<=thr]-COST):+.3f} | 2x-cost netR={np.mean(a-2*COST):+.3f}")
            yu=sorted(set(ys.tolist())); loyo=min((np.mean(a[ys!=y]-COST) for y in yu if (ys==y).sum()>=8),default=float('nan'))
            posy=sum(1 for y in yu if (ys==y).sum()>=15 and np.mean(a[ys==y]-COST)>0); toty=sum(1 for y in yu if (ys==y).sum()>=15)
            print(f"    per-year net>0 {posy}/{toty} | LOYO worst netR={loyo:+.3f}")
    print(f"CHRONO-CHoCH counter-bias test: total CHoCH signals={len(rows)}")
    gate(arr,yrs,"ALL CHoCH (trade the failure direction)")
    gate(arr[ag],yrs[ag],"AGAINST-BIAS CHoCH (structure fails vs H4 regime)")
    gate(arr[wb],yrs[wb],"WITH-BIAS CHoCH (aligned with H4 regime)")
    best_net=np.mean(arr[ag]-COST) if ag.sum()>20 else -1
    print(f"\nVERDICT: counter-bias-on-failure = {'WORTH_FORWARD_TEST' if best_net>0 else 'FAIL (no edge after costs)'}")
if __name__=="__main__": main()
