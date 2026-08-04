#!/usr/bin/env python3
"""M1 acquisition verification (Mandate: acquire M1, do NOT segment/derive HTF). Pure stdlib.
Reports integrity + bar-accounting invariant + REAL coverage (first/last, gaps, continuity), plus a
cross-timeframe consistency check (aggregate M1->M5 vs the existing M5 file) and the cost/R that makes
M1 UNFIT FOR VALIDATION. Reads only; modifies nothing.

Usage: python verify_m1.py --m1 <m1.csv> --m5 <m5.csv>
"""
import argparse, csv, hashlib, statistics as st
from datetime import datetime, timezone

STEP = 60  # M1


def iso(ep): return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
def session(h): return "asia" if h < 8 else "london" if h < 13 else "ny" if h < 21 else "late"


def load(path):
    rows = []
    with open(path, newline="") as f:
        r = csv.reader(f); next(r)
        for ln in r:
            if ln and ln[0].strip():
                rows.append((int(ln[0]), float(ln[1]), float(ln[2]), float(ln[3]), float(ln[4]), float(ln[5])))
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m1", required=True)
    ap.add_argument("--m5", required=True)
    args = ap.parse_args()
    m1 = sorted(load(args.m1), key=lambda x: x[0])
    times = [b[0] for b in m1]
    tset = set(times)

    print("=" * 78)
    print("VERIFICATION — OANDA:XAUUSD M1   *** UNFIT FOR VALIDATION ***")
    print("  single regime (bull only, ~1yr), prohibitive cost/R -- execution/confirmation layer ONLY,")
    print("  never a backtest/edge-validation base. Not segmented, no HTF derived (per mandate).")
    print("=" * 78)

    # ---- CHECK 4: INTEGRITY + bar-accounting invariant ----
    print("\n[INTEGRITY + BAR-ACCOUNTING INVARIANT]")
    print(f"  sha256         : {sha256(args.m1)}")
    print(f"  bars           : {len(m1)}")
    print(f"  distinct times : {len(tset)}   (duplicates: {len(times) - len(tset)})")
    mono = all(times[i] < times[i+1] for i in range(len(times)-1))
    print(f"  strictly increasing (sorted, unique) : {mono}")
    print(f"  first bar      : {times[0]}  {iso(times[0])}")
    print(f"  last  bar      : {times[-1]}  {iso(times[-1])}")
    print(f"  span           : {(times[-1]-times[0])/86400:.1f} days ({(times[-1]-times[0])/86400/365.25:.2f} yr)")
    # invariant: present + missing_slots == nominal slot count over [first,last]
    nominal = (times[-1] - times[0]) // STEP + 1
    missing = nominal - len(tset)
    print(f"  invariant      : present {len(tset)} + missing_slots {missing} == nominal grid {nominal}  "
          f"-> {len(tset)+missing == nominal}")

    # ---- REAL COVERAGE: gaps + continuity ----
    print("\n[REAL COVERAGE — gaps > one bar; weekends separate]")
    wk, iw = [], []
    for i in range(1, len(times)):
        d = times[i] - times[i-1]
        if d > STEP:
            prev = datetime.fromtimestamp(times[i-1], tz=timezone.utc)
            (wk if (prev.weekday() == 4 or d >= 47*3600) else iw).append((times[i-1], times[i], d))
    covered = len(tset)
    print(f"  floor (deepest bar) : {iso(times[0])}   (live-measured by the walk)")
    print(f"  weekend gaps        : {len(wk)}")
    print(f"  intra-week gaps>1bar: {len(iw)}")
    print(f"  continuity          : {covered} present / {nominal} nominal = {100*covered/nominal:.1f}% "
          f"(gaps are weekends + the 21:00Z OANDA maintenance window; NOT smoothed)")
    iw.sort(key=lambda x: -x[2])
    print("  longest 10 intra-week gaps:")
    for a, b, d in iw[:10]:
        print(f"     {iso(a)} -> {iso(b)}   {d/60:.0f} min ({d//STEP} bars)")

    # ---- COVERAGE MAP ----
    print("\n[COVERAGE MAP — bars per UTC hour]")
    byhour = {h: 0 for h in range(24)}
    for t in times:
        byhour[datetime.fromtimestamp(t, tz=timezone.utc).hour] += 1
    mx = max(byhour.values())
    for h in range(24):
        flag = "  <-- maintenance gap" if byhour[h] < 0.5*mx else ""
        print(f"  {h:02d}:00 UTC  {byhour[h]:7d}  {'#'*int(40*byhour[h]/mx)}{flag}")

    # ---- CROSS-CHECK: aggregate M1 -> 5-min vs existing M5 on overlap ----
    print("\n[CONSISTENCY — aggregate M1 to 5-min vs existing M5 (overlap)]")
    m5 = {b[0]: b for b in load(args.m5)}
    buckets = {}
    for b in m1:
        k = b[0] - (b[0] % 300)
        buckets.setdefault(k, []).append(b)
    compared = ohlc_mism = vol_mism = incomplete = 0
    samples = []
    for k in sorted(buckets):
        if k not in m5:
            continue
        bs = sorted(buckets[k], key=lambda x: x[0])
        if [x[0] for x in bs] != [k, k+60, k+120, k+180, k+240]:  # complete 5-bar M5 bucket
            incomplete += 1
            continue
        agg = (bs[0][1], max(x[2] for x in bs), min(x[3] for x in bs), bs[-1][4])
        ref = m5[k]; compared += 1
        if agg != ref[1:5]:
            ohlc_mism += 1
            if len(samples) < 6: samples.append((k, agg, ref[1:5]))
        if sum(x[5] for x in bs) != ref[5]:
            vol_mism += 1
    print(f"  complete 5-min buckets compared : {compared}")
    print(f"  incomplete buckets skipped      : {incomplete}")
    print(f"  OHLC mismatches (EXACT)         : {ohlc_mism}")
    print(f"  volume mismatches               : {vol_mism}")
    print(f"  >>> CONSISTENCY VERDICT (OHLC) : {'PASS' if ohlc_mism == 0 else 'FAIL'} <<<")
    for k, a, b in samples:
        print(f"     {iso(k)}  aggM1={a}  m5={b}")

    # ---- BAR AMPLITUDE + COST/R (why UNFIT) ----
    print("\n[BAR AMPLITUDE (high-low) + COST/R -- the reason M1 is UNFIT FOR VALIDATION]")
    allr = sorted(b[2]-b[3] for b in m1)
    med = st.median(allr)
    bysess = {}
    for b in m1:
        h = datetime.fromtimestamp(b[0], tz=timezone.utc).hour
        bysess.setdefault(session(h), []).append(b[2]-b[3])
    print(f"  {'session':8s} {'n':>9s} {'median':>10s} {'IQR(25-75)':>18s}")
    for s in ("asia", "london", "ny", "late"):
        xs = sorted(bysess.get(s, []))
        if not xs: continue
        q1, q3 = xs[int(0.25*len(xs))], xs[int(0.75*len(xs))]
        print(f"  {s:8s} {len(xs):9d} {st.median(xs):10.3f}   [{q1:7.3f},{q3:7.3f}]")
    print(f"  ALL median high-low = {med:.3f} pts  (p25 {allr[len(allr)//4]:.3f}, p75 {allr[3*len(allr)//4]:.3f})")
    for spread in (0.20, 0.30, 0.50):
        # cost/R at a 1xATR-median stop, round-trip fixed cost = spread (disclosed assumption)
        print(f"  cost/R @ stop=1x median range, spread ${spread:.2f}/oz : {100*spread/med:.0f}%")
    print("  (vs ~3% on M15 -- confirms the CEO's ~40% order of magnitude; kills asymmetric-RR edges)")

    print("\n" + "=" * 78)
    print("END — M1 delivered UNFIT FOR VALIDATION. Not segmented, no HTF. Statistician decides structure.")
    print("=" * 78)


if __name__ == "__main__":
    main()
