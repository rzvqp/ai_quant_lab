"""STAT-OCO-REPLICATION-V1 -- independent re-implementation of Alpha's
DIRECTION_AGNOSTIC_EXPANSION_HARVEST_V1 anchor-B architecture, written from the spec, then instrumented.
No spec changes. No optimisation."""
from __future__ import annotations
import sys, math, hashlib, json
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MKT = r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\data\market\OANDA_XAUUSD_M15.csv"
COST = 0.419          # price units per trade (Alpha's BASE)
H = 96                # 96 M15 bars = 24h
HOLDOUT = pd.Timestamp("2025-10-23T09:15:00+00:00")

d = pd.read_csv(MKT).drop_duplicates("time").sort_values("time").reset_index(drop=True)
d["dt"] = pd.to_datetime(d["time"], unit="s", utc=True)
O = d.open.to_numpy(float); Hi = d.high.to_numpy(float); Lo = d.low.to_numpy(float)
Cl = d.close.to_numpy(float); TS = d["time"].to_numpy(np.int64); N = len(d)
YR = d.dt.dt.year.to_numpy(); DATE = d.dt.dt.date.values
DOW = d.dt.dt.dayofweek.to_numpy()

# ---- anchors: first bar of each UTC calendar date; activations = prior date's high/low
df = pd.DataFrame({"i": np.arange(N), "dd": DATE, "h": Hi, "l": Lo})
g = df.groupby("dd")
firsts = g["i"].first(); dhi = g["h"].max(); dlo = g["l"].min(); dcnt = g["i"].count()
days = list(firsts.index)
S = np.array([int(firsts.iloc[k]) for k in range(1, len(days))])
PDH = np.array([float(dhi.iloc[k - 1]) for k in range(1, len(days))])
PDL = np.array([float(dlo.iloc[k - 1]) for k in range(1, len(days))])
PDN = np.array([int(dcnt.iloc[k - 1]) for k in range(1, len(days))])     # bars in the PRIOR day
RISK = PDH - PDL
ok = (RISK > 0) & np.isfinite(RISK)
S, PDH, PDL, RISK, PDN = S[ok], PDH[ok], PDL[ok], RISK[ok], PDN[ok]


def episode(s, ua, da, mult, worst_case=False, cost=COST):
    """Alpha's semantics verbatim. worst_case=True also resolves a same-bar target+stop as a stop on the
    trigger bar AND treats an unresolved trigger-bar as adverse-first."""
    risk = ua - da
    end = min(s + H, N - 1)
    trig = None
    for j in range(s + 1, end + 1):
        up = Hi[j] >= ua; dn = Lo[j] <= da
        if up and dn:
            return dict(status="ambiguous")
        if up: trig = (j, +1, ua); break
        if dn: trig = (j, -1, da); break
    if trig is None:
        return dict(status="notrig")
    j, dr, entry = trig
    stop = da if dr > 0 else ua
    tgt = entry + dr * mult * risk
    res = None; kexit = end; samebar = 0
    for k in range(j, end + 1):
        ht = (Hi[k] >= tgt) if dr > 0 else (Lo[k] <= tgt)
        hs = (Lo[k] <= stop) if dr > 0 else (Hi[k] >= stop)
        if ht and hs:
            res = -1.0; kexit = k; samebar = 1; break
        if hs:
            res = -1.0; kexit = k; break
        if ht:
            res = float(mult); kexit = k; break
    mtm = 0
    if res is None:
        res = dr * (Cl[end] - entry) / risk; kexit = end; mtm = 1
    return dict(status="traded", net=res - cost / risk, gross=res, side=dr, risk=risk,
                trig_bar=j, exit_bar=kexit, samebar=samebar, mtm=mtm,
                bars_to_trig=j - s, hold=kexit - j, entry=entry)


def run(mult, mask=None, cost=COST, sel=None):
    out = []
    idx = range(len(S)) if sel is None else sel
    for i in idx:
        if mask is not None and not mask[i]: continue
        r = episode(S[i], PDH[i], PDL[i], mult, cost=cost)
        r["i"] = i; out.append(r)
    return out


