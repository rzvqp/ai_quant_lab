"""frontier_r.py — FRONTIER R: the VOLUME dimension (untested in the whole campaign; part of OHLCV, same instrument,
NOT exogenous). Does relative (tick-)volume add cross-era-stable information to a direction-resolving displacement
event? Info-first: displacement-UP continuation asym P(+70/-50 L)-P(+70/-50 S) conditioned on HIGH vs LOW relative
volume, cross-era. If high-volume displacement has materially + cross-era-stable better continuation -> volume is a
genuine causal filter. First verifies volume is present + non-degenerate across all eras.
"""
import numpy as np, pandas as pd, bscreen as bs
from state_path_m15 import passage_m15, Pm
HB=48

def main():
    eras=bs.build_eras()
    print("[volume availability check]")
    for tag,fr,mask in eras:
        v=fr["volume"].to_numpy() if "volume" in fr.columns else None
        if v is None: print(f"  {tag}: NO volume column"); continue
        vm=v[mask]; print(f"  {tag}: n={mask.sum()} vol med={np.nanmedian(vm):.0f} nonzero={np.mean(vm>0):.2f} distinct={len(np.unique(vm[:5000]))}")
    frames={}
    for tag,fr,m in eras: frames.setdefault(id(fr),fr)
    if not all("volume" in f.columns for f in frames.values()):
        print("volume missing in some era -> cannot test cross-era. PIVOT."); return
    PSG={k:passage_m15(v,Hmax=HB) for k,v in frames.items()}
    print("\n[Frontier R] displacement-UP->LONG continuation asym P(+70/-50 L)-P(+70/-50 S), by relative-volume tercile, cross-era:")
    for tag,fr,mask in eras:
        ou,od,mfe,mae=PSG[id(fr)]
        o=fr["open"].to_numpy(); c=fr["close"].to_numpy(); h=fr["high"].to_numpy(); l=fr["low"].to_numpy(); atr=fr["atr"].to_numpy(); rng=h-l
        v=fr["volume"].to_numpy(); vma=pd.Series(v).rolling(50).mean().shift(1).to_numpy(); relv=v/vma
        up=((c-o)>0.7*atr)&(c>l+0.75*rng)&(rng>1.2*atr)
        up=mask&np.nan_to_num(up.astype(float),nan=0).astype(bool)&np.isfinite(relv)
        idx=np.where(up)[0]
        if len(idx)<90: print(f"  {tag}: n{len(idx)} thin"); continue
        q=np.nanquantile(relv[idx],[0.5])  # split high/low vol
        for lab,sel in [("Vhi",relv[idx]>=q[0]),("Vlo",relv[idx]<q[0])]:
            ii=idx[sel]; mm=np.zeros(len(fr),bool); mm[ii]=True
            a=Pm(ou,od,70,50,'L',HB,mm)[0]-Pm(ou,od,70,50,'S',HB,mm)[0]
            print(f"  {tag} {lab}: n={len(ii)} asym70={a:+.2f}", end="  ")
        print()

if __name__=="__main__":
    main()
