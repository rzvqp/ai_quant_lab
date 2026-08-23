"""STAT-CRS1 run 2 -- materiality of the alignment defect, mechanism test, effective N, tail, FDR inputs."""
from __future__ import annotations
import sys, os, json
import numpy as np, pandas as pd

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
AD = r"C:\Users\MEDION GAMING\ai_quant_lab-alpha-automation\reports\alpha_discovery"
OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\crs"
sys.path.insert(0, AD); os.chdir(AD)
import cur_data as CD, swing_base as sb
from cur_screen import like_at
from cur_cr13_trade import h4_up_map

m = CD.load_m15(); h4 = CD.agg(m, "H4")
h4_close = h4["close_time"].to_numpy().astype(np.int64)
h4_start = h4["time"].to_numpy().astype(np.int64)
cmap = dict(zip(h4_start, h4_close))
lk = pd.read_parquet("__cur_cache__/current_like_h4.parquet")
lkm = pd.DataFrame({"close_time": [cmap.get(int(t), int(t)) for t in lk["time"].to_numpy()],
                    "like": lk["like"].to_numpy()}).sort_values("close_time")


def labels(te):
    frozen = like_at(te)
    mm_ = pd.DataFrame({"time": te}).sort_values("time")
    j = pd.merge_asof(mm_, lkm, left_on="time", right_on="close_time", direction="backward").sort_index()
    return frozen, j["like"].fillna(False).to_numpy().astype(bool)


def build(h4_state, stopmult=1.5, rr=2.0, dedup=16, cost="STRESS"):
    h4d = h4_up_map(m); atr = m["atr"].to_numpy(); n = len(m)
    ev = (h4d == h4_state) & np.isfinite(atr) & (atr > 0)
    idx = np.where(np.nan_to_num(ev.astype(float), nan=0).astype(bool))[0]; idx = idx[idx < n - 1]
    dd = sb.dedup_events(idx, dedup); idx = idx[np.isin(idx, dd)]
    return sb.simulate(m, idx, -1, stopmult * atr[idx], rr=rr, horizon=96, scenario=cost)


def M(r):
    if len(r) == 0: return dict(N=0, avgR=np.nan, PF=np.nan, best10=np.nan)
    nn = len(r); w = r[r > 0]; l = r[r < 0]
    def brem(f):
        k = min(int(np.ceil(nn * f)), nn - 1); return float(np.sort(r)[:nn - k].mean())
    return dict(N=nn, avgR=float(r.mean()), WR=float((r > 0).mean()),
                PF=float(w.sum() / -l.sum()) if len(l) else np.inf,
                best1=brem(0.01), best5=brem(0.05), best10=brem(0.10))


tr_all = build(0)
te = tr_all["t_entry"].to_numpy()
fr, c1 = labels(te)
R = tr_all["R"].to_numpy()

print("=" * 92)
print("  MATERIALITY OF THE ALIGNMENT DEFECT -- which trades does the leaky label add?")
print("=" * 92)
only_frozen = fr & ~c1
only_c1 = c1 & ~fr
both = fr & c1
print(f"    in BOTH labels          : n={int(both.sum()):4d}  avgR={R[both].mean():+.4f}")
print(f"    ONLY under leaky label  : n={int(only_frozen.sum()):4d}  avgR={R[only_frozen].mean():+.4f}   <- added by the lookahead")
print(f"    ONLY under causal label : n={int(only_c1.sum()):4d}  avgR={R[only_c1].mean():+.4f}")
print(f"    frozen total N={int(fr.sum())} avgR={R[fr].mean():+.4f}   causal total N={int(c1.sum())} avgR={R[c1].mean():+.4f}")
print(f"\n    The {int(only_frozen.sum())} trades visible only to the non-causal label average {R[only_frozen].mean():+.3f}R,")
print(f"    versus {R[both].mean():+.3f}R for the trades both labels agree on.")

