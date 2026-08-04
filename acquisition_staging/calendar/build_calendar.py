#!/usr/bin/env python3
"""ForexFactory economic-calendar normalizer + inventory stats. Pure stdlib.

Canonical source = the JSON export (carries an EXPLICIT per-record UTC offset, e.g.
2026-08-07T08:30:00-04:00). The CSV/XML exports render the SAME instants in UTC but
WITHOUT any in-file timezone marker (a trap: "12:30pm" looks naive but is UTC). We use
JSON for the authoritative instant and JOIN the CSV to attach the stable event URL/id,
reconciling UTC across every event as a verification.

Emits a normalized table (timestamp normalized to UTC, convention written in header
comment) and prints usage-filter stats. NO filtering at acquisition — all currencies,
all impacts. There is NO 'actual' field and NO revision flag in the export (reported).

Usage: python build_calendar.py --json <j> --csv <c> --out <normalized.csv>
"""
import argparse, csv, hashlib, json, re
from collections import Counter
from datetime import datetime, timezone, timedelta


def parse_json_dt(s):
    # ISO-8601 with explicit offset, e.g. 2026-08-07T08:30:00-04:00
    dt = datetime.fromisoformat(s)
    return dt  # tz-aware


def parse_csv_dt(date_s, time_s):
    # date MM-DD-YYYY ; time like '12:30pm' / '9:15am' ; treat as UTC (verified vs JSON)
    date_s = date_s.strip()
    time_s = time_s.strip()
    if not re.match(r"^\d{1,2}:\d{2}(am|pm)$", time_s, re.I):
        return None  # 'All Day', 'Tentative', 'Day 1', etc.
    dt = datetime.strptime(f"{date_s} {time_s}", "%m-%d-%Y %I:%M%p")
    return dt.replace(tzinfo=timezone.utc)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    jrows = json.load(open(a.json, encoding="utf-8"))
    # index CSV by (title, country) -> list of (utc_dt, url, raw_time)
    curl = {}
    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            k = (r["Title"], r["Country"])
            curl.setdefault(k, []).append((parse_csv_dt(r["Date"], r["Time"]), r.get("URL", ""), r["Time"]))

    out = []
    tz_recon_ok = tz_recon_bad = untimed = 0
    for r in jrows:
        dt = parse_json_dt(r["date"])
        utc = dt.astimezone(timezone.utc)
        offset = dt.strftime("%z")  # e.g. -0400
        k = (r["title"], r["country"])
        url = ""
        # match CSV row with equal UTC instant (verifies CSV==UTC systematically)
        for cdt, curl_, craw in curl.get(k, []):
            if cdt is not None and cdt == utc:
                url = curl_
                tz_recon_ok += 1
                break
            elif cdt is None:
                untimed += 1
        else:
            if any(c[0] is not None for c in curl.get(k, [])):
                tz_recon_bad += 1
        out.append({
            "datetime_utc": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "date_ny": dt.strftime("%Y-%m-%d"),
            "time_ny": dt.strftime("%H:%M"),
            "src_offset": offset,
            "currency": r["country"],
            "impact": r["impact"],
            "event": r["title"],
            "forecast": r.get("forecast", ""),
            "previous": r.get("previous", ""),
            "url": url,
        })
    out.sort(key=lambda x: x["datetime_utc"])

    cols = ["datetime_utc", "date_ny", "time_ny", "src_offset",
            "currency", "impact", "event", "forecast", "previous", "url"]
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        # convention comment line is NOT written into the CSV body to keep it machine-clean;
        # convention is documented in the report + column names (datetime_utc is authoritative).
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in out:
            w.writerow(row)

    print("=" * 78)
    print("FOREXFACTORY CALENDAR — normalized snapshot (thisweek) + inventory stats")
    print("=" * 78)
    print(f"  events            : {len(out)}")
    print(f"  sha256(normalized): {sha256(a.out)}")
    print(f"  UTC reconciliation (JSON offset vs CSV time): matched {tz_recon_ok}, "
          f"mismatched {tz_recon_bad}  -> {'PASS' if tz_recon_bad == 0 else 'FAIL'}")
    print(f"  untimed events (All Day/Tentative, no clock): {untimed} occurrences in CSV")

    # ---- usage-filter stats (filter is at USE, storage is complete) ----
    usd = [r for r in out if r["currency"] == "USD"]
    usd_high = [r for r in usd if r["impact"] == "High"]
    usd_med = [r for r in usd if r["impact"] == "Medium"]
    print("\n[USAGE FILTER PREVIEW — USD, High/Medium (this week sample; N weeks needed for a true mean)]")
    print(f"  USD total        : {len(usd)}")
    print(f"  USD High / week  : {len(usd_high)}")
    print(f"  USD Medium / week: {len(usd_med)}")

    print("\n  USD High events (ET clock — check 8:30 / 10:00 NY clustering):")
    for r in usd_high:
        print(f"     {r['date_ny']} {r['time_ny']} ET  (= {r['datetime_utc']})  {r['event']}")
    print("  USD Medium events (ET):")
    for r in usd_med:
        print(f"     {r['date_ny']} {r['time_ny']} ET  (= {r['datetime_utc']})  {r['event']}")

    print("\n[HOUR-OF-DAY DISTRIBUTION — USD High+Medium, ET clock]")
    hh = Counter(r["time_ny"] for r in usd_high + usd_med)
    for t in sorted(hh):
        print(f"     {t} ET : {hh[t]}")

    print("\n[IMPACT / CURRENCY BREAKDOWN — full snapshot, no filter]")
    print("  impact:", dict(Counter(r["impact"] for r in out)))
    print("  currency:", dict(Counter(r["currency"] for r in out)))
    print("=" * 78)


if __name__ == "__main__":
    main()
