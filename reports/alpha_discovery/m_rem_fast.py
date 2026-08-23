"""m_rem_fast.py — MODULAR_DISCOVERY_V1, remaining fast pure-price branches (all CAUSAL, cur_data M15, partitions D<=2018/
C19-22/O23+). Closes the low-priority/bounded open branches for full coverage:
 M01 persistence-hold  : forward up-asym in ema-up state by run-age (does trend persistence lift continuation?)
 M02 Fib/measured      : pullback to 50% retrace of prior 20-bar leg in trend context -> continuation
 M05 session-extreme   : sweep of Asian (00-08 UTC) session H/L during London+NY -> reversal
 M06 vol-regime-MR     : after a 4-bar +/-1ATR thrust, P(revert 0.5ATR) in HIGH-vol vs LOW-vol (non-directional MR)
 M07 session-transition: at NY open (13:00 UTC) does the London (08-13) session return CONTINUE or reverse?
 M12 multi-leg         : two consecutive same-dir 20-bar-breakout legs (no intervening opposite) -> continuation"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m)
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy(); yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy(); dayk=m["dt"].dt.date.to_numpy()
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr
    base=np.isfinite(up)&np.isfinite(dn)&np.isfinite(atr)&(atr>0)
    def row(mask,ln):
        idx=np.where(mask&base)[0]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):6d} asym={a:+.2f}"
    def report(name,mask,ln):
        line=f"  {name}: {row(mask,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            line+=f" | {pl} {row(mask&ym,ln)}"
        print(line)
    # ---- M01 persistence-hold ----
    emaup=e20>e50; age=np.zeros(n,int)
    for i in range(1,n): age[i]=age[i-1]+1 if emaup[i] else 0
    print("M01 persistence-hold (ema-up state, forward up-asym by run-age):")
    for lo,hi in [(1,20),(20,60),(60,150),(150,10**9)]:
        report(f"age[{lo},{hi})->LONG",(age>=lo)&(age<hi),1)
    # ---- M02 Fib/measured ----
    hi20=pd.Series(h).rolling(20).max().shift(1).to_numpy(); lo20=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    rng=hi20-lo20; fib=lo20+0.5*rng
    pb_up=emaup&(l<=fib)&(c>fib)&(rng>0)   # up-context pullback to 50% then close above
    pb_dn=(~emaup)&(h>=lo20+0.5*rng)&(c<lo20+0.5*rng)&(rng>0)
    print("M02 Fib/measured 50%-retrace continuation:")
    report("up-context 50%-retrace->LONG",pb_up,1); report("dn-context 50%-retrace->SHORT",pb_dn,-1)
    # ---- M05 session-extreme-sweep (Asian 00-08 UTC H/L) ----
    asia=(hr>=0)&(hr<8); df=pd.DataFrame({"d":dayk,"h":h,"l":l,"a":asia})
    ah=df[df.a].groupby("d")["h"].max(); al=df[df.a].groupby("d")["l"].min()
    ahm={d:v for d,v in ah.items()}; alm={d:v for d,v in al.items()}
    asiaH=np.array([ahm.get(d,np.nan) for d in dayk]); asiaL=np.array([alm.get(d,np.nan) for d in dayk])
    ldn=(hr>=8)&(hr<20)  # London+NY window
    swH=ldn&(h>asiaH)&(c<=asiaH)&np.isfinite(asiaH)   # swept Asian high, closed back -> SHORT
    swL=ldn&(l<asiaL)&(c>=asiaL)&np.isfinite(asiaL)   # swept Asian low, closed back -> LONG
    print("M05 session-extreme-sweep (Asian H/L swept during London+NY):")
    report("sweep Asian-High->SHORT",swH,-1); report("sweep Asian-Low ->LONG",swL,1)
    # ---- M06 vol-regime-MR ----
    thrust_up=(c-np.roll(c,4))>=1.0*atr; thrust_dn=(np.roll(c,4)-c)>=1.0*atr
    hivol=atr>1.3*atr_ma; lovol=atr<0.8*atr_ma
    def p_revert(mask,updir):
        idx=np.where(mask&base)[0]; wins=0;tot=0
        for i in idx:
            if i>=n-1: continue
            tgt=0.5*atr[i]
            if updir: rev=(c[i]-l[i+1:i+49]).max() if i+1<n else -1; hit=rev>=tgt
            else: rev=(h[i+1:i+49]-c[i]).max() if i+1<n else -1; hit=rev>=tgt
            tot+=1; wins+=hit
        return (wins/tot if tot else float('nan')),tot
    for vn,vm in [("HItvol",hivol),("LOvol",lovol)]:
        pu,tu=p_revert(thrust_up&vm,True); pd_,td=p_revert(thrust_dn&vm,False)
        print(f"  M06 {vn}: after +thrust P(revert .5ATR)={pu:.3f} n={tu} | after -thrust P(revert)={pd_:.3f} n={td}")
    # ---- M07 session-transition ----
    # London session return sign (close@~13:00 - close@~08:00) predicts NY forward?
    ny_open=(hr==13); df2=pd.DataFrame({"d":dayk,"hr":hr,"c":c})
    c08={}; c13idx=[]
    for i in range(n):
        if hr[i]==8 and dayk[i] not in c08: c08[dayk[i]]=c[i]
    for i in range(n):
        if hr[i]==13 and dayk[i] in c08:
            c13idx.append((i,np.sign(c[i]-c08[dayk[i]])))
    lon_up=np.zeros(n,bool); lon_dn=np.zeros(n,bool)
    for i,sgn in c13idx:
        if sgn>0: lon_up[i]=True
        elif sgn<0: lon_dn[i]=True
    print("M07 session-transition (London-return sign -> NY forward):")
    report("London-up -> NY LONG",lon_up,1); report("London-dn -> NY SHORT",lon_dn,-1)
    # ---- M12 multi-leg ----
    leg_up=(c>hi20).astype(int); leg_dn=(c<lo20).astype(int); K=40
    up_prev=pd.Series(leg_up).rolling(K).sum().shift(1).to_numpy()  # up-legs in prior K bars
    dn_prev=pd.Series(leg_dn).rolling(K).sum().shift(1).to_numpy()
    ml_up=(leg_up==1)&(up_prev>=1)&(dn_prev==0)   # 2nd+ up-leg, no intervening down-leg
    ml_dn=(leg_dn==1)&(dn_prev>=1)&(up_prev==0)
    print("M12 multi-leg (2nd consecutive same-dir 20-bar breakout):")
    report("2x up-leg -> LONG",ml_up,1); report("2x dn-leg -> SHORT",ml_dn,-1)
    print("  => each branch tradeable only if BOTH sides robustly>0 (dir edge) / P clearly>0.5 (non-dir), across ALL eras.")
if __name__=="__main__": main()
