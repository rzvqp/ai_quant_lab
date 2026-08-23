"""frontier_n.py — FRONTIER N: SERIAL DEPENDENCE (return autocorrelation) across horizons, cross-era. Distinct lens
(not event-based): is there a horizon k where consecutive k-bar returns are correlated (momentum>0 / reversal<0) in a
cross-era-stable way? Non-overlapping k-returns, Pearson corr, per era. Cross-era same-sign material corr = a tradeable
serial-dependence signal. Info-only, causal. M15.
"""
import numpy as np, pandas as pd, bscreen as bs
KS=[1,2,4,8,16,32,48,96,192]

def main():
    print("Frontier N SERIAL DEPENDENCE: Pearson corr(consecutive k-bar returns), per era. momentum>0 / reversal<0. cross-era stable?")
    eras=bs.build_eras()
    print(f"  {'k(bars)':>8} |  " + "  ".join(f"{t:>7}" for t,_,_ in eras) + "   | cross-era")
    for k in KS:
        row=[]; signs=[]
        for tag,fr,mask in eras:
            c=fr["close"].to_numpy(); idx=np.where(mask)[0]
            # non-overlapping k-returns within the era-contiguous region
            i0,i1=idx.min(),idx.max(); c2=c[i0:i1+1]
            if len(c2)<4*k: row.append("na"); signs.append(0); continue
            r=c2[k:]-c2[:-k]            # k-bar returns (overlapping)
            r=r[::k]                    # non-overlapping
            if len(r)<30: row.append("na"); signs.append(0); continue
            a=r[:-1]; b=r[1:]; cc=np.corrcoef(a,b)[0,1]
            row.append(f"{cc:+.3f}"); signs.append(np.sign(cc) if abs(cc)>=0.05 else 0)
        nz=[s for s in signs if s!=0]; stable="STABLE "+("MOM" if nz and nz[0]>0 else "REV") if (len(nz)>=3 and len(set(nz))==1) else "-"
        print(f"  {k:>8} |  " + "  ".join(f"{x:>7}" for x in row) + f"   | {stable}")

if __name__=="__main__":
    main()
