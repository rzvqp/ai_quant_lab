"""STAT-CRS1-INDEPENDENT-REVIEW-FDR-001 -- run 1.
Independent reproduction of frozen CRS-1 + the two causality audits.
PREREGISTERED BEFORE SCORING (see PREREG block below). Read-only; CRS-1 is not modified.
"""
from __future__ import annotations
import sys, os, json, hashlib
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\crs"
sys.path.insert(0, AD); os.chdir(AD)
import cur_data as CD, swing_base as sb, sig_build as SB
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

PREREG = """
PREREGISTERED CAUSAL CONSTRUCTIONS (declared before any scoring; exactly two, no fishing):

  C1  LABEL-ALIGNMENT-CAUSAL:  keep the frozen mu/sd/centroid/threshold EXACTLY as frozen, and change ONLY
      the temporal alignment of the label to an M15 bar -- from 'floor to this bar's own H4 bucket start'
      to merge_asof-backward on H4 close_time (the identical rule the frozen spec already uses for its H4
      trend gate). This isolates the intra-bar alignment defect from the normalization question.

  C2  CAUSAL-FREEZE-2021: rebuild the ENTIRE signature using ONLY H4 bars with dt <= 2021-12-31 --
      mu/sd from that period, centroid = median z of its LAST 90 days, threshold = 12th pct of its
      non-current distance distribution -- then label all bars with those constants and score CRS-1 on
      2022-01-01 .. 2026-07-27 ONLY. This is the pipeline a researcher standing at 2021-12-31 could
      actually have frozen and deployed; everything after is out-of-sample for the whole construction.
      Cutoff 2021-12-31 is the lab's OWN pre-existing DISCOVERY/CONFIRMATION boundary, not chosen by me.

  Both use label-alignment C1 (causal) so the normalization question is tested cleanly.
  No other normalization will be scored. Whatever these produce is what I report.
"""
print(PREREG)

m = CD.load_m15()
h4 = CD.agg(m, "H4")
print(f"  M15 bars={len(m)}  H4 bars={len(h4)}  span {h4['dt'].min()} .. {h4['dt'].max()}")
with open(CD.MKT, "rb") as f:
    dh = hashlib.sha256(f.read()).hexdigest()
print(f"  data sha256 {dh[:16]}  (spec claims 57f4ed9544993c8f)  MATCH={dh.startswith('57f4ed9544993c8f')}")

# ---------------------------------------------------------------- reproduction of the frozen candidate
h4d = h4_up_map(m); atr = m["atr"].to_numpy(); n = len(m)
ev = (h4d == 0) & np.isfinite(atr) & (atr > 0)
idx = np.where(np.nan_to_num(ev.astype(float), nan=0).astype(bool))[0]; idx = idx[idx < n - 1]
dd = sb.dedup_events(idx, 16); idx = idx[np.isin(idx, dd)]
sl = 1.5 * atr[idx]
tr_all = sb.simulate(m, idx, -1, sl, rr=2.0, horizon=96, scenario="STRESS")
te = tr_all["t_entry"].to_numpy()
lab_frozen = like_at(te)
tr = tr_all[lab_frozen]
r = tr["R"].to_numpy()
yr = pd.Series(pd.to_datetime(tr["t_entry"], unit="s", utc=True)).dt.year.to_numpy()


def M(rr_, lab=""):
    if len(rr_) == 0: return dict(N=0)
    nn = len(rr_); w = rr_[rr_ > 0]; l = rr_[rr_ < 0]
    eq = np.cumsum(rr_)
    def brem(f):
        k = min(int(np.ceil(nn * f)), nn - 1); return float(np.sort(rr_)[:nn - k].mean())
    return dict(N=nn, avgR=float(rr_.mean()), medR=float(np.median(rr_)), WR=float((rr_ > 0).mean()),
                PF=float(w.sum() / -l.sum()) if len(l) else np.inf,
                maxDD=float((eq - np.maximum.accumulate(eq)).min()), maxLoss=float(rr_.min()),
                best1=brem(0.01), best5=brem(0.05), best10=brem(0.10))


