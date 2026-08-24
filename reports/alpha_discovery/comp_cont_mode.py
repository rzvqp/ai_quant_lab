"""comp_cont_mode.py — COMP-CONT-L-MODE-BULL-v1 (mandate ALPHA-COMP-CONT-MODE-BULL-V1-001). NEW identity; inherits
NOTHING from the failed COMP-CONT-L-rr2. Question: does the FROZEN MARKET_OPERATING_MODE_V1 == PRIMARY_BULL_IMPULSE
add STABLE cross-era forward information to H4 compression->continuation (LONG), replacing the old D1-uptrend regime?
Information-first: compares comp->cont GLOBAL vs inside PRIMARY_BULL, cross-era (b0/b1/DEV/CAL). Then tradeability
(structural stop = compression low, STRESS). Frozen mode untouched. No post-hoc regime rescue (only PRIMARY_BULL).
"""
import numpy as np, pandas as pd
import swing_base as sb, hist_data as hd
import market_mode as MM
from state_path_m15 import passage_m15, Pm
NB=8; HB=12  # H4: compression box over 8 bars; forward 12 H4 bars = 2 days

def comp_cont(fr):
    h=fr["high"]; l=fr["low"]; c=fr["close"].to_numpy(); atr=fr["atr"].to_numpy(); atrm=fr["atr_ma"].to_numpy()
    box_hi=h.rolling(NB).max().shift(1).to_numpy(); box_lo=l.rolling(NB).min().shift(1).to_numpy()
    box=box_hi-box_lo; box_ma=pd.Series(box).rolling(50).mean().shift(1).to_numpy(); vr=atr/atrm
    comp=(box<0.7*box_ma)&(vr<0.9)&np.isfinite(box_ma); cp=pd.Series(comp).shift(1).fillna(False).to_numpy().astype(bool)
    rng=(h.to_numpy()-l.to_numpy())
    cont_up=cp&(c>box_hi)&(rng>1.3*atr)   # continuation = break UP out of compression
    return np.nan_to_num(cont_up.astype(float),nan=0).astype(bool), box_lo

def run():
    hh=hd._load("H4"); ss=sb.build_frames()["H4"]
    frames=[("b0",hh,"is_b0"),("b1",hh,"is_b1"),("DEV",ss,"is_dev"),("CAL",ss,"is_cal")]
    PSG={"h":passage_m15(hh,Hmax=HB),"s":passage_m15(ss,Hmax=HB)}; PS={"b0":"h","b1":"h","DEV":"s","CAL":"s"}
    print("COMP-CONT-L-MODE-BULL-v1: H4 compression->continuation LONG. INFORMATION-FIRST P(+70/-50) L/S. Frozen PRIMARY_BULL. Cross-era.")
    print("era | PB_bars | comp-cont: GLOBAL n / P70 L/S | inside PRIMARY_BULL n / P70 L/S | tradeR(structSL,STRESS)")
    trade_by_era={}
    for tag,fr,mk in frames:
        lab=MM.mode(fr); PB=(lab=="PRIMARY_BULL_IMPULSE"); mask=fr[mk].to_numpy()
        ev,box_lo=comp_cont(fr); ou,od,mfe,mae=PSG[PS[tag]]; n=len(fr)
        gmask=mask&ev; pmask=mask&ev&PB
        def p70(m):
            mm=np.zeros(n,bool); idx=np.where(m)[0]; idx=idx[idx<n-1]; mm[idx]=True
            if idx.size<20: return None
            return Pm(ou,od,70,50,'L',HB,mm)[0], Pm(ou,od,70,50,'S',HB,mm)[0], idx.size
        g=p70(gmask); p=p70(pmask)
        # tradeability inside PRIMARY_BULL
        o=fr["open"].to_numpy(); idx=np.where(pmask)[0]; idx=idx[idx<n-1]
        tr_s="thin"
        if idx.size>=20:
            entry=o[idx+1]; sl=np.abs(entry-box_lo[idx]); ok=np.isfinite(sl)&(sl>0); idx2=idx[ok]; sl=sl[ok]
            tr=sb.simulate(fr,idx2,1,sl,rr=2.0,horizon=HB,scenario="STRESS")
            if len(tr): mm=sb.metrics(tr,fr,2.0); trade_by_era[tag]=tr; tr_s=f"avgR{mm['avgR']:+.3f}(n{len(tr)})"
        gs=f"n{g[2]} L{g[0]:.2f}/S{g[1]:.2f}" if g else "thin"
        ps=f"n{p[2]} L{p[0]:.2f}/S{p[1]:.2f}" if p else "thin"
        print(f"  {tag:4s} | PB={int(PB[mask].sum())} | GLOBAL {gs} | PRIMARY_BULL {ps} | {tr_s}")
    # DISC/CONF on pooled PRIMARY_BULL trades
    if trade_by_era:
        allt=pd.concat(trade_by_era.values(),ignore_index=True).sort_values("t_entry")
        r=allt["R"].to_numpy(); cut=int(len(r)*0.6)
        print(f"\n  POOLED PRIMARY_BULL comp-cont-long: N={len(r)} avgR={r.mean():+.3f} DISC={r[:cut].mean():+.3f} CONF={r[cut:].mean():+.3f} pos-eras={sum(1 for t in trade_by_era if trade_by_era[t]['R'].mean()>0)}/{len(trade_by_era)}")

if __name__=="__main__":
    run()
