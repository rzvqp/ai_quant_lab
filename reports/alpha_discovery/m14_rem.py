"""m14_rem.py — MODULAR_DISCOVERY_V1, M14 remaining branches: OB-mitigation + demand-zone-reentry.
Ratified Mod.5 order_flow. BRANCH-2 OB-MITIGATION: detect_mitigations = wick touches the OB body zone (vs rejection = wick
penetrates+closes back). Hypothesis: after mitigation, price moves in OB polarity (demand->up). BRANCH-3 DEMAND-ZONE-REENTRY:
detect_demand_zones = FULL [Low,High] anchor-bar zone (superset of OB body); reentry = a later bar (after a >=6-bar gap) whose
range intersects the zone; does OB polarity predict forward direction after reentry? Both CAUSAL (event_idx / reentry bar >=
formation; excursion strictly forward). Partitions DISC<=2018/CONF19-22/OOS23+. Data cur_data M15 2011-2026."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD, order_flow as OF
def main():
    m=CD.load_m15(); o=m["open"].to_numpy(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    KIND=OF.OrderBlockKind; DEM=[k for k in KIND if 'DEM' in k.name or 'BULL' in k.name][0]
    def row(idx,ln):
        idx=np.array(sorted(set(int(x) for x in idx)),int); idx=idx[(idx>=0)&(idx<n-1)]
        ok=np.isfinite(up[idx])&np.isfinite(dn[idx]); idx=idx[ok]
        if len(idx)<150: return f"n={len(idx)}(thin)"
        a=np.median(up[idx])-np.median(dn[idx]) if ln>0 else np.median(dn[idx])-np.median(up[idx])
        return f"n={len(idx):5d} asym={a:+.2f}"
    def report(name,ev,ln):
        line=f"  {name}: {row(ev,ln)}"
        for pl,ym in [("D",yr<=2018),("C",(yr>=2019)&(yr<=2022)),("O",yr>=2023)]:
            ii=[x for x in ev if 0<=x<n and ym[x]]; line+=f" | {pl} {row(ii,ln)}"
        print(line)
    obs=OF.detect_order_blocks(o,h,l,c,n)
    # ---- BRANCH-2 OB-MITIGATION ----
    mit_dem=[]; mit_sup=[]
    for ob in obs:
        for e in OF.detect_mitigations(ob,h,l,c,n):
            i=e.event_idx
            if i is None or i>=n-1 or not np.isfinite(atr[i]) or atr[i]<=0: continue
            (mit_dem if ob.kind==DEM else mit_sup).append(int(i))
    print(f"M14-MIT: order_blocks={len(obs)} demand-mitigations={len(mit_dem)} supply-mitigations={len(mit_sup)}")
    report("DEMAND-OB mitigation -> LONG",mit_dem,1)
    report("SUPPLY-OB mitigation -> SHORT",mit_sup,-1)
    # ---- BRANCH-3 DEMAND-ZONE-REENTRY ----
    zones=OF.detect_demand_zones(o,h,l,c,n)
    rz_dem=[]; rz_sup=[]; GAP=6
    for z in zones:
        a=z.formation_idx; zl=z.zone_lower; zu=z.zone_upper; hit=None
        for j in range(a+GAP, min(a+400,n)):   # first reentry after gap, bounded scan
            if l[j]<=zu and h[j]>=zl: hit=j; break
        if hit is None or hit>=n-1 or not np.isfinite(atr[hit]) or atr[hit]<=0: continue
        (rz_dem if z.kind==DEM else rz_sup).append(int(hit))
    print(f"M14-DZ: zones={len(zones)} demand-reentries={len(rz_dem)} supply-reentries={len(rz_sup)}")
    report("DEMAND-ZONE reentry -> LONG",rz_dem,1)
    report("SUPPLY-ZONE reentry -> SHORT",rz_sup,-1)
    print("  => tradeable only if OB-polarity asym robustly>0 across ALL partitions (not era-trend).")
if __name__=="__main__": main()
