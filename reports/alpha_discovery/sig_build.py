"""sig_build.py — Phase 1 (freeze CURRENT_XAUUSD_MARKET_SIGNATURE_V1) + Phase 2 (CURRENT_LIKE_POPULATION_V1).
Mechanical, causal, price-normalized H4 descriptors; NO P&L / no future return in the signature. Current window =
latest 90 days. Signature = median z-vector of the current window (frozen). Current-like = historical H4 bars within a
distance threshold of that centroid (structural similarity, NOT calendar). Reports the year-distribution to verify the
population is not merely recent. Fingerprints the definition. Read-only on the ratified current M15 CSV.
"""
import os, hashlib, numpy as np, pandas as pd
import cur_data as CD
DESC=["vol_norm","vol_rel","effic","ddfh","ret60"]
CUR_DAYS=90; PCTL=12.0  # current-like = distance <= 12th percentile

def descriptors(h4):
    c=h4["close"].to_numpy(); atr=h4["atr"].to_numpy(); atrm=h4["atr_ma"].to_numpy()
    vol_norm=atr/c; vol_rel=atr/atrm; effic=h4["effic"].to_numpy()
    ddfh=(c-pd.Series(h4["high"].to_numpy()).rolling(120).max().shift(1).to_numpy())/c
    ret60=(c-pd.Series(c).shift(60).to_numpy())/c
    X=np.column_stack([vol_norm,vol_rel,effic,ddfh,ret60]); ok=np.isfinite(X).all(1)
    return X, ok

def main():
    m=CD.load_m15(); h4=CD.agg(m,"H4")
    with open(CD.MKT,"rb") as f: dh=hashlib.sha256(f.read()).hexdigest()[:16]
    X,ok=descriptors(h4); dt=h4["dt"]
    mu=np.nanmean(X[ok],0); sd=np.nanstd(X[ok],0)+1e-12; Z=(X-mu)/sd
    curmask=(dt>=(dt.max()-pd.Timedelta(days=CUR_DAYS))).to_numpy()&ok
    centroid=np.nanmedian(Z[curmask],0)
    dist=np.sqrt(((Z-centroid)**2).sum(1)); dist[~ok]=np.inf
    thr=np.nanpercentile(dist[ok&~curmask],PCTL)   # threshold from NON-current history
    like=ok&(dist<=thr)
    yrs=dt.dt.year.to_numpy()
    print(f"=== CURRENT_XAUUSD_MARKET_SIGNATURE_V1 (H4, {len(h4)} bars, dataHash {dh}) ===")
    print(f"current window = last {CUR_DAYS}d (n_H4={int(curmask.sum())}), latest={dt.max()}")
    raw=np.nanmedian(X[curmask],0)
    print("SIGNATURE centroid (raw medians):", {DESC[i]:round(float(raw[i]),4) for i in range(len(DESC))})
    print("SIGNATURE centroid (z):", {DESC[i]:round(float(centroid[i]),2) for i in range(len(DESC))})
    print(f"norm mu={np.round(mu,4).tolist()} sd={np.round(sd,4).tolist()}")
    print(f"\n=== CURRENT_LIKE_POPULATION_V1 (dist<= p{PCTL}={thr:.2f}) ===")
    print(f"current-like H4 bars: {int(like.sum())} ({100*like.mean():.1f}% of history)")
    from collections import Counter; yc=Counter(yrs[like])
    print("by year:", {int(y):yc[y] for y in sorted(yc)})
    # compare: what fraction of each year is current-like (structural, not calendar)
    print("frac of each year that is current-like:")
    for y in range(2011,2027):
        yy=(yrs==y)&ok
        if yy.sum()<50: continue
        print(f"   {y}: {100*np.mean(like[yy]):.0f}%", end="  ")
    print()
    # save the frozen population mask (H4 time boundaries) for downstream re-screen
    out=pd.DataFrame({"time":h4["time"].to_numpy(),"dt":dt.to_numpy(),"like":like,"dist":dist})
    out.to_parquet(os.path.join(CD._HERE if hasattr(CD,'_HERE') else os.path.dirname(os.path.abspath(__file__)),"__cur_cache__.parquet")) if False else None
    os.makedirs("__cur_cache__",exist_ok=True); out.to_parquet("__cur_cache__/current_like_h4.parquet")
    print("saved __cur_cache__/current_like_h4.parquet")
    fp=hashlib.sha256((str(DESC)+str(np.round(centroid,3).tolist())+str(round(thr,2))+str(CUR_DAYS)+dh).encode()).hexdigest()[:16]
    print(f"SIGNATURE_FINGERPRINT={fp}")

if __name__=="__main__":
    main()
