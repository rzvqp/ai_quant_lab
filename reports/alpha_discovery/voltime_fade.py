"""voltime_fade.py — VOLTIME-5: PATH-ASYMMETRY / first-move-FADE after compression. Since compression BREAKOUTS whipsaw to exactly
null (V2/V3/V4), test the mirror mechanism: is the first break a LIQUIDITY GRAB that REVERSES? INFO: of first breaks from a mature
compression range, what fraction return to the range midpoint (fade) BEFORE extending +1R further (continuation)? TRADEABLE: fade the
break — on close>range_hi go SHORT (mirror LONG), stop=break-bar extreme +/-0.3ATR, target=range midpoint (and opposite-extreme
variant). Direction supplied by the fade of the sweep (non-directional frontier). STRESS 0.24, cross-era gate. If breaks reverse with
tradeable asymmetry cross-era -> candidate; else the frontier's fade side is also null. D=12."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; HMAX=96
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy()
    comp=(atr<atr_ma).astype(int); comp_dur=np.zeros(n,int)
    for i in range(1,n): comp_dur[i]=comp_dur[i-1]+1 if comp[i] else 0
    # gather first-break events from mature compression
    events=[]; T=250
    while T<n-HMAX-30:
        if comp_dur[T]<12 or not np.isfinite(atr[T]) or atr[T]<=0: T+=1; continue
        W=min(comp_dur[T],40); rhi=np.max(h[T-W+1:T+1]); rlo=np.min(l[T-W+1:T+1]); mid=0.5*(rhi+rlo); a=atr[T]
        brk=None
        for j in range(T+1,min(T+25,n-2)):
            if c[j]>rhi: brk=(j,1); break
            if c[j]<rlo: brk=(j,-1); break
        if brk is None: T+=24; continue
        j,dirn=brk; events.append((j,dirn,rhi,rlo,mid,a,yr[T])); T=j+5
    print(f"VOLTIME-5 fade: first-break events from mature compression = {len(events)}")
    # INFO: fraction that revert to midpoint before extending +1R (1R = range half-width) beyond break
    rev=0; cont=0
    for j,dirn,rhi,rlo,mid,a,yy in events:
        halfw=0.5*(rhi-rlo)+1e-9; segh=h[j+1:j+1+HMAX]; segl=l[j+1:j+1+HMAX]
        if dirn>0:  # broke up; revert=back to mid (down), continue=+1R above rhi
            rr=np.where(segl<=mid)[0]; cc=np.where(segh>=rhi+halfw)[0]
        else:
            rr=np.where(segh>=mid)[0]; cc=np.where(segl<=rlo-halfw)[0]
        fr=rr[0] if len(rr) else 10**9; fc=cc[0] if len(cc) else 10**9
        if fr<fc: rev+=1
        elif fc<10**9: cont+=1
    tot=rev+cont
    print(f"  INFO path-asymmetry: revert-to-mid-first={rev} continue-first={cont} -> P(revert first)={rev/tot:.3f} (0.5=symmetric)")
    # TRADEABLE fade: SHORT on up-break (mirror), stop=break extreme+/-0.3ATR, target=mid or opposite extreme
    def fade(target="mid"):
        sig=[]
        for j,dirn,rhi,rlo,mid,a,yy in events:
            ei=j+1
            if ei>=n-HMAX: continue
            entry=o[ei]; fdir=-dirn  # fade
            if fdir<0: stop=max(h[j],entry)+0.3*a; tgt=(mid if target=="mid" else rlo)
            else: stop=min(l[j],entry)-0.3*a; tgt=(mid if target=="mid" else rhi)
            risk=abs(entry-stop);
            if risk<=0.05*a: continue
            reward=abs(entry-tgt)/risk
            if reward<0.2: continue
            segl=l[ei:ei+HMAX]; segh=h[ei:ei+HMAX]
            if fdir<0: fs=np.where(segh>=stop)[0]; ft=np.where(segl<=tgt)[0]
            else: fs=np.where(segl<=stop)[0]; ft=np.where(segh>=tgt)[0]
            fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
            if fstop==ftgt==10**9: continue
            R=reward if ftgt<fstop else -1.0
            sig.append((yy,R))
        return sig
    st=lambda a:(len(a),(np.mean([x>0 for x in a]) if len(a) else float('nan')),(np.mean(a) if len(a) else float('nan')),(np.mean([x-COST for x in a]) if len(a) else float('nan')))
    for tg in ["mid","opposite"]:
        s=fade(tg)
        if not s: print(f"  fade->{tg}: 0 sig"); continue
        arr=np.array([x[1] for x in s]); yrs=np.array([x[0] for x in s]); N,wr,g,net=st(arr)
        e=lambda mk: st(arr[mk])[3]
        print(f"  fade->{tg:9s}: n={N:4d} WR={wr:.3f} grossR={g:+.3f} netR={net:+.3f} | D={e(yrs<=2018):+.3f} C={e((yrs>=2019)&(yrs<=2022)):+.3f} O={e(yrs>=2023):+.3f}")
    print("\n=> P(revert first) materially >0.5 AND a fade variant net>0 cross-era => path-asymmetry edge. Else fade side also null.")
if __name__=="__main__": main()