print("\n" + "=" * 92)
print("  SECTION 11 -- MECHANISM SPECIFICITY  (A = CRS-1, B = H4-DOWN, C = outside current-like)")
print("=" * 92)
tr_dn = build(1)
te_dn = tr_dn["t_entry"].to_numpy(); fr_dn, c1_dn = labels(te_dn)
Rdn = tr_dn["R"].to_numpy()
print(f"  {'arm':46}{'label':>10}{'N':>7}{'avgR':>10}{'PF':>7}{'best10':>9}")
for lab_nm, LF, LD in (("FROZEN (non-causal)", fr, fr_dn), ("CAUSAL C1", c1, c1_dn)):
    a = M(R[LF]); b = M(Rdn[LD]); c = M(R[~LF])
    print(f"  {'A  current-like & H4-UP -> SHORT [CRS-1]':46}{lab_nm:>10}{a['N']:7d}{a['avgR']:+10.4f}{a['PF']:7.2f}{a['best10']:+9.4f}")
    print(f"  {'B  current-like & H4-DOWN -> SHORT':46}{lab_nm:>10}{b['N']:7d}{b['avgR']:+10.4f}{b['PF']:7.2f}{b['best10']:+9.4f}")
    print(f"  {'C  outside current-like & H4-UP -> SHORT':46}{lab_nm:>10}{c['N']:7d}{c['avgR']:+10.4f}{c['PF']:7.2f}{c['best10']:+9.4f}")
    print(f"    A-B spread = {a['avgR']-b['avgR']:+.4f}   A-C spread = {a['avgR']-c['avgR']:+.4f}")

print("\n" + "=" * 92)
print("  SECTION 8 -- EFFECTIVE SAMPLE SIZE")
print("=" * 92)
for nm, L in (("FROZEN", fr), ("CAUSAL C1", c1)):
    t = te[L]; idxs = np.sort(t)
    days = pd.Series(pd.to_datetime(idxs, unit="s", utc=True)).dt.date.nunique()
    gaps = np.diff(idxs) / 900.0
    nep = 1 + int((gaps > 16 * 4).sum())
    rr_ = R[L]
    ac = float(np.corrcoef(rr_[:-1], rr_[1:])[0, 1]) if len(rr_) > 2 else np.nan
    print(f"    {nm:10} N={len(t):4d}  unique days={days:4d}  distinct H4-up episodes(>4 H4 gap)={nep:4d}  lag-1 autocorr={ac:+.4f}")
    print(f"               trades/episode={len(t)/nep:.2f}  median gap between trades={np.median(gaps)/4:.1f} H4 bars")

print("\n" + "=" * 92)
print("  SECTION 7 -- TAIL ROBUSTNESS")
print("=" * 92)
for nm, L in (("FROZEN", fr), ("CAUSAL C1", c1)):
    r = R[L]; nn = len(r); s = np.sort(r)
    tot = r.sum()
    print(f"  {nm}:  N={nn}  total={tot:+.1f}R")
    for f in (0.01, 0.05, 0.10):
        k = min(int(np.ceil(nn * f)), nn - 1)
        print(f"    best-{int(f*100):2d}%-removed (k={k:2d}) -> {s[:nn-k].mean():+.4f}      "
              f"worst-{int(f*100):2d}%-removed -> {s[k:].mean():+.4f}")
    print(f"    largest single winner {s[-1]:+.3f}R = {s[-1]/tot:.1%} of total   top-5 = {s[-5:].sum()/tot:.1%}   top-10 = {s[-10:].sum()/tot:.1%}")
    yy = pd.Series(pd.to_datetime(te[L], unit="s", utc=True)).dt.year.to_numpy()
    ysum = {int(y): float(r[yy == y].sum()) for y in sorted(set(yy))}
    by = max(ysum, key=ysum.get)
    print(f"    largest winning YEAR {by} contributes {ysum[by]/tot:.1%}; removing it -> avgR {r[yy!=by].mean():+.4f}")

print("\n" + "=" * 92)
print("  SECTION 9/10 -- EXECUTION AND NEIGHBOUR ROBUSTNESS, both labels (no selection)")
print("=" * 92)
print(f"  {'variant':26}{'FROZEN N':>10}{'FROZEN avgR':>13}{'CAUSAL N':>10}{'CAUSAL avgR':>13}")
for nm, kw in (("dedup 8", dict(dedup=8)), ("dedup 16 (frozen)", dict(dedup=16)), ("dedup 24", dict(dedup=24)),
               ("dedup 32", dict(dedup=32)), ("dedup 48", dict(dedup=48)),
               ("stop 1.0 rr3", dict(stopmult=1.0, rr=3.0)), ("stop 2.0 rr2", dict(stopmult=2.0, rr=2.0)),
               ("stop 1.5 rr1", dict(stopmult=1.5, rr=1.0))):
    t = build(0, **kw); tt = t["t_entry"].to_numpy(); f2, c2 = labels(tt); rr_ = t["R"].to_numpy()
    print(f"  {nm:26}{int(f2.sum()):10d}{rr_[f2].mean():+13.4f}{int(c2.sum()):10d}{rr_[c2].mean():+13.4f}")

json.dump(dict(only_frozen_n=int(only_frozen.sum()), only_frozen_avgR=float(R[only_frozen].mean()),
               both_n=int(both.sum()), both_avgR=float(R[both].mean())),
          open(os.path.join(OUT, "run2.json"), "w"), indent=1)
