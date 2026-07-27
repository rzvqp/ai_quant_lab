#!/usr/bin/env python3
"""Phase-2 verification for the M5 extended file. Pure stdlib.

CHECK 1 for M5 is the cross-timeframe consistency test the mandate specifies: aggregate M5 into
15-minute bars and compare to the extended M15 file over the whole overlap (zero OHLC mismatches,
same standard). Verification 0 (half-window-offset double pull) is reported separately, before this.

Usage: python verify_m5.py --m5 <m5.csv> --m15 <extended_m15.csv>
"""
import argparse, csv, hashlib, statistics as st
from datetime import datetime, timezone

STEP = 300  # M5


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
    ap.add_argument("--m5", required=True)
    ap.add_argument("--m15", required=True)
    args = ap.parse_args()

    m5 = sorted(load(args.m5), key=lambda x: x[0])
    m15 = {b[0]: b for b in load(args.m15)}
    times = [b[0] for b in m5]
    tset = set(times)

    print("=" * 78)
    print(f"VERIFICATION — OANDA:XAUUSD M5   new={args.m5}")
    print("=" * 78)

    # ---- CHECK 1: aggregate M5 -> 15-min and compare to extended M15 ----
    print("\n[CHECK 1] CONSISTENCY — aggregate M5 to 15-min vs extended M15 (overlap)")
    buckets = {}
    for b in m5:
        k = b[0] - (b[0] % 900)
        buckets.setdefault(k, []).append(b)
    compared = ohlc_mism = vol_mism = incomplete = 0
    ohlc_samples, vol_samples = [], []
    for k in sorted(buckets):
        if k not in m15:
            continue
        bs = sorted(buckets[k], key=lambda x: x[0])
        # a complete 15-min bucket has 3 M5 bars at k, k+300, k+600
        if [x[0] for x in bs] != [k, k + 300, k + 600]:
            incomplete += 1
            continue
        agg_o = bs[0][1]
        agg_h = max(x[2] for x in bs)
        agg_l = min(x[3] for x in bs)
        agg_c = bs[-1][4]
        agg_v = sum(x[5] for x in bs)
        ref = m15[k]
        compared += 1
        if (agg_o, agg_h, agg_l, agg_c) != (ref[1], ref[2], ref[3], ref[4]):
            ohlc_mism += 1
            if len(ohlc_samples) < 8:
                ohlc_samples.append((k, (agg_o, agg_h, agg_l, agg_c), ref[1:5]))
        if agg_v != ref[5]:
            vol_mism += 1
            if len(vol_samples) < 8:
                vol_samples.append((k, agg_v, ref[5]))
    print(f"  complete 15-min buckets compared : {compared}")
    print(f"  incomplete buckets skipped       : {incomplete}")
    print(f"  OHLC mismatches (EXACT)          : {ohlc_mism}")
    print(f"  volume mismatches (sum vs M15)   : {vol_mism}")
    print(f"  >>> CHECK 1 VERDICT (OHLC) : {'PASS' if ohlc_mism == 0 else 'FAIL — STOP'} <<<")
    for k, a, b in ohlc_samples:
        print(f"     {iso(k)}  agg={a}  m15={b}")
    for k, a, b in vol_samples:
        print(f"     [vol] {iso(k)}  aggSum={a:.0f}  m15={b:.0f}  d={a-b:+.0f}")

    # ---- CHECK 2: coverage map ----
    print("\n[CHECK 2] COVERAGE MAP — bars per UTC hour")
    byhour = {h: 0 for h in range(24)}
    for t in times:
        byhour[datetime.fromtimestamp(t, tz=timezone.utc).hour] += 1
    mx = max(byhour.values())
    for h in range(24):
        flag = "  <-- maintenance gap" if byhour[h] < 0.5 * mx else ""
        print(f"  {h:02d}:00 UTC  {byhour[h]:8d}  {'#' * int(40 * byhour[h] / mx)}{flag}")

    # ---- CHECK 3: gaps ----
    print("\n[CHECK 3] GAPS (missing intervals > one bar; weekends separate)")
    wk, iw = [], []
    for i in range(1, len(times)):
        d = times[i] - times[i - 1]
        if d > STEP:
            prev = datetime.fromtimestamp(times[i - 1], tz=timezone.utc)
            (wk if (prev.weekday() == 4 or d >= 47 * 3600) else iw).append((times[i-1], times[i], d))
    print(f"  weekend gaps            : {len(wk)}")
    print(f"  intra-week gaps > 1 bar : {len(iw)}")
    iw.sort(key=lambda x: -x[2])
    for a, b, d in iw[:15]:
        print(f"     {iso(a)} -> {iso(b)}   {d/60:.0f} min ({d//STEP} bars)")

    # ---- CHECK 4: integrity ----
    print("\n[CHECK 4] INTEGRITY")
    print(f"  sha256         : {sha256(args.m5)}")
    print(f"  bars           : {len(m5)}")
    print(f"  distinct times : {len(tset)}  (duplicates: {len(times)-len(tset)})")
    print(f"  first bar      : {times[0]}  {iso(times[0])}")
    print(f"  last  bar      : {times[-1]}  {iso(times[-1])}")
    print(f"  span           : {(times[-1]-times[0])/86400/365.25:.2f} years")

    # ---- CHECK 5: anomalies ----
    print("\n[CHECK 5] ANOMALIES — high amplitude on low volume")
    ranges = sorted(b[2] - b[3] for b in m5)
    vols = sorted(b[5] for b in m5)
    r_hi = ranges[int(0.999 * len(ranges))]
    v_lo = vols[int(0.05 * len(vols))]
    generic = [b for b in m5 if (b[2] - b[3]) >= r_hi and b[5] <= v_lo]
    print(f"  generic (range>=p99.9 [{r_hi:.3f}] AND vol<=p5 [{v_lo:.0f}]): {len(generic)}")
    for b in generic[:8]:
        print(f"     {iso(b[0])}  range={b[2]-b[3]:.3f}  vol={b[5]:.0f}")

    # ---- CHECK 6: bar amplitude (MANDATORY — derives §9 min stop threshold) ----
    print("\n[CHECK 6] BAR AMPLITUDE (high-low) per session — derives §9 minimum stop threshold")
    print("  On a 5-min bar the high/low ordering is unknown; a stop tighter than the typical bar")
    print("  amplitude makes the intrabar outcome indeterminate. This is the distribution to floor against.")
    bysess = {}
    allr = []
    for b in m5:
        h = datetime.fromtimestamp(b[0], tz=timezone.utc).hour
        rng = b[2] - b[3]
        bysess.setdefault(session(h), []).append(rng); allr.append(rng)
    print(f"  {'session':8s} {'n':>9s} {'median':>10s} {'IQR (25-75)':>20s} {'p90':>9s}")
    for s in ("asia", "london", "ny", "late"):
        xs = sorted(bysess.get(s, []))
        if not xs: continue
        q1, q3, p90 = xs[int(0.25*len(xs))], xs[int(0.75*len(xs))], xs[int(0.90*len(xs))]
        print(f"  {s:8s} {len(xs):9d} {st.median(xs):10.3f}   [{q1:8.3f}, {q3:8.3f}] {p90:9.3f}")
    allr.sort()
    print(f"  ALL      {len(allr):9d} {st.median(allr):10.3f}   "
          f"[{allr[int(0.25*len(allr))]:8.3f}, {allr[int(0.75*len(allr))]:8.3f}] {allr[int(0.90*len(allr))]:9.3f}")

    # ---- CHECK 7: regime map is M15-specific ----
    print("\n[CHECK 7] REGIME COVERAGE")
    print("  N/A for M5: the M5 window (2021-07 onward) sits inside regimes already mapped on the")
    print("  extended M15 (2020-2022 correction tail + 2022-2026 bull). No separate regime map needed.")

    print("\n" + "=" * 78)
    print("END OF REPORT — nothing integrated, nothing modified.")
    print("=" * 78)


if __name__ == "__main__":
    main()
