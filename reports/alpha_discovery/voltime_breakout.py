"""voltime_breakout.py — VOLTIME-2: tradeable compression-BREAKOUT (direction supplied by the break) — the decisive path/cost test
of the VOLTIME-1 non-directional signal. Deterministic causal rule: when compression is mature (comp_dur=consecutive ATR<ATR_ma >= D)
define the compression range [min low, max high] over the last min(comp_dur,40) bars; scan forward up to M bars for the FIRST CLOSE
break (close>range_hi -> LONG, close<range_lo -> SHORT); enter next-bar open; stop=opposite range extreme -/+0.1ATR; target=+RR*risk.
Direction is NOT predicted — the break supplies it. STRESS cost 0.24. Reports overall/per-era/per-session net + tail/LOYO/2x/neighbor.
Tests the generalized-S5 hypothesis: does breakout-capture of the (real, cross-era-stable) expansion beat costs+whipsaw?"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; HMAX=200
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    comp=(atr<atr_ma).astype(int); comp_dur=np.zeros(n,int)
    for i in range(1,n): comp_dur[i]=comp_dur[i-1]+1 if comp[i] else 0
    def sess(i):
        H=hr[i]; return "AS" if H<8 else ("LN" if H<13 else ("NY" if H<20 else "AS"))
    def build(D=12, M=24, RR=2.0, buf=0.1, delay=1):
        sig=[]; T=250
        while T<n-HMAX-M-2:
            if comp_dur[T]<D or not np.isfinite(atr[T]) or atr[T]<=0: T+=1; continue
            W=min(comp_dur[T],40); rhi=np.max(h[T-W+1:T+1]); rlo=np.min(l[T-W+1:T+1])
            brk=None
            for j in range(T+1,min(T+1+M,n-2)):
                if c[j]>rhi: brk=(j,1); break
                if c[j]<rlo: brk=(j,-1); break
            if brk is None: T+=M; continue
            j,dirn=brk; ei=j+delay
            if ei>=n-HMAX: break
            entry=o[ei]
            stop=(rlo-buf*atr[T]) if dirn>0 else (rhi+buf*atr[T])
            risk=abs(entry-stop)
            if risk<=0.05*atr[T]: T=j+5; continue
            tgt=entry+RR*risk*dirn
            seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
            if dirn>0: fs=np.where(seg_l<=stop)[0]; ft=np.where(seg_h>=tgt)[0]
            else: fs=np.where(seg_h>=stop)[0]; ft=np.where(seg_l<=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: T=j+5; continue
            R=RR if ftgt<fstop else -1.0
            sig.append((T,yr[T],dirn,R,sess(T))); T=j+5
        return sig
    sig=build()
    if not sig: print("VOLTIME-2: 0 signals"); return
    arr=np.array([s[3] for s in sig]); yrs=np.array([s[1] for s in sig]); ss=np.array([s[4] for s in sig])
    st=lambda a:(len(a),(np.mean(a>0) if len(a) else float('nan')),(np.mean(a) if len(a) else float('nan')),(np.mean(a-COST) if len(a) else float('nan')))
    N,wr,g,net=st(arr)
    print(f"VOLTIME-2 compression-breakout (D=12,M=24,RR=2,STRESS {COST}): signals={N} winrate={wr:.3f} grossR={g:+.3f} netR={net:+.3f}")
    print("GATE:")
    for lab,mk in [("DISC<=2018",yrs<=2018),("CONF19-22",(yrs>=2019)&(yrs<=2022)),("OOS23+",yrs>=2023)]:
        nn,ww,gg,nn2=st(arr[mk]); print(f"  {lab:10s} n={nn:4d} WR={ww:.3f} grossR={gg:+.3f} netR={nn2:+.3f}")
    for s in ["AS","LN","NY"]:
        nn,ww,gg,nn2=st(arr[ss==s]); print(f"  session {s} n={nn:4d} WR={ww:.3f} netR={nn2:+.3f}")
    thr=np.quantile(arr,0.9); print(f"  tail(best-decile-removed) netR={np.mean(arr[arr<=thr]-COST):+.3f} | 2x-cost netR={np.mean(arr-2*COST):+.3f}")
    yu=sorted(set(yrs.tolist())); posy=sum(1 for y in yu if (yrs==y).sum()>=15 and np.mean(arr[yrs==y]-COST)>0); toty=sum(1 for y in yu if (yrs==y).sum()>=15)
    loyo=min((np.mean(arr[yrs!=y]-COST) for y in yu if (yrs==y).sum()>=8),default=float('nan'))
    print(f"  per-year net>0 {posy}/{toty} | LOYO worst netR={loyo:+.3f}")
    # neighbors
    print("NEIGHBORS:")
    for D,M,RR in [(8,24,2.0),(20,24,2.0),(12,16,2.0),(12,36,2.0),(12,24,1.5),(12,24,3.0)]:
        s2=build(D=D,M=M,RR=RR); a2=np.array([x[3] for x in s2])
        print(f"  D={D} M={M} RR={RR}: n={len(a2)} netR={(np.mean(a2-COST) if len(a2) else float('nan')):+.3f}")
    verdict="SURVIVES" if (net>0 and st(arr[yrs>=2023])[3]>0 and np.mean(arr[arr<=thr]-COST)>0 and loyo>0) else "FAIL (whipsaw/cost)"
    print(f"\nVERDICT: compression-breakout = {verdict}")
if __name__=="__main__": main()
