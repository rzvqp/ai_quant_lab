"""L1 — corectie de multiplicitate la nivel de gramatica. Re-ruleaza tot ecranul capturand statistici-t."""
import os, sys, math, json, time
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AA = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation"
sys.path.insert(0, os.path.join(AA, "code"))
import mstrat, mstrat_ext as ME
from alpha_lab import CFG
mstrat.TICK = 0.01
if hasattr(ME, "TICK"): ME.TICK = 0.01
def cfg_for(rt):
    c = dict(CFG); c["spread_ticks"] = rt / (2 * mstrat.TICK); c["slip_ticks"] = 0.0; return c
CB = cfg_for(0.05)
d = mstrat.load()
T = d["time"].to_numpy()
mon = (pd.to_datetime(T, unit="s", utc=True).year * 12 + pd.to_datetime(T, unit="s", utc=True).month).to_numpy()

def clustered_t(r, cl):
    """t pentru media R, cu SE clusterizat pe luna calendaristica (conservator)."""
    n = len(r); mu = r.mean()
    g = pd.DataFrame({"c": cl, "r": r}).groupby("c")["r"].agg(["sum", "count"])
    G = len(g)
    resid = g["sum"].to_numpy() - g["count"].to_numpy() * mu
    se = math.sqrt(max((resid ** 2).sum() / n ** 2 * (G / max(G - 1, 1)), 1e-18))
    return mu, se, (mu / se if se > 0 else 0.0), G

mods = {}
for N in range(1, 52):
    for mod in (mstrat, ME):
        if getattr(mod, f"s{N}_grammar", None) and getattr(mod, f"s{N}_setups", None):
            mods[N] = mod; break
rows = []; t0 = time.time()
for N in sorted(mods):
    mod = mods[N]; gram = getattr(mod, f"s{N}_grammar")(); sfn = getattr(mod, f"s{N}_setups")
    for h in gram:
        try: su = sfn(d, h)
        except Exception: continue
        if not su or len(su) < 100: continue
        try: tb = mstrat.simulate(d, su, CB)
        except Exception: continue
        if len(tb) < 100: continue
        r = tb.R.to_numpy(); ei = tb.ei.to_numpy()
        mu, se, t, G = clustered_t(r, mon[ei])
        rows.append(dict(hid=f"S{N}::{h['id']}", family=f"S{N}", id=h["id"], N=len(r),
                         mean=mu, se=se, t=t, clusters=G, sd=float(r.std(ddof=1))))
R = pd.DataFrame(rows)
print(f"  scorate {len(R)} configuratii in {time.time()-t0:.0f}s")
from statistics import NormalDist
ND = NormalDist()
R["p_one"] = R.t.apply(lambda x: 1 - ND.cdf(x))          # test unilateral: media R > 0
R["p_two"] = R.t.apply(lambda x: 2 * (1 - ND.cdf(abs(x))))
R.to_csv("fwer_all.csv", index=False)

a = pd.read_csv(os.path.join(AA, "reports", "alpha_discovery", "GOV_SCREEN_ALL_RESULTS.csv"))
a["id"] = a.hid.str.extract(r"id=([0-9a-f]+)")
M = R.merge(a[["id", "BASE", "SURVIVE"]], on="id", how="left")
print(f"  verificare incrucisata cu ALL_RESULTS: media |BASE_alpha - mean_meu| = {np.nanmean(np.abs(M.BASE - M['mean'])):.6f}")

# m efectiv = semnaturi distincte
sig = a[["family", "N", "WR", "BASE", "STRESS", "PF", "maxDD", "db5"]].astype(str).agg("|".join, axis=1)
m_eff = sig.nunique()
print("\n" + "=" * 112); print("  L1 — CORECTIE DE MULTIPLICITATE"); print("=" * 112)
print(f"  ipoteze testate (config cu >=100 tranzactii) : {len(R)}")
print(f"  ipoteze DISTINCTE (duplicate exacte inlaturate): {m_eff}")
for m, nm in ((len(R), "toate configuratiile"), (m_eff, "doar cele distincte")):
    zb = ND.inv_cdf(1 - 0.05 / m)
    print(f"  Bonferroni FWER 5% la m={m:5d} ({nm}): necesita t > {zb:.2f}")
# BH-FDR
p = np.sort(R.p_one.to_numpy()); mtot = len(p)
crit = np.arange(1, mtot + 1) / mtot * 0.05
k = np.where(p <= crit)[0]
thr = p[k.max()] if len(k) else 0.0
print(f"  BH-FDR q=0.05 pe toate cele {mtot}: praguri satisfacute de {len(k)} ipoteze; p-prag = {thr:.3e}")
print(f"  (adica t > {ND.inv_cdf(1-thr):.2f} daca thr>0)" if thr > 0 else "  (nicio ipoteza nu trece BH)")

print("\n  CANDIDATII:")
zb_all = ND.inv_cdf(1 - 0.05 / len(R)); zb_eff = ND.inv_cdf(1 - 0.05 / m_eff)
for hid in ("85dfa65a9ce1", "047d776a1bcb", "601e20753a4a"):
    row = R[R.id == hid]
    if not len(row): print(f"    {hid}: ABSENT"); continue
    x = row.iloc[0]
    bh = "TRECE" if x.p_one <= thr else "PICA"
    print(f"    {x.hid:14} N={int(x.N):4d} mean={x['mean']:+.4f} se_clust={x.se:.4f} t={x.t:+.2f} "
          f"p1={x.p_one:.2e} | Bonf(m={m_eff}) t>{zb_eff:.2f} -> {'TRECE' if x.t>zb_eff else 'PICA'} | BH-FDR -> {bh}")
print(f"\n  rang t in gramatica (din {len(R)}):")
R2 = R.sort_values("t", ascending=False).reset_index(drop=True)
for hid in ("85dfa65a9ce1", "047d776a1bcb", "601e20753a4a"):
    i = R2.index[R2.id == hid]
    if len(i): print(f"    {hid}: rangul {int(i[0])+1} dupa t  (t={R2.loc[i[0],'t']:+.2f})")
print(f"  top-5 t din toata gramatica: {R2.head(5)[['hid','N','mean','t']].to_string(index=False)}")
