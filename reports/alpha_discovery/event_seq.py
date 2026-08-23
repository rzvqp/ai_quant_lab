"""event_seq.py — Frontier C: EVENT SEQUENCE (preregistered): compression -> up-break -> FAILED acceptance (close back inside)
-> forward response. Also the down mirror. Info-first: after a failed breakout out of a coil, is the forward OPPOSITE
displacement robust (down after failed up-break), or era-split/none? Causal coil = range over L < 0.6x trailing-median width.
No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
import gate
L=16; H=96
def events(m):
    h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); n=len(m)
    hh=pd.Series(h).rolling(L).max().shift(1).to_numpy(); ll=pd.Series(l).rolling(L).min().shift(1).to_numpy()
    wid=hh-ll; medw=pd.Series(wid).rolling(8*L).median().shift(1).to_numpy(); coil=(wid<0.6*medw)
    up_fail=coil&(h>hh)&(c<hh)   # broke coil high but closed back inside = failed up-break -> expect down
    dn_fail=coil&(l<ll)&(c>ll)   # failed down-break -> expect up
    return np.nan_to_num(up_fail.astype(float),nan=0).astype(bool), np.nan_to_num(dn_fail.astype(float),nan=0).astype(bool)
def main():
    m=CD.load_m15(); c=m["close"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    uf,df=events(m)
    fmax=pd.Series(h).rolling(H).max().shift(-H).to_numpy(); fmin=pd.Series(l).rolling(H).min().shift(-H).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(up)&np.isfinite(dn)&(atr>0)
    print(f"FRONTIER C: compression->failed-break->forward. up-fail={int(uf.sum())} dn-fail={int(df.sum())}")
    def row(msk,rev):  # rev=-1 for up-fail (want down=dn-up>0), +1 for dn-fail (want up)
        nn=int(msk.sum())
        if nn<200: return f"n={nn}(thin)"
        a=np.nanmedian(dn[msk])-np.nanmedian(up[msk]) if rev<0 else np.nanmedian(up[msk])-np.nanmedian(dn[msk])
        return f"n={nn:5d} favorable-asym={a:+.2f}"
    print("  up-fail -> DOWN response:", row(uf&ok,-1))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", row(uf&ok&ym,-1))
    print("  dn-fail -> UP response  :", row(df&ok,+1))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", row(df&ok&ym,+1))
    print("  tradeable (if info robust): fade the failed break")
    gate.screen(m, np.where(uf&ok)[0], -1, atr, "up-fail SHORT")
    gate.screen(m, np.where(df&ok)[0], 1, atr, "dn-fail LONG ")
if __name__=="__main__": main()
