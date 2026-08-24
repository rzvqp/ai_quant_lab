"""m09_crossscale.py — MODULAR_DISCOVERY_V1, M09 cross-scale remaining branches: nested-align + confluence-amplify.
Price-only nested-scale trend on the M15 grid (CAUSAL — EMAs use only past bars): M15 = ema20>ema50; H1-proxy = ema80>ema200;
H4-proxy = ema320>ema800 (4x/16x nesting). nested-align UP = all 3 up; DOWN = all 3 down. INFO: forward excursion-asym when
3-scale aligned, partitioned D<=2018/C19-22/O23+. confluence-amplify (§10 incremental): does 3-scale alignment beat M15-only?
Genuine cross-scale edge only if aligned-UP AND aligned-DOWN are BOTH robustly favorable across eras (not just era-trend)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\code")
import cur_data as CD
def ema(x,span): return pd.Series(x).ewm(span=span,adjust=False).mean().to_numpy()
def main():
    m=CD.load_m15(); h=m["high"].to_numpy(); l=m["low"].to_numpy(); c=m["close"].to_numpy(); atr=m["atr"].to_numpy(); n=len(m)
    e20=m["ema20"].to_numpy(); e50=m["ema50"].to_numpy()
    e80=ema(c,80); e200=ema(c,200); e320=ema(c,320); e800=ema(c,800)
    m15_up=e20>e50; h1_up=e80>e200; h4_up=e320>e800
    fmax=pd.Series(h).rolling(96).max().shift(-96).to_numpy(); fmin=pd.Series(l).rolling(96).min().shift(-96).to_numpy()
    up=(fmax-c)/atr; dn=(c-fmin)/atr; yr=m["dt"].dt.year.to_numpy()
    warm=800  # EMA warmup
    valid=np.isfinite(up)&np.isfinite(dn)&np.isfinite(atr)&(atr>0); valid[:warm]=False
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
    align_up=m15_up&h1_up&h4_up; align_dn=(~m15_up)&(~h1_up)&(~h4_up)
    print(f"M09 nested-align: aligned-UP bars={int((align_up&valid).sum())} aligned-DOWN bars={int((align_dn&valid).sum())}")
    report("3-scale aligned-UP  -> LONG",align_up,1)
    report("3-scale aligned-DOWN-> SHORT",align_dn,-1)
    # confluence-amplify §10: M15-only vs 3-scale
    print("confluence-amplify (§10 incremental, LONG side):")
    report("  M15-only-up -> LONG",m15_up,1)
    report("  M15+H1+H4-up-> LONG",align_up,1)
    # HTF-state x LTF-event: LTF fresh 20-bar breakout FILTERED by H4-proxy trend (symmetric test)
    hi20=pd.Series(h).rolling(20).max().shift(1).to_numpy(); lo20=pd.Series(l).rolling(20).min().shift(1).to_numpy()
    ltf_up=c>hi20; ltf_dn=c<lo20   # LTF momentum event (causal: prior-20 extreme)
    print("HTF-state x LTF-event (LTF 20-bar breakout gated by H4-proxy):")
    report("  LTF-up-break & H4-up -> LONG",ltf_up&h4_up,1)
    report("  LTF-dn-break & H4-dn -> SHORT",ltf_dn&(~h4_up),-1)
    print("  => genuine cross-scale edge only if BOTH aligned sides robustly>0 across eras (else era-trend).")
if __name__=="__main__": main()
