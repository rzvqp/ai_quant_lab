"""INVENTORY / MEASUREMENT ONLY (no matched-null, no holdout, no parquet modification).
For every hist_prof=True hypothesis, reconstructs research-segment trades (deterministic MS.simulate)
and computes NET concentration (best/top3/top5 divided by NET sumR) alongside the existing GROSS
metrics t1/t3/t5 (best/top-k divided by GROSS profit = sum of positive R). Verifies the basis by
reproducing t1/t3/t5, then reports net-vs-gross distributions and threshold counts. Draws no conclusion."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mstrat as MS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fr = pd.read_parquet(os.path.join(ROOT, "results", "FAMILY_RESULTS.parquet"))
idmap = {}
for fam in MS.REGISTRY:
    for h in MS.REGISTRY[fam][0](): idmap[h['id']] = h

d = MS.load(); n = len(d); a = int(n*0.6); res = d.iloc[:a].copy()   # research only; holdout never loaded

hp = fr[fr.hist_prof].copy()
rows = []
for _, r in hp.iterrows():
    hid = r['id']; h = idmap[hid]
    tr = MS.simulate(res, MS.setups(res, h))
    R = np.sort(tr['R'].values)[::-1]   # descending
    nR = len(R); sumR = float(R.sum())
    gross = float(R[R > 0].sum())
    best = float(R[0]) if nR else np.nan
    top3 = float(R[:3].sum()); top5 = float(R[:5].sum())
    rows.append(dict(id=hid, fam=r['fam'], n=int(nR), sumR=sumR, gross=gross, best=best, top3=top3, top5=top5,
                     # gross ratios (should match FAMILY t1/t3/t5)
                     g1=best/gross if gross>0 else np.nan, g3=top3/gross if gross>0 else np.nan, g5=top5/gross if gross>0 else np.nan,
                     # net ratios
                     net1=best/sumR if sumR>0 else np.nan, net3=top3/sumR if sumR>0 else np.nan, net5=top5/sumR if sumR>0 else np.nan,
                     t1=float(r['t1']), t3=float(r['t3']), t5=float(r['t5']),
                     exp_fr=float(r['exp']), n_fr=int(r['n']), fragile=bool(r['fragile'])))
m = pd.DataFrame(rows)

# --- BASIS VERIFICATION ---
print("=== BASIS: reconstructed research vs FAMILY_RESULTS (357 hist_prof) ===")
print("n match:", int((m['n']==m['n_fr']).sum()), "/", len(m), " | max|exp - sumR/n| =",
      float((m['exp_fr'] - m['sumR']/m['n']).abs().max()))
print("gross-ratio vs t1/t3/t5 (should ~match): max|g1-t1|=%.4f max|g3-t3|=%.4f max|g5-t5|=%.4f" % (
      (m['g1']-m['t1']).abs().max(), (m['g3']-m['t3']).abs().max(), (m['g5']-m['t5']).abs().max()))

# --- NET vs GROSS distribution (single best trade) ---
def q(s): return {k: round(float(np.nanquantile(s, k)),3) for k in (0.5,0.75,0.9,0.95,1.0)}
print("\n=== single-best-trade share of profit ===")
print("GROSS (t1 / g1) quantiles [p50,p75,p90,p95,max]:", q(m['g1']))
print("NET   (best/sumR)      quantiles [p50,p75,p90,p95,max]:", q(m['net1']))
print("NET/GROSS ratio (net1/g1) quantiles:", q((m['net1']/m['g1']).replace([np.inf,-np.inf],np.nan)))
print("\n=== top-3 / top-5 net share ===")
print("NET top3 (top3/sumR) quantiles:", q(m['net3']))
print("NET top5 (top5/sumR) quantiles:", q(m['net5']))
print("GROSS t5 quantiles:", q(m['t5']))

# --- THRESHOLD COUNTS ---
print("\n=== fragile=False but high NET single-trade concentration ===")
nf = m[~m['fragile']]
print("hist_prof total:", len(m), " | fragile=False:", len(nf), " | fragile=True:", int(m['fragile'].sum()))
for thr in (0.30, 0.50):
    c_all = int((m['net1']>thr).sum())
    c_nf  = int((nf['net1']>thr).sum())
    print(f"  net best/sumR > {thr:.0%}:  all hist_prof = {c_all}   | of which fragile=False = {c_nf}")
print("  (context) net top5/sumR > 50%:", int((m['net5']>0.50).sum()), " > 80%:", int((m['net5']>0.80).sum()))
print("  net best/sumR > 100% (best exceeds net -> without best the rest is net-negative):", int((m['net1']>1.0).sum()))

# survivor row for reference
sv = m[m['id']=='ce76669a3b2a'].iloc[0]
print(f"\nsurvivor ce76669a3b2a: net1={sv['net1']:.3f} (g1/t1={sv['g1']:.3f}) net5={sv['net5']:.3f} t5={sv['t5']:.3f} fragile={sv['fragile']}")
m.to_parquet(os.path.join(ROOT, "results", "matched_null_validation", "net_concentration_inventory.parquet"))
print("\nwrote results/matched_null_validation/net_concentration_inventory.parquet")