def stats(rows, label, quiet=False):
    tr = [r for r in rows if r["status"] == "traded"]
    net = np.array([r["net"] for r in tr]); gross = np.array([r["gross"] for r in tr])
    ii = np.array([r["i"] for r in tr]); yE = YR[S[ii]]
    dev = yE <= 2019; pre = yE < 2021
    nt = sum(1 for r in rows if r["status"] == "notrig")
    am = sum(1 for r in rows if r["status"] == "ambiguous")
    w = net > 0
    pf = net[w].sum() / abs(net[~w].sum()) if (~w).any() else np.inf
    if not quiet:
        print(f"  {label:24s} N={len(net):5d} gross={gross.mean():+.4f} net={net.mean():+.4f} WR={w.mean():.3f} "
              f"PF={pf:.3f} DEV={net[dev].mean():+.4f} OOS={net[~dev].mean():+.4f} "
              f"PRE={net[pre].mean():+.4f} POST={net[~pre].mean():+.4f} notrig={nt} amb={am}")
    return dict(net=net, gross=gross, ii=ii, tr=tr, notrig=nt, amb=am, pf=float(pf))


print("=" * 122)
print("  §2  INDEPENDENT RE-IMPLEMENTATION vs ALPHA'S REPORTED NUMBERS")
print("=" * 122)
print(f"  data: {MKT}")
print(f"        {N} M15 bars, {d.dt.min()} -> {d.dt.max()}   sha256 {hashlib.sha256(open(MKT,'rb').read()).hexdigest()[:16]}...")
print(f"  candidate daily episodes with valid prior-day range: {len(S)}\n")
R = {}
for m, claim in ((1.0, 0.032), (1.5, 0.045), (2.0, 0.054)):
    rows = run(m); R[m] = stats(rows, f"target {m}R")
    got = R[m]["net"].mean()
    print(f"  {'':24s} Alpha claimed {claim:+.3f} -> {'MATCH' if abs(got-claim)<0.0015 else 'DIFFER'}")

print("\n" + "=" * 122)
print("  §1/§3  THE RISK UNIT -- everything below is denominated in it, so it is audited first")
print("=" * 122)
tr = R[2.0]["tr"]; rk = np.array([r["risk"] for r in tr]); ii = np.array([r["i"] for r in tr])
print(f"  risk = prior-day HIGH minus prior-day LOW (USD).  quantiles over the {len(rk)} traded episodes:")
for q in (0.001, 0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99):
    print(f"    p{q*100:6.1f} : {np.quantile(rk,q):8.3f} USD  ({np.quantile(rk,q)/0.10:7.0f} pips)   "
          f"cost as R = {COST/np.quantile(rk,q):.4f}")
print(f"\n  bars in the PRIOR day (a full UTC trading day is ~92-96 M15 bars):")
pn = PDN[ii]
for q in (0.001, 0.01, 0.02, 0.05, 0.10, 0.50):
    print(f"    p{q*100:6.1f} : {np.quantile(pn,q):6.0f} bars")
short = pn < 40
print(f"\n  episodes whose 'prior day' had FEWER THAN 40 bars: {short.sum()} ({short.mean():.2%})")
print(f"    -> these are MONDAYS, whose 'prior day' is the Sunday re-open stub (~2h of trading).")
print(f"    prior-day-bar count on those: min {pn[short].min()}, median {np.median(pn[short]):.0f}")
print(f"    their risk unit: median {np.median(rk[short]):.2f} USD vs {np.median(rk[~short]):.2f} USD on normal days")
print(f"    day-of-week of those episodes: {dict(zip(*np.unique(DOW[S[ii[short]]], return_counts=True)))}  (0=Mon)")
net2 = R[2.0]["net"]
print(f"\n  CONTRIBUTION OF THOSE {short.sum()} STUB-PRIOR-DAY EPISODES to the 2R result:")
print(f"    mean net on stub episodes    : {net2[short].mean():+.4f} R   (n={short.sum()})")
print(f"    mean net on normal episodes  : {net2[~short].mean():+.4f} R   (n={(~short).sum()})")
print(f"    share of TOTAL PnL from stubs: {100*net2[short].sum()/net2.sum():.1f}%  "
      f"while being {100*short.mean():.1f}% of episodes")
print(f"    largest single net-R values overall: {np.sort(net2)[-8:].round(2)}")
big = net2 > 3
print(f"    episodes with net > +3R: {big.sum()}  -- of these {int((short & big).sum())} are stub-prior-day")
json.dump({"n": int(len(S))}, open("meta.json", "w"))
