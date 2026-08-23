"""auction.py — Frontier D: AUCTION / reference-level acceptance vs rejection (info-first). Prior-day high/low (PDH/PDL, causal
= previous completed day). ACCEPTED-ABOVE-PDH = close>PDH for K bars (value migrated up) -> continuation? REJECTED-AT-PDH =
touched PDH, closed back below (failed auction) -> reversion? Mirror for PDL. Info-first: forward up-dn per event, partitioned.
Distinct from CR-10 (which tested single-bar break/reject); this tests multi-bar ACCEPTANCE (value migration). No like_at."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
K=4; H=96
def pdlevels(m):
    day=m["dt"].dt.floor("D"); dlow=m.groupby(day)["low"].min(); dhigh=m.groupby(day)["high"].max()
    PDL=day.map(dlow.shift(1)).to_numpy(); PDH=day.map(dhigh.shift(1)).to_numpy(); return PDL,PDH
def main():
    m=CD.load_m15(); c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    PDL,PDH=pdlevels(m)
    acc_above=(pd.Series((c>PDH).astype(float)).rolling(K).sum().to_numpy()>=K)   # accepted above PDH
    acc_below=(pd.Series((c<PDL).astype(float)).rolling(K).sum().to_numpy()>=K)
    # fresh acceptance = first bar of the K-run
    acc_above=acc_above&~np.r_[False,acc_above[:-1]]; acc_below=acc_below&~np.r_[False,acc_below[:-1]]
    fmax=pd.Series(h).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(l).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&(atr>0)
    aa=np.nan_to_num(acc_above.astype(float),nan=0).astype(bool); ab=np.nan_to_num(acc_below.astype(float),nan=0).astype(bool)
    print(f"FRONTIER D: PDH/PDL acceptance (value migration). acc-above={int(aa.sum())} acc-below={int(ab.sum())}")
    def row(msk):
        nn=int(msk.sum())
        if nn<150: return f"n={nn}(thin)"
        return f"n={nn:5d} up-dn={np.nanmedian(up[msk])-np.nanmedian(dn[msk]):+.2f}"
    print("  accepted-ABOVE-PDH -> up-continuation:", row(aa&ok))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", row(aa&ok&ym))
    print("  accepted-BELOW-PDL -> dn-continuation:", row(ab&ok))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", row(ab&ok&ym))
    print("  tradeable (value-migration continuation):")
    gate.screen(m, np.where(aa&ok)[0], 1, atr, "acc-above LONG ")
    gate.screen(m, np.where(ab&ok)[0], -1, atr, "acc-below SHORT")
if __name__=="__main__": main()
