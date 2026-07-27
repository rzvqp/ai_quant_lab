#!/usr/bin/env python3
"""Data Acquisition — Phase 2 verification for an extended intraday CSV.

Pure stdlib (no pandas). Runs the seven mandated checks and prints a structured
report. Reads only; never writes, imputes, or "corrects" anything.

Check numbering follows the CEO mandate:
  1. Consistency vs existing, bar-by-bar on overlap  (EXACT OHLC mismatch count)
  2. Coverage map: bars per UTC hour                 (21:00 maintenance gap)
  3. Gaps > one bar, weekends separate
  4. Integrity: sha256, bar count, first/last bar
  5. Anomalies: high amplitude on low volume         (120-136pt @ vol 748-3980)
  6. Bar amplitude high-low: median + IQR per session
  7. Regime coverage (M15 only): up/down/sideways legs over the span

Usage:
  python verify_extension.py --new <ext.csv> --existing <existing.csv> --tf M15 [--regime]
"""
import argparse, csv, hashlib, statistics as st
from datetime import datetime, timezone

TF_SECONDS = {"M15": 900, "H1": 3600, "M5": 300, "M1": 60}


def iso(ep):
    return datetime.fromtimestamp(ep, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def load(path):
    """Return list of (t,o,h,l,c,v) using only the first 6 columns (ignores any 7th)."""
    rows = []
    with open(path, newline="") as f:
        r = csv.reader(f)
        next(r)  # header
        for line in r:
            if not line or not line[0].strip():
                continue
            rows.append((int(line[0]), float(line[1]), float(line[2]),
                         float(line[3]), float(line[4]), float(line[5])))
    return rows


def sha256(path):
    hsh = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            hsh.update(chunk)
    return hsh.hexdigest()


def session(hour):
    return "asia" if hour < 8 else "london" if hour < 13 else "ny" if hour < 21 else "late"


def regime_map(new, thresh=0.15):
    """Descriptive swing decomposition on monthly closes (index-tracked zig-zag): a leg
    closes when price reverses >= `thresh` from the running extreme. Purely descriptive:
    no signal, no indicator used for trading — a factual regime map for split pre-registration."""
    monthly = {}
    for t, o, h, l, c, v in new:
        d = datetime.fromtimestamp(t, tz=timezone.utc)
        monthly[(d.year, d.month)] = (t, c)
    pts = [monthly[k] for k in sorted(monthly)]  # [(t, close), ...]
    if len(pts) < 3:
        return []
    legs = []            # list of (anchor_idx, extreme_idx)
    anchor = hi = lo = 0
    trend = 0            # +1 up, -1 down, 0 undecided
    for i in range(1, len(pts)):
        c = pts[i][1]
        if c > pts[hi][1]:
            hi = i
        if c < pts[lo][1]:
            lo = i
        if trend >= 0 and c <= pts[hi][1] * (1 - thresh):
            legs.append((anchor, hi)); anchor = hi; trend = -1; lo = i
        elif trend <= 0 and c >= pts[lo][1] * (1 + thresh):
            legs.append((anchor, lo)); anchor = lo; trend = 1; hi = i
    last = hi if trend >= 0 else lo
    if last != anchor:
        legs.append((anchor, last))
    out = []
    for a, b in legs:
        (t0, p0), (t1, p1) = pts[a], pts[b]
        if t1 <= t0:
            continue
        pct = (p1 - p0) / p0 * 100
        lab = "UP" if pct >= 10 else "DOWN" if pct <= -10 else "SIDEWAYS"
        out.append((t0, t1, p0, p1, pct, lab))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--existing", required=True)
    ap.add_argument("--tf", required=True, choices=list(TF_SECONDS))
    ap.add_argument("--regime", action="store_true", help="include check 7 regime map (M15)")
    args = ap.parse_args()
    step = TF_SECONDS[args.tf]

    new = sorted(load(args.new), key=lambda x: x[0])
    ex = sorted(load(args.existing), key=lambda x: x[0])
    times = [b[0] for b in new]
    tset = set(times)

    print("=" * 78)
    print(f"VERIFICATION — OANDA:XAUUSD {args.tf}")
    print(f"  new={args.new}")
    print(f"  existing={args.existing}")
    print("=" * 78)

    # Named, pre-declared exception to the zero-mismatch standard (CEO-fixed):
    # the existing file's terminal bar, where TEST B proved the NEW capture (13464) is correct
    # and the existing value (8201) was the existing file's own provisional terminal bar.
    NAMED_EXCEPTIONS = {1783922400: "existing terminal bar 2026-07-13 06:00Z; TEST B: new=13464 correct, existing=8201 provisional"}

    # ---- VERIFICATION 0 / CHECK 1: CONTROL — consistency vs existing, bar-by-bar on overlap ----
    print("\n[VERIFICATION 0 / CHECK 1] CONTROL — bar-by-bar OHLCV vs existing on overlap")
    print("  Standard: ZERO mismatches, except the ONE pre-named exception below.")
    exmap = {b[0]: b for b in ex}
    newmap = {b[0]: b for b in new}
    common = sorted(t for t in tset if t in exmap)
    if not common:
        print("  no overlapping timestamps — cannot run provenance test")
    else:
        mism = [(t, newmap[t], exmap[t]) for t in common
                if any(newmap[t][i] != exmap[t][i] for i in range(1, 6))]
        allowed = [m for m in mism if m[0] in NAMED_EXCEPTIONS]
        disallowed = [m for m in mism if m[0] not in NAMED_EXCEPTIONS]
        verdict = "PASS" if not disallowed else "FAIL — STOP"
        print(f"  total overlap mismatches   : {len(mism)}")
        print(f"  named-exception mismatches : {len(allowed)}")
        for t, a, b in allowed:
            print(f"     [allowed] {iso(t)}  new={a[1:]}  existing={b[1:]}  ({NAMED_EXCEPTIONS[t]})")
        print(f"  DISALLOWED mismatches      : {len(disallowed)}")
        print(f"  >>> VERIFICATION 0 VERDICT : {verdict} <<<")
        mism = disallowed  # only unexpected ones flow into the detailed breakdown below
        # coverage of the existing file by the new file
        missing_from_new = [t for t in exmap if t not in tset]
        print(f"  existing bars              : {len(ex)}")
        print(f"  overlap range              : {iso(common[0])} -> {iso(common[-1])}")
        print(f"  overlap bars compared      : {len(common)}")
        print(f"  existing bars NOT in new   : {len(missing_from_new)}")
        print(f"  OHLCV mismatches (EXACT)   : {len(mism)}   ({len(mism)/len(common)*100:.3f}% of overlap)")
        if mism:
            print("  !! NON-ZERO. GATE: report and STOP. Do NOT correct, do NOT choose a version.")
            # --- field-level breakdown (reporting only, no modification) ---
            FIELDS = ["open", "high", "low", "close", "volume"]
            field_diff = {f: 0 for f in FIELDS}
            maxdiff = {f: 0.0 for f in FIELDS}
            only = {f: 0 for f in FIELDS}   # differs in exactly this one field
            price_only = vol_only = price_and_vol = 0
            by_year = {}
            for t, a, b in mism:
                which = [i for i in range(1, 6) if a[i] != b[i]]
                for i in which:
                    field_diff[FIELDS[i-1]] += 1
                    maxdiff[FIELDS[i-1]] = max(maxdiff[FIELDS[i-1]], abs(a[i]-b[i]))
                if len(which) == 1:
                    only[FIELDS[which[0]-1]] += 1
                pset = set(which) & {1, 2, 3, 4}
                if pset and 5 in which:
                    price_and_vol += 1
                elif pset:
                    price_only += 1
                elif which == [5]:
                    vol_only += 1
                y = datetime.fromtimestamp(t, tz=timezone.utc).year
                by_year[y] = by_year.get(y, 0) + 1
            print("  field-level breakdown:")
            for f in FIELDS:
                print(f"     {f:7s}: {field_diff[f]:4d} bars differ   max|delta|={maxdiff[f]:.4f}   (only-this-field: {only[f]})")
            print(f"  category: volume-only={vol_only}   price-only={price_only}   price+volume={price_and_vol}")
            print(f"  by year : " + ", ".join(f"{y}:{by_year[y]}" for y in sorted(by_year)))
            print("  sample mismatches:")
            for t, a, b in mism[:12]:
                print(f"     {iso(t)}  new={a[1:]}  existing={b[1:]}")
        else:
            print("  ZERO mismatches — extended file supersedes the existing cleanly (same source).")

    # ---- CHECK 2: COVERAGE MAP ----
    print("\n[CHECK 2] COVERAGE MAP — bars per UTC hour")
    byhour = {h: 0 for h in range(24)}
    for t in times:
        byhour[datetime.fromtimestamp(t, tz=timezone.utc).hour] += 1
    mx = max(byhour.values())
    for h in range(24):
        bar = "#" * int(40 * byhour[h] / mx)
        flag = "  <-- maintenance gap" if byhour[h] < 0.5 * mx else ""
        print(f"  {h:02d}:00 UTC  {byhour[h]:8d}  {bar}{flag}")

    # ---- CHECK 3: GAPS ----
    print("\n[CHECK 3] GAPS (missing intervals > one bar; weekends separate)")
    wk, iw = [], []
    for i in range(1, len(times)):
        d = times[i] - times[i - 1]
        if d > step:
            prev = datetime.fromtimestamp(times[i - 1], tz=timezone.utc)
            (wk if (prev.weekday() == 4 or d >= 47 * 3600) else iw).append((times[i-1], times[i], d))
    print(f"  weekend gaps               : {len(wk)}")
    print(f"  intra-week gaps > 1 bar    : {len(iw)}")
    iw.sort(key=lambda x: -x[2])
    print("  longest 15 intra-week gaps :")
    for a, b, d in iw[:15]:
        print(f"     {iso(a)} -> {iso(b)}   {d/60:.0f} min  ({d//step} bars missing)")

    # ---- CHECK 4: INTEGRITY ----
    print("\n[CHECK 4] INTEGRITY")
    print(f"  sha256         : {sha256(args.new)}")
    print(f"  bars           : {len(new)}")
    print(f"  distinct times : {len(tset)}   (duplicates: {len(times) - len(tset)})")
    print(f"  first bar      : {times[0]}  {iso(times[0])}")
    print(f"  last  bar      : {times[-1]}  {iso(times[-1])}")
    print(f"  span           : {(times[-1]-times[0])/86400/365.25:.2f} years")

    # ---- CHECK 5: ANOMALIES ----
    print("\n[CHECK 5] ANOMALIES — high amplitude on low volume")
    ranges = sorted(b[2] - b[3] for b in new)
    vols = sorted(b[5] for b in new)
    r_hi = ranges[int(0.999 * len(ranges))]
    v_lo = vols[int(0.05 * len(vols))]
    generic = [b for b in new if (b[2] - b[3]) >= r_hi and b[5] <= v_lo]
    sig = [b for b in new if 120 <= (b[2] - b[3]) <= 136 and 748 <= b[5] <= 3980]
    print(f"  generic (range>=p99.9 [{r_hi:.3f}] AND vol<=p5 [{v_lo:.0f}]) : {len(generic)}")
    print(f"  documented M15 signature (range 120-136 @ vol 748-3980)  : {len(sig)}")
    for b in generic[:8]:
        print(f"     {iso(b[0])}  range={b[2]-b[3]:.3f}  vol={b[5]:.0f}")

    # ---- CHECK 6: BAR AMPLITUDE per session ----
    print("\n[CHECK 6] BAR AMPLITUDE (high-low) per session")
    bysess = {}
    for b in new:
        h = datetime.fromtimestamp(b[0], tz=timezone.utc).hour
        bysess.setdefault(session(h), []).append(b[2] - b[3])
    print(f"  {'session':8s} {'n':>9s} {'median':>10s} {'IQR (25-75)':>20s}")
    for s in ("asia", "london", "ny", "late"):
        xs = sorted(bysess.get(s, []))
        if not xs:
            continue
        q1, q3 = xs[int(0.25 * len(xs))], xs[int(0.75 * len(xs))]
        print(f"  {s:8s} {len(xs):9d} {st.median(xs):10.3f}   [{q1:8.3f}, {q3:8.3f}]")

    # ---- CHECK 7: REGIME COVERAGE (M15) ----
    if args.regime:
        print("\n[CHECK 7] REGIME COVERAGE — descriptive swing map (monthly closes, 15% reversal)")
        print("  Descriptive only: no indicator/edge, no hypothesis. For split pre-registration.")
        legs = regime_map(new)
        print(f"  {'from':12s} {'to':12s} {'start$':>9s} {'end$':>9s} {'chg%':>8s}  regime")
        for t0, t1, p0, p1, pct, lab in legs:
            print(f"  {iso(t0)[:10]:12s} {iso(t1)[:10]:12s} {p0:9.1f} {p1:9.1f} {pct:+8.1f}  {lab}")
        # calendar-year closes for grounding
        yc = {}
        for t, o, h, l, c, v in new:
            yc[datetime.fromtimestamp(t, tz=timezone.utc).year] = c
        print("  year-end closes:", ", ".join(f"{y}:{yc[y]:.0f}" for y in sorted(yc)))

    print("\n" + "=" * 78)
    print("END OF REPORT — nothing integrated, nothing modified.")
    print("=" * 78)


if __name__ == "__main__":
    main()
