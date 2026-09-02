"""m5_regime.py — §23/§24 ONE transparent regime test on E.LONG (near-positive, info-bearing). Prospectively-observable uptrend regime
(causal EMA200: close>ema200). Does E.LONG-in-uptrend beat unconditional LONG-BETA in the same regime, in BOTH DEV and OOS? If it only
beats beta in OOS / is DEV-negative -> not robust (directional beta). Time exit (best for E.LONG). No grid, no mining.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery")
import m5_core as MC, m5_families as MF

def add_ema(M):
    c=M["c"]; M["ema200"]=pd.Series(c).ewm(span=200,adjust=False).mean().shift(1).to_numpy(); return M

def beta_long(M, ref_stops):
    """Unconditional LONG entries in uptrend, matched stop distribution (sampled from E.LONG risks), time exit."""
    c=M["c"];ema=M["ema200"];atr=M["atr"];n=M["n"]; rng=np.random.RandomState(3); out=[]; last=-99
    for i in range(210,n-100,7):
        if i-last<6 or not (np.isfinite(ema[i]) and np.isfinite(atr[i]) and atr[i]>0): continue
        if c[i]<=ema[i]: continue
        stop=c[i]-rng.choice(ref_stops); out.append((i+1,+1,stop)); last=i
    return out

def ev(M,trades,mode="time"):
    rows=[]
    for k,side,stop in trades:
        r=MC.resolve(M,k,side,stop,mode)
        if r is None: continue
        r["yr"]=M["yr"][min(k,M["n"]-1)]; r["kk"]=k; rows.append(r)
    return rows

def rep(M,rows,label):
    if len(rows)<30: print(f"{label:28s} N={len(rows)} small"); return None
    net=np.array([r["net"] for r in rows]); g=np.array([r["g"] for r in rows]); k=np.array([r["kk"] for r in rows]); yr=np.array([r["yr"] for r in rows])
    ky=M["t"][np.clip(k,0,M["n"]-1)]; dev=ky<1719792000; ie=len(MC.dedup_episodes(k))
    yrs=" ".join(f"{y}:{net[yr==y].mean():+.2f}" for y in sorted(set(yr.tolist())))
    print(f"{label:28s} N={len(net):4d} ie={ie:4d} net={net.mean():+.3f} WR={(g>0).mean():.3f} DEV={net[dev].mean():+.3f} OOS={net[~dev].mean():+.3f} | {yrs}")
    return net.mean()

def main():
    M=add_ema(MC.load())
    E=MF.famE(M)
    Elong=[t for t in E if t[1]>0]
    # split E.LONG by regime at entry
    up=[]; dn=[]
    for k,side,stop in Elong:
        kk=min(k,M["n"]-1)
        if not np.isfinite(M["ema200"][kk]): continue
        (up if M["c"][kk]>M["ema200"][kk] else dn).append((k,side,stop))
    print("=== E.LONG by causal uptrend regime (close>EMA200), time exit ===")
    rep(M,ev(M,Elong),"E.LONG.all")
    up_rows=ev(M,up); rep(M,up_rows,"E.LONG.UPTREND")
    rep(M,ev(M,dn),"E.LONG.DOWNTREND")
    # long-beta control in uptrend, matched stops
    ref=np.array([abs(M["c"][min(k,M["n"]-1)]-stop) for k,s,stop in up]); ref=ref[ref>0]
    print("=== matched LONG-BETA control in uptrend ===")
    beta_rows=ev(M,beta_long(M,ref)); bmean=rep(M,beta_rows,"BETA.LONG.UPTREND")
    emean=np.mean([r["net"] for r in up_rows]) if up_rows else float('nan')
    print(f"\nE.LONG.UPTREND {emean:+.3f} vs BETA.LONG.UPTREND {bmean:+.3f} -> E-minus-beta {emean-bmean:+.3f}")
    print("VERDICT: survives only if E.LONG.UPTREND is positive in BOTH DEV and OOS AND beats beta in both.")

if __name__=="__main__":
    main()
