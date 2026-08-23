"""STAT-CRS1 run 3 -- multiple-testing / FDR under the lab's ratified protocol, plus temporal robustness."""
from __future__ import annotations
import sys, os, math, json
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\crs"
sys.path.insert(0, AD); os.chdir(AD)
import cur_data as CD, swing_base as sb
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

m = CD.load_m15(); h4 = CD.agg(m, "H4")
cmap = dict(zip(h4["time"].to_numpy().astype(np.int64), h4["close_time"].to_numpy().astype(np.int64)))
lk = pd.read_parquet("__cur_cache__/current_like_h4.parquet")
lkm = pd.DataFrame({"close_time": [cmap.get(int(t), int(t)) for t in lk["time"].to_numpy()],
                    "like": lk["like"].to_numpy()}).sort_values("close_time")
h4d = h4_up_map(m); atr = m["atr"].to_numpy(); n = len(m)
ev = (h4d == 0) & np.isfinite(atr) & (atr > 0)
idx = np.where(np.nan_to_num(ev.astype(float), nan=0).astype(bool))[0]; idx = idx[idx < n - 1]
idx = idx[np.isin(idx, sb.dedup_events(idx, 16))]
tr = sb.simulate(m, idx, -1, 1.5 * atr[idx], rr=2.0, horizon=96, scenario="STRESS")
te = tr["t_entry"].to_numpy(); R = tr["R"].to_numpy()
fr = like_at(te)
j = pd.merge_asof(pd.DataFrame({"time": te}).sort_values("time"), lkm,
                  left_on="time", right_on="close_time", direction="backward").sort_index()
c1 = j["like"].fillna(False).to_numpy().astype(bool)


def ncdf(z): return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def cluster_p(r, t, gap_h4=4):
    """one-sided p for mean>0 with episode-clustered SE (episode = >gap_h4 H4 bars apart)."""
    o = np.argsort(t); r = r[o]; t = t[o]
    gaps = np.diff(t) / 900.0
    ep = np.concatenate([[0], np.cumsum(gaps > gap_h4 * 4)])
    sums = np.array([r[ep == e].sum() for e in np.unique(ep)])
    cnts = np.array([(ep == e).sum() for e in np.unique(ep)])
    G = len(sums); N = len(r)
    mu = r.mean()
    resid = sums - cnts * mu
    var = (resid ** 2).sum() / max(N ** 2, 1) * (G / max(G - 1, 1))
    se = math.sqrt(max(var, 1e-18))
    z = mu / se if se > 0 else 0.0
    return mu, se, z, 1 - ncdf(z), G


print("=" * 92)
print("  SECTION 5 -- MULTIPLE TESTING / FDR")
print("=" * 92)
print("  Family reconstruction from the lab's OWN ledgers (ALPHA_MULTIPLE_TESTING_LEDGER.md,")
print("  ALPHA_DISCOVERY_CHECKPOINTS.md, ALPHA_CURRENT_REGIME_RESCREEN_LEDGER.md):")
fam = [("named strategy families S1-S51", 51),
       ("prior program frontiers (42 hypotheses / 19 frontiers)", 42),
       ("broad-discovery v2 batches A-J + later frontiers", 60),
       ("state-path method (~50 state/transition defs x 2 sides)", 100),
       ("R-series radar hypotheses R1-R32", 32),
       ("current-regime frontiers CR-1..CR-15", 15)]
for nm, k in fam: print(f"    {nm:56} {k:4d}")
mtot = sum(k for _, k in fam)
print(f"    {'TOTAL enumerated hypothesis-level tests':56} {mtot:4d}")
print("  NOTE: CRS-1's own frozen card states it is registered as a SEPARATE multiple-testing family")
print("        from the MK/detector line, and Alpha discloses '12 negatives' immediately before it (CR-1..CR-12).")
print("        I therefore report THREE nested family definitions rather than asserting one.")

for lab_nm, L in (("FROZEN (non-causal label)", fr), ("CAUSAL C1 (alignment corrected)", c1)):
    r = R[L]; t = te[L]
    mu, se, z, p, G = cluster_p(r, t)
    print(f"\n  {lab_nm}")
    print(f"    N={len(r)}  episode-clusters G={G}  avgR={mu:+.4f}  clustered SE={se:.4f}  z={z:+.3f}")
    print(f"    RAW one-sided p = {p:.3e}")
    for fam_nm, mfam in (("CR-1..CR-15 only", 15), ("current-regime + radar (CR+R)", 47), ("full enumerated program", mtot)):
        bonf = min(1.0, p * mfam)
        # Benjamini-Hochberg: CRS-1 is the single declared survivor -> rank 1 of mfam
        bh = min(1.0, p * mfam / 1)
        print(f"      family={fam_nm:30} m={mfam:4d}  Bonferroni p={bonf:.3e}  BH q(rank1)={bh:.3e}  "
              f"{'SIGNIFICANT at 0.05' if bh < 0.05 else 'NOT significant at 0.05'}")

print("\n" + "=" * 92)
print("  SECTION 6 -- TEMPORAL ROBUSTNESS, both labels")
print("=" * 92)
for lab_nm, L in (("FROZEN", fr), ("CAUSAL C1", c1)):
    r = R[L]; yy = pd.Series(pd.to_datetime(te[L], unit="s", utc=True)).dt.year.to_numpy()
    print(f"\n  {lab_nm}: per-year avgR (n)")
    print("   ", {int(y): (round(float(r[yy == y].mean()), 3), int((yy == y).sum())) for y in sorted(set(yy))})
    pos = sum(1 for y in set(yy) if r[yy == y].mean() > 0)
    print(f"    years positive: {pos}/{len(set(yy))}")
    worst = min(((y, float(r[yy != y].mean())) for y in set(yy)), key=lambda x: x[1])
    print(f"    leave-one-year-out worst avgR = {worst[1]:+.4f} (dropping {int(worst[0])})")
    d = r[yy <= 2021]; c = r[(yy >= 2022) & (yy <= 2024)]; o = r[yy >= 2025]
    print(f"    DISC={d.mean():+.4f}(n{len(d)})  CONF={c.mean():+.4f}(n{len(c)})  OOS={o.mean():+.4f}(n{len(o)})")
    lo = min(d.mean(), c.mean(), o.mean())
    print(f"    min partition = {lo:+.4f}")

print("\n" + "=" * 92)
print("  SECTION 12 -- S5 INDEPENDENCE (entry-time structure)")
print("=" * 92)
for lab_nm, L in (("FROZEN", fr), ("CAUSAL C1", c1)):
    hh = pd.Series(pd.to_datetime(te[L], unit="s", utc=True)).dt.hour.to_numpy()
    print(f"    {lab_nm}: frac 13-14 UTC (S5 NY-open window) = {np.mean((hh >= 13) & (hh < 14)):.3f}   "
          f"frac 12-16 UTC = {np.mean((hh >= 12) & (hh < 16)):.3f}   direction=SHORT (S5 is LONG)")
print("    S5 validated population is 2023-07..2025-10 M15 NY opening-range LONG; CRS-1 is a SHORT on a")
print("    different mechanism. Trade-level overlap NOT COMPUTABLE (S5 ledger sealed in escrow_red_team).")
