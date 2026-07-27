#!/usr/bin/env python3
"""Phase-2 verification for the H1 extended file. Pure stdlib.

CHECK 1 (authoritative, same-source): aggregate the extended M15 -> hourly and compare to the native
H1 pull (zero OHLC mismatches expected, like the M5->M15 check).
VERIFICATION 0(a) (cross-check, DIFFERENT construction): native H1 vs the lab's EXISTING H1, which was
resampled from the OLD M15 (7th 'sub' column), not natively pulled — reported with an appropriate,
looser standard. VERIFICATION 0(b) (double-pull offset, pre-2023) is run separately.

Usage: python verify_h1.py --h1 <native_h1.csv> --m15 <extended_m15.csv> --existing <existing_h1.csv>
"""
import argparse, csv, hashlib, statistics as st
from datetime import datetime, timezone

STEP = 3600  # H1


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
    ap.add_argument("--h1", required=True)
    ap.add_argument("--m15", required=True)
    ap.add_argument("--existing", required=True)
    args = ap.parse_args()

    h1 = sorted(load(args.h1), key=lambda x: x[0])
    h1map = {b[0]: b for b in h1}
    m15 = load(args.m15)
    existing = {b[0]: b for b in load(args.existing)}
    times = [b[0] for b in h1]
    tset = set(times)

    print("=" * 78)
    print(f"VERIFICATION — OANDA:XAUUSD H1   new={args.h1}")
    print("=" * 78)

    # ---- VERIFICATION 0(a): native H1 vs EXISTING resampled H1 (different construction) ----
    print("\n[VERIFICATION 0a] native H1 vs EXISTING resampled-from-M15 H1 (overlap)")
    print("  NOTE: the existing H1 was resampled from the OLD M15 (7-col, 'sub'), not natively pulled,")
    print("  and the old M15 carried the provisional-edge defect. So this is NOT a same-source compare;")
    print("  small OHLC/volume differences are expected. Authoritative check is CHECK 1 below.")
    common = sorted(t for t in tset if t in existing)
    if common:
        tsalign = all(t % 3600 == 0 for t in common)
        ohlc_d = [t for t in common if h1map[t][1:5] != existing[t][1:5]]
        vol_d = [t for t in common if h1map[t][5] != existing[t][5]]
        # magnitude of OHLC differences
        maxd = 0.0
        for t in ohlc_d:
            for i in range(1, 5):
                maxd = max(maxd, abs(h1map[t][i] - existing[t][i]))
        print(f"  overlap bars                 : {len(common)}  ({iso(common[0])}..{iso(common[-1])})")
        print(f"  all timestamps :00 aligned   : {tsalign}")
        print(f"  bars with OHLC difference    : {len(ohlc_d)}  ({len(ohlc_d)/len(common)*100:.2f}%)  max|delta|={maxd:.4f}")
        print(f"  bars with volume difference  : {len(vol_d)}  ({len(vol_d)/len(common)*100:.2f}%)")
        for t in ohlc_d[:6]:
            print(f"     {iso(t)}  native={h1map[t][1:5]}  resampled={existing[t][1:5]}")

    # ---- CHECK 1: aggregate extended M15 -> H1 vs native H1 (SAME SOURCE, authoritative) ----
    print("\n[CHECK 1] CONSISTENCY — aggregate extended M15 to hourly vs native H1 (SAME SOURCE)")
    buckets = {}
    for b in m15:
        k = b[0] - (b[0] % 3600)
        buckets.setdefault(k, []).append(b)
    compared = ohlc_mism = vol_mism = incomplete = 0
    samples = []
    for k in sorted(buckets):
        if k not in h1map:
            continue
        bs = sorted(buckets[k], key=lambda x: x[0])
        if [x[0] for x in bs] != [k, k + 900, k + 1800, k + 2700]:
            incomplete += 1
            continue
        agg = (bs[0][1], max(x[2] for x in bs), min(x[3] for x in bs), bs[-1][4])
        aggv = sum(x[5] for x in bs)
        ref = h1map[k]
        compared += 1
        if agg != ref[1:5]:
            ohlc_mism += 1
            if len(samples) < 8:
                samples.append((k, agg, ref[1:5]))
        if aggv != ref[5]:
            vol_mism += 1
    print(f"  complete hourly buckets compared : {compared}")
    print(f"  incomplete buckets skipped       : {incomplete}  (mostly the 21:00 UTC maintenance hour)")
    print(f"  OHLC mismatches (EXACT)          : {ohlc_mism}")
    print(f"  volume mismatches                : {vol_mism}")
    print(f"  >>> CHECK 1 VERDICT (OHLC) : {'PASS' if ohlc_mism == 0 else 'FAIL — STOP'} <<<")
    for k, a, b in samples:
        print(f"     {iso(k)}  aggM15={a}  h1={b}")

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
    for a, b, d in iw[:12]:
        print(f"     {iso(a)} -> {iso(b)}   {d/3600:.1f} h ({d//STEP} bars)")

    # ---- CHECK 4: integrity ----
    print("\n[CHECK 4] INTEGRITY")
    print(f"  sha256         : {sha256(args.h1)}")
    print(f"  bars           : {len(h1)}")
    print(f"  distinct times : {len(tset)}  (duplicates: {len(times)-len(tset)})")
    print(f"  first bar      : {times[0]}  {iso(times[0])}")
    print(f"  last  bar      : {times[-1]}  {iso(times[-1])}")
    print(f"  span           : {(times[-1]-times[0])/86400/365.25:.2f} years")

    # ---- CHECK 5: anomalies ----
    print("\n[CHECK 5] ANOMALIES — high amplitude on low volume")
    ranges = sorted(b[2] - b[3] for b in h1)
    vols = sorted(b[5] for b in h1)
    r_hi = ranges[int(0.999 * len(ranges))]
    v_lo = vols[int(0.05 * len(vols))]
    generic = [b for b in h1 if (b[2] - b[3]) >= r_hi and b[5] <= v_lo]
    print(f"  generic (range>=p99.9 [{r_hi:.3f}] AND vol<=p5 [{v_lo:.0f}]): {len(generic)}")
    for b in generic[:8]:
        print(f"     {iso(b[0])}  range={b[2]-b[3]:.3f}  vol={b[5]:.0f}")

    # ---- CHECK 6: bar amplitude per session ----
    print("\n[CHECK 6] BAR AMPLITUDE (high-low) per session")
    bysess = {}
    for b in h1:
        h = datetime.fromtimestamp(b[0], tz=timezone.utc).hour
        bysess.setdefault(session(h), []).append(b[2] - b[3])
    print(f"  {'session':8s} {'n':>9s} {'median':>10s} {'IQR (25-75)':>20s}")
    for s in ("asia", "london", "ny", "late"):
        xs = sorted(bysess.get(s, []))
        if not xs: continue
        q1, q3 = xs[int(0.25*len(xs))], xs[int(0.75*len(xs))]
        print(f"  {s:8s} {len(xs):9d} {st.median(xs):10.3f}   [{q1:8.3f}, {q3:8.3f}]")

    # ---- CHECK 7: regime coverage (H1 spans ~20y — worth a descriptive map) ----
    print("\n[CHECK 7] REGIME COVERAGE — descriptive (yearly closes; full map is on extended M15)")
    yc = {}
    for t, o, h, l, c, v in h1:
        yc[datetime.fromtimestamp(t, tz=timezone.utc).year] = c
    print("  year-end closes:", ", ".join(f"{y}:{yc[y]:.0f}" for y in sorted(yc)))
    print("  (2006-2011 pre-dates the M15 file — new regime territory: 2008 crisis run-up + 2011 peak.)")

    print("\n" + "=" * 78)
    print("END OF REPORT — nothing integrated, nothing modified.")
    print("=" * 78)


if __name__ == "__main__":
    main()
