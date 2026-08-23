"""frontier_u.py — FRONTIER U: SEQUENCE GRAMMAR (conditional transition probabilities). Distinct from N (linear
autocorrelation): does any short bar-direction PATTERN (3-gram of up/down bars) predict the next bar's direction in a
cross-era-stable way? Nonlinear / pattern-conditional. Info-first scan (existence, not fitting): report P(next up |
3-gram) per era; flag any 3-gram that is cross-era-stable materially off 0.5. Causal, cross-era. Preregistered.
"""
import numpy as np, pandas as pd, bscreen as bs
from itertools import product

def main():
    print("Frontier U SEQUENCE GRAMMAR: P(next bar up | last-3 up/down pattern), per era. cross-era-stable off 0.5?")
    eras=bs.build_eras()
    grams=["".join(p) for p in product("UD",repeat=3)]
    print(f"  {'3-gram':>7} | " + "  ".join(f"{t:>12}" for t,_,_ in eras) + "  | cross-era")
    tab={g:[] for g in grams}
    for tag,fr,mask in eras:
        c=fr["close"].to_numpy(); idx=np.where(mask)[0]; i0,i1=idx.min(),idx.max(); c2=c[i0:i1+1]
        up=(np.diff(c2)>0).astype(int)  # up-bar sequence (len N-1)
        # 3-gram at position t = up[t-3..t-1], predict up[t]
        for g in grams:
            pat=np.array([1 if ch=="U" else 0 for ch in g])
            m=(up[0:-3]==pat[0])&(up[1:-2]==pat[1])&(up[2:-1]==pat[2])
            nxt=up[3:]
            if m.sum()<200: tab[g].append(None); continue
            tab[g].append(float(nxt[m].mean()))
    for g in grams:
        vals=tab[g]; cells=[f"{v:.3f}" if v is not None else "thin" for v in vals]
        vv=[v for v in vals if v is not None]
        st="STABLE>0.5" if (len(vv)>=3 and all(v>=0.53 for v in vv)) else ("STABLE<0.5" if (len(vv)>=3 and all(v<=0.47 for v in vv)) else "-")
        print(f"  {g:>7} | " + "  ".join(f"{x:>12}" for x in cells) + f"  | {st}")

if __name__=="__main__":
    main()
