"""bfsd2_observe.py — BLIND_FORWARD_STRUCTURE_DISCOVERY_V1 engine v2, OPEN-ENDED / PRIMITIVE-AGNOSTIC observation (CEO correction
2026-08-24: do NOT impose FVG/OB/sweep/zone-reaction; observe what is ACTUALLY forming, let morphology emerge). This file records,
for every candle T (causal, bars<=T only; NO future, NO outcome), a primitive-agnostic STRUCTURAL SYMBOL describing 'what is forming'
plus the CANONICAL N1/N2 state (from n_cache.npz). A vectorized causal feature == the candle-by-candle walk (pure fn of bars<=T,
zero future leak) — this is NOT future-return labeling (no outcome is touched here). Morphologies emerge later (bfsd2_mine.py) as
recurring symbol SEQUENCES; outcomes are estimated only afterward.

Agnostic symbol per candle = MOM | EXP | EVENT :
  MOM   (4-bar return / ATR):  SU(>1) U(.3..1) F(-.3..3) D(-1..-.3) SD(<-1)
  EXP   (ATR/ATR_ma):          X(>1.2 expansion) N(0.8..1.2) C(<0.8 compression)
  EVENT (vs prior-20 extreme): BOH close>prior20H (acceptance up) | BOL close<prior20L | SWH wick>prior20H & close back (sweep/rej)
                               | SWL wick<prior20L & close back | .. none
Canonical context (n_cache): N1 regime direction label, N1 vol label, N2 bias direction. Output: bfsd2_stream.npz."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy()
    atr=m["atr"].to_numpy(); atr_ma=m["atr_ma"].to_numpy(); n=len(m)
    # --- causal agnostic features (all use bars <= T) ---
    c4=np.full(n,np.nan); c4[4:]=c[4:]-c[:-4]
    mom=np.where(atr>0, c4/atr, 0.0)
    def mom_sym(x):
        return "SU" if x>1 else ("U" if x>0.3 else ("SD" if x<-1 else ("D" if x<-0.3 else "F")))
    prior20H=pd.Series(h).rolling(20).max().shift(1).to_numpy()  # prior-20 high, excludes T
    prior20L=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    exp=np.where(atr_ma>0, atr/atr_ma, 1.0)
    sym=np.empty(n,object)
    for T in range(n):
        if not np.isfinite(atr[T]) or atr[T]<=0 or not np.isfinite(prior20H[T]):
            sym[T]="na"; continue
        ms=mom_sym(mom[T]); es="X" if exp[T]>1.2 else ("C" if exp[T]<0.8 else "N")
        pH=prior20H[T]; pL=prior20L[T]
        if c[T]>pH: ev="BOH"
        elif c[T]<pL: ev="BOL"
        elif h[T]>pH and c[T]<=pH: ev="SWH"
        elif l[T]<pL and c[T]>=pL: ev="SWL"
        else: ev=".."
        sym[T]=f"{ms}|{es}|{ev}"
    # --- canonical N1/N2 from cache (present per N1_N6_PRESENCE_REPORT) ---
    try:
        z=np.load(r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\n_cache.npz",allow_pickle=True)
        n1dir=z["dire"].astype(str); n1vol=z["vol"].astype(str); n2bias=z["bdir"].astype(str)
        cache_ok=True
    except Exception as e:
        n1dir=np.array(["na"]*n); n1vol=np.array(["na"]*n); n2bias=np.array(["na"]*n); cache_ok=False
        print("WARN n_cache missing:",e)
    yr=m["dt"].dt.year.to_numpy(); hr=m["dt"].dt.hour.to_numpy()
    outp=r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery\bfsd2_stream.npz"
    np.savez_compressed(outp, sym=sym.astype(str), n1dir=n1dir, n1vol=n1vol, n2bias=n2bias, yr=yr, hr=hr)
    from collections import Counter
    valid=[s for s in sym if s!="na"]
    print(f"bfsd2_observe: n={n} valid_symbols={len(valid)} distinct={len(set(valid))} cache_ok={cache_ok}")
    print("  top symbols:",Counter(valid).most_common(12))
    print("  N1 dir dist:",dict(Counter(n1dir[300::300])))
    print(f"  wrote {outp} (NO outcome computed — emergence+outcomes in bfsd2_mine.py)")
if __name__=="__main__": main()
