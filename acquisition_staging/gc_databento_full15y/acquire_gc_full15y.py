#!/usr/bin/env python3
"""GC full-15y Databento acquisition (mandate ACQUIRE GC FULL 15Y DATASET, cap USD 25.00).

Reads DATABENTO_API_KEY from the environment ONLY (databento.Historical() auto-reads it). The key is
NEVER printed, logged, written, committed, or otherwise exposed. If the key is absent -> STOP.

Flow (mandate §3 cap enforcement is MANDATORY and mechanical):
  1. metadata.get_cost (READ-ONLY) for ohlcv-1m + definition + statistics.
  2. FINAL_TOTAL_COST = sum. If > 25.00 USD -> STOP, no paid request (PURCHASE_BLOCKED_COST_CAP=YES).
  3. If <= 25.00 -> download the three raw DBN streams to raw/, preserve exactly.
  4. Checksums -> GC_FULL15Y_RAW_MANIFEST.json (no credentials).

EXACT requests (do NOT broaden — mandate §1/§4/§5/§6):
  OHLCV      dataset=GLBX.MDP3 schema=ohlcv-1m   symbols=GC.v.0  stype_in=continuous  2011-07-26..2026-07-28(excl)
  definition dataset=GLBX.MDP3 schema=definition symbols=GC.FUT  stype_in=parent      (min GC identity scope)
  statistics dataset=GLBX.MDP3 schema=statistics symbols=GC.FUT  stype_in=parent      (OI/roll diagnostics)

Usage: python acquire_gc_full15y.py            # cost-recheck + (if <=cap) download
       python acquire_gc_full15y.py --dry-run  # cost-recheck ONLY, never download
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, sys

DATASET = "GLBX.MDP3"
START, END = "2011-07-26", "2026-07-28"   # Databento end is EXCLUSIVE -> includes all of 2026-07-27
CAP_USD = 25.00
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
REQUESTS = [
    {"name": "ohlcv",      "schema": "ohlcv-1m",   "symbols": ["GC.v.0"], "stype_in": "continuous",
     "file": "gc_ohlcv-1m_GC.v.0_2011-07-26_2026-07-28.dbn"},
    {"name": "definition", "schema": "definition", "symbols": ["GC.FUT"], "stype_in": "parent",
     "file": "gc_definition_GC.FUT_2011-07-26_2026-07-28.dbn"},
    {"name": "statistics", "schema": "statistics", "symbols": ["GC.FUT"], "stype_in": "parent",
     "file": "gc_statistics_GC.FUT_2011-07-26_2026-07-28.dbn"},
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="cost recheck only; never download")
    a = ap.parse_args()

    if not os.environ.get("DATABENTO_API_KEY"):
        print("STOP: DATABENTO_API_KEY not available in the environment (mandate §2). No request made.",
              file=sys.stderr)
        return 2
    import databento as db  # noqa: E402
    client = db.Historical()  # reads DATABENTO_API_KEY from env; key never touched by this code

    # ---- 1) READ-ONLY cost recheck (mandate §3) ----
    costs, total = {}, 0.0
    for r in REQUESTS:
        c = float(client.metadata.get_cost(
            dataset=DATASET, symbols=r["symbols"], schema=r["schema"], stype_in=r["stype_in"],
            start=START, end=END, mode="historical-streaming"))
        costs[r["name"]] = c
        total += c
        print(f"FINAL_{r['name'].upper()}_COST = {c:.6f} USD")
    print(f"FINAL_TOTAL_COST = {total:.6f} USD  (cap {CAP_USD:.2f})")

    if total > CAP_USD:
        print(f"PURCHASE_BLOCKED_COST_CAP = YES  ({total:.2f} > {CAP_USD:.2f}) -- STOP, no paid data requested.",
              file=sys.stderr)
        return 3
    if a.dry_run:
        print("COST_CAP_RESPECTED = YES; --dry-run -> no download.")
        return 0

    # ---- 2) download raw DBN, preserve exactly (mandate §4/§8) ----
    os.makedirs(RAW, exist_ok=True)
    lib_ver = getattr(db, "__version__", "unknown")
    manifest = {"vendor": "Databento", "dataset": DATASET,
                "download_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "databento_library_version": lib_ver, "cap_usd": CAP_USD,
                "final_costs_usd": costs, "final_total_cost_usd": round(total, 6), "files": []}
    for r in REQUESTS:
        path = os.path.join(RAW, r["file"])
        store = client.timeseries.get_range(
            dataset=DATASET, symbols=r["symbols"], schema=r["schema"], stype_in=r["stype_in"],
            start=START, end=END, path=path)  # writes raw DBN to disk
        sz = os.path.getsize(path)
        manifest["files"].append({
            "request": r["name"], "schema": r["schema"], "symbol_request": r["symbols"],
            "stype_in": r["stype_in"], "start": START, "end": END,
            "file_name": r["file"], "byte_size": sz, "sha256": sha256(path)})
        print(f"downloaded {r['name']}: {sz} bytes -> {r['file']}")

    with open(os.path.join(HERE, "GC_FULL15Y_RAW_MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("RAW_FILES_SHA256_VERIFIED = YES; manifest written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
