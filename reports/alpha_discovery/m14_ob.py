"""m14_ob.py — MODULAR_DISCOVERY_V1, M14 ORDER-BLOCK (info-first §8/§9, ratified Mod.5 order_flow). OB = geometric body of the
last opposite bar before an impulse (zone_lower/upper, kind demand/supply). Hypothesis: at an OB REJECTION (price returns to the
zone and reacts), price moves in the OB polarity (demand→up, supply→down). INFO: forward excursion asym by OB kind, partitioned
DISC<=2018/CONF19-22/OOS23+. Causal (rejection uses horizon after formation). Data cur_data M15 2011-2026."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD, order_flow as OF
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); t=m["time"].to_numpy(); n=len(m)
    obs=OF.detect_order_blocks(o,h,l,c, n)  # single block_end=n (whole data)
    KIND=OF.OrderBlockKind; kinds=list(KIND); DEM=[k for k in kinds if 'DEM' in k.name or 'BULL' in k.name][0]
    # rejections per OB
    ev_dem=[]; ev_sup=[]
    for ob in obs:
        rej=OF.detect_rejections(ob,h,l,c, n)
        for e in rej:
            i=e.event_idx
            if i is None or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
            (ev_dem if ob.kind==DEM else ev_sup).append(int(i))
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    print(f"M14 OB info: order_blocks={len(obs)} demand-rejections={len(ev_dem)} supply-rejections={len(ev_sup)} (DEM={DEM})")
    def row(idx,ln):
        idx=np.array(sorted(set(idx)),int); idx=idx[idx<n-1]; ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} asym={a:+.2f}"
    for nm,ev,ln in [("DEMAND-OB rej -> LONG(up)",ev_dem,1),("SUPPLY-OB rej -> SHORT(dn)",ev_sup,-1)]:
        line=f"  {nm}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
    print("  => M14 supports tradeable only if OB-polarity asym robustly>0 across partitions (not era-trend).")
if __name__=="__main__": main()
