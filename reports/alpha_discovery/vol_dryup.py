"""vol_dryup.py — Frontier A: VOLUME DRY-UP preceding structural expansion (info-first). Distinct from confirmation/climax.
Dry-up = tick-volume below trailing norm for K consecutive bars (accumulation/coiling). Q1(info): does forward realized range
EXPAND after dry-up (vs baseline)? Q2(info): is the expansion DIRECTIONAL (up-dn excursion asym, P(upFirst) != 0.5) or symmetric?
Only if directional -> tradeable. Causal: vz=volume/rolling-median(V).shift(1); range fwd over H. No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
K=6; V=50; H=96
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); vol=m["volume"].to_numpy(); n=len(m)
    vz=vol/pd.Series(vol).rolling(V).median().shift(1).to_numpy()
    dry=pd.Series((vz<0.6).astype(float)).rolling(K).sum().to_numpy()>=K  # K consecutive low-vol bars
    fmax=pd.Series(h).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(l).rolling(H).min().shift(-H).to_numpy()
    frng=(fmax-fmin)/atr; up=(fmax-c)/atr; dn=(c-fmin)/atr
    yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(frng)&np.isfinite(atr)&(atr>0)&np.isfinite(vz)
    dry=np.nan_to_num(dry.astype(float),nan=0).astype(bool)
    print("FRONTIER A: volume DRY-UP -> forward expansion + directionality (info-first).")
    def row(msk):
        nn=int(msk.sum())
        if nn<200: return f"n={nn}(thin)"
        return f"n={nn:6d} fwdRange={np.nanmedian(frng[msk]):.2f}ATR up-dn={np.nanmedian(up[msk])-np.nanmedian(dn[msk]):+.2f}"
    print("  [dry-up]  :", row(dry&ok))
    print("  [baseline]:", row((~dry)&ok))
    for lab,ym in [("DISC",yr<=2021),("CONF",(yr>=2022)&(yr<=2024)),("OOS",yr>=2025)]:
        print(f"    dry-up {lab}:", row(dry&ok&ym))
    print("  => expansion directional? (up-dn != 0 robustly) determines whether a tradeable form is built.")
if __name__=="__main__": main()
