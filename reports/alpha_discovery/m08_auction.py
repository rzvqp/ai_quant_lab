"""m08_auction.py — MODULAR_DISCOVERY_V1, M08 auction/reference remaining branches: value-migration + reclaim-reversal.
Price-only reference = prior calendar day's High/Low (PDH/PDL), CAUSAL (prior COMPLETED day, shifted). Data cur_data M15.
BRANCH value-migration: on a decisive close BEYOND PDH by >0.5ATR (upward value-migration / acceptance), does price CONTINUE
(migration persists) or REVERT? forward excursion-asym, symmetric with PDL downside. BRANCH reclaim-reversal (failed break):
high>PDH but close<=PDH (rejected above) -> SHORT; low<PDL but close>=PDL (rejected below) -> LONG. Info-positive only if the
mechanic's own direction is robust across eras (D<=2018/C19-22/O23+), not era-trend."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    day=m["dt"].dt.date.to_numpy()
    dfd=pd.DataFrame({"day":day,"h":h,"l":l})
    dh=dfd.groupby("day")["h"].max(); dl=dfd.groupby("day")["l"].min()
    days=list(dh.index); pdh_map={days[i]:dh.iloc[i-1] for i in range(1,len(days))}; pdl_map={days[i]:dl.iloc[i-1] for i in range(1,len(days))}
    pdh=np.array([pdh_map.get(d,np.nan) for d in day]); pdl=np.array([pdl_map.get(d,np.nan) for d in day])
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    valid=np.isfinite(up)&np.isfinite(dn)&np.isfinite(atr)&(atr>0)&np.isfinite(pdh)&np.isfinite(pdl)
    def row(mask,ln):
        idx=np.where(mask&valid)[0]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):6d} asym={a:+.2f}"
    def report(name,mask,ln):
        line=f"  {name}: {row(mask,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            line+=f" | {pl} {row(mask&ym,ln)}"
        print(line)
    # value-migration (acceptance beyond reference)
    mig_up=(c>pdh+0.5*atr); mig_dn=(c<pdl-0.5*atr)
    print(f"M08 value-migration: up-accept bars={int((mig_up&valid).sum())} dn-accept bars={int((mig_dn&valid).sum())}")
    report("accept>PDH -> CONTINUE-UP(LONG)",mig_up,1)
    report("accept<PDL -> CONTINUE-DN(SHORT)",mig_dn,-1)
    # reclaim-reversal (failed break)
    rej_above=(h>pdh)&(c<=pdh); rej_below=(l<pdl)&(c>=pdl)
    print(f"M08 reclaim-reversal: rejected-above bars={int((rej_above&valid).sum())} rejected-below bars={int((rej_below&valid).sum())}")
    report("reject-above PDH -> SHORT",rej_above,-1)
    report("reject-below PDL -> LONG",rej_below,1)
    print("  => tradeable only if the mechanic's own direction is robust across ALL eras (not era-trend).")
if __name__=="__main__": main()
