"""autocorr_adaptive.py — Frontier I: AUTOCORRELATION-ADAPTIVE meta-strategy (genuinely-novel; the market's own persistence
character as a causal state). Rolling lag-1 return autocorrelation AC over W bars (causal). If AC>0 (persistent/trending micro-
regime) -> trade WITH the recent R-bar move (momentum); if AC<0 (mean-reverting) -> trade AGAINST it (reversion). Does adapting
by AC beat either alone? Info-first: does AC sign predict forward continuation-of-recent-move? Then tradeable. No like_at."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
W=50; R=4; H=96
def main():
    m=CD.load_m15(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    ret=pd.Series(c).diff().to_numpy()
    sr=pd.Series(ret); AC=sr.rolling(W).corr(sr.shift(1)).shift(1).to_numpy()  # vectorized rolling lag-1 autocorr (causal)
    recent=(c-pd.Series(c).shift(R).to_numpy())  # recent R-bar move
    dir_=np.sign(recent); ok=np.isfinite(AC)&np.isfinite(atr)&(atr>0)&(dir_!=0)
    # adaptive side: AC>0 -> with dir (momentum); AC<0 -> against dir (reversion)
    side=np.where(AC>0, dir_, -dir_).astype(int)
    fmax=pd.Series(m["high"].to_numpy()).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(m["low"].to_numpy()).rolling(H).min().shift(-H).to_numpy()
    fwd=(pd.Series(c).shift(-H).to_numpy()-c)/atr; yr=m["dt"].dt.year.to_numpy()
    print("FRONTIER I: autocorrelation-adaptive. info: forward return in adaptive-side direction (should be >0 if AC informs):")
    signed=fwd*side
    def row(msk):
        nn=int(msk.sum()); return f"n={nn:6d} sided-fwdRet={np.nanmedian(signed[msk]):+.3f}ATR" if nn>=300 else "thin"
    print("  ALL:", row(ok), "| AC>0:", row(ok&(AC>0)), "| AC<0:", row(ok&(AC<0)))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", row(ok&ym))
    # tradeable: enter adaptive side, dedup, gate (split by side to use scalar side)
    idxL=np.where(ok&(side==1))[0]; idxS=np.where(ok&(side==-1))[0]
    print("  tradeable adaptive (long-leg + short-leg):")
    rL=gate.screen(m, idxL, 1, atr, "adaptive LONG-leg ")
    rS=gate.screen(m, idxS, -1, atr, "adaptive SHORT-leg")
    if rL and rS:
        r=np.concatenate([rL['r'],rS['r']]); yr2=np.concatenate([rL['yr'],rS['yr']])
        d=r[yr2<=2021].mean(); cc=r[(yr2>=2022)&(yr2<=2024)].mean(); o=r[yr2>=2025].mean()
        print(f"  COMBINED adaptive: N={len(r)} avgR={r.mean():+.4f} | D {d:+.3f} C {cc:+.3f} O {o:+.3f}")
if __name__=="__main__": main()
