"""Cross-population validation of the STABLE path-history SHORT signals (clean_up, shallowPB_up) on b0/b1 H1.
Decisive test: does the 'clean advance near recent highs -> SHORT exhaustion' lift generalize beyond 2021-2023?
Causal, price-only. Uses hist_data H1 (features computed per-block to avoid cross-gap contamination)."""
import numpy as np, pandas as pd
import hist_data as hd
from state_validate import passage, P
W=24
def feats(df):
    c=df["close"].to_numpy(); h=df["high"].to_numpy(); l=df["low"].to_numpy(); atr=df["atr"].to_numpy()
    rhh=pd.Series(h).rolling(W).max().to_numpy(); cW=pd.Series(c).shift(W).to_numpy()
    pathlen=pd.Series(np.abs(np.diff(c,prepend=c[0]))).rolling(W).sum().to_numpy()
    reff=np.where(pathlen>0,(c-cW)/pathlen,0.0); pb=(rhh-c)/atr
    return reff,pb
def main():
    h1=hd.load()["H1"]
    print("PATH-HISTORY SHORT signals cross-population (b0 2011-2013, b1 2016-2018 H1). P(+100/-70) H48.")
    for blk in ("is_b0","is_b1"):
        sub=h1[h1[blk]].reset_index(drop=True)
        reff,pb=feats(sub); up,dn=passage(sub); n=len(sub); m=np.ones(n,bool)
        clean=(reff>0.5); shallow=(reff>0.3)&(pb<0.5)
        for nm,cond in (("clean_up",clean),("shallowPB_up",shallow)):
            cond=np.nan_to_num(cond.astype(float),nan=0).astype(bool)
            bS,_=P(up,dn,100,70,'S',48,m); cS,nc=P(up,dn,100,70,'S',48,cond)
            bL,_=P(up,dn,100,70,'L',48,m); cL,_=P(up,dn,100,70,'L',48,cond)
            print(f"  {blk[3:]} {nm}: SHORT base={bS:.3f} cond={cS:.3f} lift={cS-bS:+.3f}(n{nc}) | LONG base={bL:.3f} cond={cL:.3f} lift={cL-bL:+.3f}")
if __name__=="__main__":
    main()
