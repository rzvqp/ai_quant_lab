"""voltime_resolution.py — VOLTIME-3: does a whipsaw-filtering DIRECTION-RESOLUTION capture the (real) compression expansion?
Same compression-range setup as VOLTIME-2, but the break must be CONFIRMED by the mandate's resolution mechanisms:
 RAW         = close breaks range (VOLTIME-2 baseline, was exactly null)
 DISPLACEMENT= break bar body |close-open| >= 1.5*ATR (momentum-confirmed break)
 ACCEPTANCE  = two consecutive closes beyond the range (sustained break)
 RETEST      = break, then a pullback that holds the broken level, then continue (S5-like)
Direction supplied by the confirmed break. Entry next-bar open after confirmation; stop=opposite range extreme; target +RR*risk;
STRESS 0.24. If any resolution nets>0 after costs cross-era, the volatility-timing frontier yields a tradeable edge. D=12,M=24,RR=2."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; HMAX=200
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy()
    comp=(atr<atr_ma).astype(int); comp_dur=np.zeros(n,int)
    for i in range(1,n): comp_dur[i]=comp_dur[i-1]+1 if comp[i] else 0
    def build(res="RAW", D=12, M=24, RR=2.0, buf=0.1):
        sig=[]; T=250
        while T<n-HMAX-M-6:
            if comp_dur[T]<D or not np.isfinite(atr[T]) or atr[T]<=0: T+=1; continue
            W=min(comp_dur[T],40); rhi=np.max(h[T-W+1:T+1]); rlo=np.min(l[T-W+1:T+1])
            conf=None
            for j in range(T+1,min(T+1+M,n-6)):
                up=c[j]>rhi; dn=c[j]<rlo
                if not(up or dn): continue
                dirn=1 if up else -1
                if res=="RAW": conf=(j,dirn); break
                if res=="DISPLACEMENT":
                    if abs(c[j]-o[j])>=1.5*atr[j]: conf=(j,dirn); break
                    else: continue
                if res=="ACCEPTANCE":
                    if (dirn>0 and c[j+1]>rhi) or (dirn<0 and c[j+1]<rlo): conf=(j+1,dirn); break
                    else: continue
                if res=="RETEST":
                    # after break at j, look for a pullback to the level that holds then a close continuing
                    lvl=rhi if dirn>0 else rlo
                    for k in range(j+1,min(j+12,n-3)):
                        if dirn>0 and l[k]<=lvl and c[k]>lvl: conf=(k,dirn); break
                        if dirn<0 and h[k]>=lvl and c[k]<lvl: conf=(k,dirn); break
                    if conf: break
                    else: break
            if conf is None: T+=M; continue
            j,dirn=conf; ei=j+1
            if ei>=n-HMAX: break
            entry=o[ei]; stop=(rlo-buf*atr[T]) if dirn>0 else (rhi+buf*atr[T]); risk=abs(entry-stop)
            if risk<=0.05*atr[T]: T=j+5; continue
            tgt=entry+RR*risk*dirn; seg_l=l[ei:ei+HMAX]; seg_h=h[ei:ei+HMAX]
            if dirn>0: fs=np.where(seg_l<=stop)[0]; ft=np.where(seg_h>=tgt)[0]
            else: fs=np.where(seg_h>=stop)[0]; ft=np.where(seg_l<=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: T=j+5; continue
            sig.append((yr[T],(RR if ftgt<fstop else -1.0))); T=j+5
        return sig
    st=lambda a:(len(a),(np.mean([x>0 for x in a]) if len(a) else float('nan')),(np.mean(a) if len(a) else float('nan')),(np.mean([x-COST for x in a]) if len(a) else float('nan')))
    for res in ["RAW","DISPLACEMENT","ACCEPTANCE","RETEST"]:
        s=build(res=res);
        if not s: print(f"{res}: 0 signals"); continue
        arr=np.array([x[1] for x in s]); yrs=np.array([x[0] for x in s])
        N,wr,g,net=st(arr)
        e=lambda mk: st(arr[mk])
        dD=e(yrs<=2018); dC=e((yrs>=2019)&(yrs<=2022)); dO=e(yrs>=2023)
        thr=np.quantile(arr,0.9) if len(arr)>20 else 0; tail=np.mean(arr[arr<=thr]-COST) if len(arr)>20 else float('nan')
        print(f"{res:12s}: n={N:5d} WR={wr:.3f} grossR={g:+.3f} netR={net:+.3f} | D={dD[3]:+.3f} C={dC[3]:+.3f} O={dO[3]:+.3f} | tail={tail:+.3f}")
    print("\n=> any resolution net>0 cross-era (D/C/O all >0) + tail>0 => tradeable volatility-timing edge -> preregister+full gate.")
if __name__=="__main__": main()