print("\n" + "=" * 92)
print("  SECTION 3 -- INDEPENDENT REPRODUCTION OF THE FROZEN CANDIDATE")
print("=" * 92)
mm = M(r)
claims = dict(N=298, avgR=0.4507, PF=1.87, WR=0.507, best10=0.286)
for k, v in claims.items():
    got = mm[k]
    ok = "MATCH" if abs(got - v) <= max(0.006, abs(v) * 0.02) else "DIFFER"
    print(f"    {k:8} reproduced {got:>10.4f}   claimed {v:>8}   {ok}")
print(f"    medR={mm['medR']:+.4f} maxDD={mm['maxDD']:.2f}R maxLoss={mm['maxLoss']:.3f}R best1={mm['best1']:+.4f}")
d_ = r[yr <= 2021]; c_ = r[(yr >= 2022) & (yr <= 2024)]; o_ = r[yr >= 2025]
print(f"    DISC<=2021 N={len(d_):3d} avgR={d_.mean():+.4f} (claim +0.425 n193)")
print(f"    CONF 22-24 N={len(c_):3d} avgR={c_.mean():+.4f} (claim +0.367 n35)")
print(f"    OOS  25-26 N={len(o_):3d} avgR={o_.mean():+.4f} (claim +0.565 n70)")
py = {int(y): (round(float(r[yr == y].mean()), 3), int((yr == y).sum())) for y in sorted(set(yr))}
print(f"    per-year: {py}")
print(f"    years positive: {sum(1 for v in py.values() if v[0] > 0)}/{len(py)}  (claim 13/14)")

