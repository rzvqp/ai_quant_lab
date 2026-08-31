"""factory_falsify.py — ALPHA_DISCOVERY_FACTORY_V2 falsification of the 3 most-distinct data-driven hypotheses (post-dedup).
H1 FAILED_BREAK_FADE_STRUCTURAL: a break of the prior-20 extreme that FAILS (wick beyond, close back inside) -> FADE toward range mid
   (mean-reversion specialist; target=range mid, stop=beyond the sweep extreme). Distinct from continuation.
H2 SWEEP_REVERSE_STRUCTURAL: sweep one extreme (fail) then within K bars break the OPPOSITE extreme -> trade the reversal (liquidity-
   grab reversal; target=structural, stop=the swept extreme).
H3 STRUCTURAL_TARGET_BREAK: HTF-aligned break, target = 100-bar extreme in break dir (STRUCTURAL target, not fixed R), stop=0.5ATR
   below break level (tight structural). Variable R. Tests §17E target-space with a structural (not R-multiple) exit.
Each: NET after STRESS 0.24, cross-era D/C/O, one-trade dependence (best-trade-removed), N. S5 frozen. cur_data M15."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
COST=0.24; H=48
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m); yr=m["dt"].dt.year.to_numpy()
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); e200=pd.Series(c).ewm(span=200,adjust=False).mean().to_numpy()
    p20H=pd.Series(h).rolling(20).max().shift(1).to_numpy(); p20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    p20M=(p20H+p20L)/2
    hi100=pd.Series(h).rolling(100).max().shift(1).to_numpy(); lo100=pd.Series(l).rolling(100).min().shift(1).to_numpy()
    def era(i): return "D" if yr[i]<=2018 else ("C" if yr[i]<=2022 else "O")
    def sim(entry,stop,tgt,dirn,ei):
        risk=abs(entry-stop); rr=abs(tgt-entry)/risk if risk>0 else 0
        if risk<=0.05*atr[ei-1] if ei>0 else True: return None
        segl=l[ei:ei+H]; segh=h[ei:ei+H]
        if dirn>0: fs=np.where(segl<=stop)[0]; ft=np.where(segh>=tgt)[0]
        else: fs=np.where(segh>=stop)[0]; ft=np.where(segl<=tgt)[0]
        fstop=fs[0] if len(fs) else 10**9; ftgt=ft[0] if len(ft) else 10**9
        if fstop==ftgt==10**9: return None
        return rr if ftgt<fstop else -1.0
    H1=[]; H2=[]; H3=[]; last1=last2=last3=-10**9
    for T in range(120,n-H-6):
        if not np.isfinite(atr[T]) or atr[T]<=0 or not np.isfinite(p20H[T]) or not np.isfinite(hi100[T]): continue
        a=atr[T]; ei=T+1
        # H1 failed-break fade
        fbu=h[T]>p20H[T] and c[T]<p20H[T]; fbd=l[T]<p20L[T] and c[T]>p20L[T]
        if (fbu or fbd) and T-last1>=6:
            dirn=-1 if fbu else 1; entry=o[ei]; stop=(h[T]+0.2*a) if fbu else (l[T]-0.2*a); tgt=p20M[T]
            r=sim(entry,stop,tgt,dirn,ei)
            if r is not None: H1.append((era(T),r)); last1=T
        # H2 sweep then opposite break (within 8 bars)
        if (fbu or fbd) and T-last2>=6:
            if fbu:
                brk=np.where(c[T+1:T+9]<p20L[T])[0]  # after sweep-high, break low
                if len(brk): j=T+1+brk[0]; ei2=j+1
                if len(brk) and ei2<n-H:
                    entry=o[ei2]; stop=h[T]+0.2*a; tgt=lo100[T]
                    r=sim(entry,stop,tgt,-1,ei2)
                    if r is not None: H2.append((era(T),r)); last2=T
            else:
                brk=np.where(c[T+1:T+9]>p20H[T])[0]
                if len(brk): j=T+1+brk[0]; ei2=j+1
                if len(brk) and ei2<n-H:
                    entry=o[ei2]; stop=l[T]-0.2*a; tgt=hi100[T]
                    r=sim(entry,stop,tgt,1,ei2)
                    if r is not None: H2.append((era(T),r)); last2=T
        # H3 HTF-aligned structural-target break
        up=c[T]>p20H[T]; dn=c[T]<p20L[T]
        if (up or dn) and T-last3>=6:
            dirn=1 if up else -1
            htf=(dirn>0 and e20[T]>e50[T] and c[T]>e200[T]) or (dirn<0 and e20[T]<e50[T] and c[T]<e200[T])
            if htf:
                lvl=p20H[T] if up else p20L[T]; entry=o[ei]; stop=lvl-0.5*a*dirn
                tgt=hi100[T] if up else lo100[T]
                if (dirn>0 and tgt>entry+0.3*a) or (dirn<0 and tgt<entry-0.3*a):
                    r=sim(entry,stop,tgt,dirn,ei)
                    if r is not None: H3.append((era(T),r)); last3=T
    def rep(name,rows):
        if len(rows)<80: return f"{name}: n={len(rows)} INSUFFICIENT"
        arr=np.array([x[1] for x in rows]); net=np.mean(arr-COST)
        eras={e:np.mean([x[1]-COST for x in rows if x[0]==e]) for e in ["D","C","O"]}
        btr=np.mean(np.sort(arr)[:-1]-COST)  # best-trade removed
        stable=all(v<0 for v in eras.values()) or all(v>0 for v in eras.values())
        return (f"{name}: n={len(rows):4d} netR={net:+.3f} | D={eras['D']:+.2f} C={eras['C']:+.2f} O={eras['O']:+.2f} "
                f"best-trade-removed={btr:+.3f} sign-stable={stable} "+("<== POSITIVE cross-era" if (net>0 and all(v>0 for v in eras.values())) else ""))
    print("ALPHA_DISCOVERY_FACTORY_V2 falsification (STRESS 0.24, cross-era, best-trade-removed):")
    print("  "+rep("H1 FAILED_BREAK_FADE_STRUCTURAL",H1))
    print("  "+rep("H2 SWEEP_REVERSE_STRUCTURAL   ",H2))
    print("  "+rep("H3 STRUCTURAL_TARGET_BREAK    ",H3))
    print("=> a candidate needs netR>0 AND all-era>0 AND not one-trade-dependent. Else FALSIFIED.")
if __name__=="__main__": main()
