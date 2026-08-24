"""session_inherit.py — Frontier E: SESSION INHERITANCE (causal). Does the PRIOR session's range/direction inform the NEXT
session's directional resolution? Sessions (UTC): Asia 0-7, London 7-13, NY 13-21. For each session, prior-session range
[lo,hi] + prior-session net direction; test whether the next session breaks in the prior direction (momentum) or opposite
(reversion), info-first. Causal (prior session fully closed). Distinct from S5 (S5=NY opening-range breakout; this=prior-session
inheritance). No like_at. Data thru 2026-07-27."""
import numpy as np, pandas as pd
import cur_data as CD
def main():
    m=CD.load_m15(); hr=m["dt"].dt.hour.to_numpy(); c=m["close"].to_numpy(); o=m["open"].to_numpy(); atr=m["atr"].to_numpy()
    day=m["dt"].dt.floor("D").astype("int64").to_numpy()
    sess=np.where(hr<7,0,np.where(hr<13,1,np.where(hr<21,2,3)))  # 0 Asia 1 London 2 NY 3 late
    # session id = day*4+sess ; group net direction + range
    sid=day*10+sess
    g=pd.DataFrame({"sid":sid,"o":o,"c":c,"h":m["high"].to_numpy(),"l":m["low"].to_numpy()}).groupby("sid")
    net=(g["c"].last()-g["o"].first()); rng=(g["h"].max()-g["l"].min())
    sdir=pd.Series(sid).map(np.sign(net)).to_numpy(); srng=pd.Series(sid).map(rng).to_numpy()
    # prior-session net direction (shift by one session): map each session to the previous distinct session's dir
    uniq=pd.Series(sid).drop_duplicates().to_numpy(); prevdir={}
    ndir=np.sign(net); 
    for i in range(1,len(uniq)): prevdir[uniq[i]]=ndir.get(uniq[i-1],0)
    pdirbar=pd.Series(sid).map(prevdir).to_numpy()
    # forward: this session's net direction; does it match prior?
    fwd=pd.Series(sid).map(ndir).to_numpy()
    yr=m["dt"].dt.year.to_numpy(); ok=np.isfinite(pdirbar)&(pdirbar!=0)
    # one row per session (first bar)
    firstbar=np.r_[True,sid[1:]!=sid[:-1]]
    msk=ok&firstbar
    print("FRONTIER E: session inheritance. P(next-session dir == prior-session dir):")
    def pr(m2):
        nn=int(m2.sum())
        if nn<200: return f"n={nn}(thin)"
        match=(fwd[m2]==pdirbar[m2]).mean(); return f"n={nn:5d} P(match)={match:.3f}"
    print("  ALL:", pr(msk))
    for pl,ym in [("D",yr<=2021),("C",(yr>=2022)&(yr<=2024)),("O",yr>=2025)]: print(f"    {pl}:", pr(msk&ym))
    print("  (P(match)>>0.5 = momentum inheritance; <<0.5 = reversion; ~0.5 = no inheritance)")
if __name__=="__main__": main()