# ---------------------------------------------------------------- CAUSALITY AUDIT 1: label alignment
print("\n" + "=" * 92)
print("  SECTION 2a -- CAUSALITY AUDIT: TEMPORAL ALIGNMENT OF THE current-like LABEL")
print("=" * 92)
print("  cur_screen.like_at:  h4_bucket = (m15_time // 14400) * 14400   -> the bar's OWN, still-forming H4 bucket")
print("  cur_cr13_trade.h4_up_map: merge_asof(m15_time, h4.close_time, backward) -> the last CLOSED H4 bar")
print("  The two activation gates of the SAME strategy use DIFFERENT temporal conventions.")
bucket_start = (te // 14400) * 14400
lead = te - bucket_start
print(f"\n    entry time minus its label-bucket START: min={lead.min()/60:.0f}min  median={np.median(lead)/60:.0f}min  max={lead.max()/60:.0f}min")
h4_close = h4["close_time"].to_numpy().astype(np.int64)
h4_start = h4["time"].to_numpy().astype(np.int64)
cmap = dict(zip(h4_start, h4_close))
bclose = np.array([cmap.get(int(b), b) for b in bucket_start])
not_closed = te < bclose
print(f"    trades whose label bucket had NOT yet closed at entry: {int(not_closed.sum())} / {len(te)} = {not_closed.mean():.1%}")
print(f"    lookahead among those: median={np.median((bclose-te)[not_closed])/60:.0f}min  max={(bclose-te)[not_closed].max()/60:.0f}min")

# C1: causal alignment, frozen constants unchanged
lk = pd.read_parquet("__cur_cache__/current_like_h4.parquet")
lkm = pd.DataFrame({"close_time": [cmap.get(int(t), int(t)) for t in lk["time"].to_numpy()],
                    "like": lk["like"].to_numpy()}).sort_values("close_time")
mm_ = pd.DataFrame({"time": te}).sort_values("time")
j = pd.merge_asof(mm_, lkm, left_on="time", right_on="close_time", direction="backward").sort_index()
lab_c1 = j["like"].fillna(False).to_numpy().astype(bool)
print(f"\n    C1 (frozen constants, CAUSAL alignment): labels differ on {int((lab_c1 != lab_frozen).sum())} of {len(te)} candidate entries")
tr1 = tr_all[lab_c1]; r1 = tr1["R"].to_numpy()
yr1 = pd.Series(pd.to_datetime(tr1["t_entry"], unit="s", utc=True)).dt.year.to_numpy()
m1 = M(r1)
print(f"    C1 RESULT: N={m1['N']} avgR={m1['avgR']:+.4f} PF={m1['PF']:.2f} WR={m1['WR']:.3f} best10={m1['best10']:+.4f}")
print(f"       DISC={r1[yr1<=2021].mean():+.4f}(n{(yr1<=2021).sum()}) CONF={r1[(yr1>=2022)&(yr1<=2024)].mean():+.4f}"
      f"(n{((yr1>=2022)&(yr1<=2024)).sum()}) OOS={r1[yr1>=2025].mean():+.4f}(n{(yr1>=2025).sum()})")
print(f"       vs frozen avgR {mm['avgR']:+.4f}  ->  delta {m1['avgR']-mm['avgR']:+.4f}")

# ---------------------------------------------------------------- C2: causal freeze 2021
print("\n" + "=" * 92)
print("  SECTION 4 -- C2 CAUSAL-FREEZE-2021 (whole signature rebuilt on <=2021 only)")
print("=" * 92)
X, ok = SB.descriptors(h4)
dt = h4["dt"]
pre = (dt <= pd.Timestamp("2021-12-31", tz="UTC")).to_numpy() & ok
mu2 = np.nanmean(X[pre], 0); sd2 = np.nanstd(X[pre], 0) + 1e-12
Z2 = (X - mu2) / sd2
last90 = (dt > (pd.Timestamp("2021-12-31", tz="UTC") - pd.Timedelta(days=90))).to_numpy() & pre
cent2 = np.nanmedian(Z2[last90], 0)
dist2 = np.sqrt(((Z2 - cent2) ** 2).sum(1)); dist2[~ok] = np.inf
thr2 = np.nanpercentile(dist2[pre & ~last90], SB.PCTL)
like2 = ok & (dist2 <= thr2)
print(f"    mu(<=2021)={np.round(mu2,5).tolist()}")
print(f"    centroid z (2021 last-90d)={np.round(cent2,2).tolist()}   threshold p{SB.PCTL}={thr2:.3f}")
print(f"    current-like bars under C2: {int(like2.sum())} ({100*like2.mean():.1f}%)  vs frozen {int(lk['like'].sum())} ({100*lk['like'].mean():.1f}%)")
inter = int((like2 & lk["like"].to_numpy()).sum()); union = int((like2 | lk["like"].to_numpy()).sum())
print(f"    Jaccard(C2, frozen) = {inter/union:.4f}   (Red Team claims 0.883-0.890 for its own causal variant)")
lk2 = pd.DataFrame({"close_time": h4_close, "like": like2}).sort_values("close_time")
j2 = pd.merge_asof(mm_, lk2, left_on="time", right_on="close_time", direction="backward").sort_index()
lab_c2 = j2["like"].fillna(False).to_numpy().astype(bool)
post = pd.Series(pd.to_datetime(te, unit="s", utc=True)).dt.year.to_numpy() >= 2022
tr2 = tr_all[lab_c2 & post]; r2 = tr2["R"].to_numpy()
yr2 = pd.Series(pd.to_datetime(tr2["t_entry"], unit="s", utc=True)).dt.year.to_numpy()
m2 = M(r2)
print(f"\n    C2 SCORED ONLY ON 2022-01-01..2026-07 (fully out-of-sample for the whole construction):")
print(f"      N={m2['N']} avgR={m2['avgR']:+.4f} PF={m2['PF']:.2f} WR={m2['WR']:.3f} best10={m2['best10']:+.4f} maxDD={m2['maxDD']:.2f}")
print(f"      per-year: { {int(y): (round(float(r2[yr2==y].mean()),3), int((yr2==y).sum())) for y in sorted(set(yr2))} }")
print(f"      2022-24 = {r2[yr2<=2024].mean():+.4f} (n{(yr2<=2024).sum()})   2025-26 = {r2[yr2>=2025].mean():+.4f} (n{(yr2>=2025).sum()})")

json.dump(dict(frozen=mm, c1=m1, c2=m2,
               not_closed_frac=float(not_closed.mean()),
               jaccard_c2=inter / union,
               per_year_frozen={str(k): v for k, v in py.items()}),
          open(os.path.join(OUT, "run1.json"), "w"), indent=1, default=str)
np.save(os.path.join(OUT, "r_frozen.npy"), r)
np.save(os.path.join(OUT, "yr_frozen.npy"), yr)
np.save(os.path.join(OUT, "te_frozen.npy"), te[lab_frozen])
np.save(os.path.join(OUT, "idx_frozen.npy"), tr["i"].to_numpy() if "i" in tr.columns else np.arange(len(r)))
print("\n  persisted run1 artifacts")
