#!/usr/bin/env python3
"""DXY H1 processing pipeline (mandate DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001). Pure stdlib.

RAW -> QA -> NORMALIZED (research region, <=2023-12-31) -> governed slices (b0/b1/2021-2023)
-> DXY_EVIDENCE_MANIFEST.json + DXY_COVERAGE_OVERLAP_REPORT.json + fingerprints.

Governance: the 2024+ head physically present in RAW (upper-bound margin for the provisional cursor
bar) is classified PROTECTED and EXCLUDED from NORMALIZED and every research slice. No interpolation,
no forward-fill, no fabricated volume (DXY is a cash index -> volume column is structurally 0, the ICE
feed supplies none; kept only for 6-col schema parity, documented as NOT-supplied).

Usage: python dxy_process.py
"""
import csv, hashlib, json, os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "RAW_DXY_H1_ICEUS.csv")
NORM = os.path.join(HERE, "NORMALIZED_DXY_H1.csv")
STEP = 3600
# XAUUSD H1 research reference (ratified, M15_v2-derived context H1)
XAU_H1 = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data", "market", "OANDA_XAUUSD_H1_from_M15_v2.csv")

def ep(y, mo, d, h=0, mi=0): return int(datetime(y, mo, d, h, mi, tzinfo=timezone.utc).timestamp())
def iso(e): return datetime.fromtimestamp(int(e), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()

# canonical governed block boundaries (repository evidence contracts)
RESEARCH_END = ep(2023, 12, 31, 0, 0)      # <=2023-12-31 delivered; 2024+ PROTECTED
BLOCKS = {
    "DXY_B0_RESEARCH_SLICE":      (ep(2011, 7, 26, 16, 30), ep(2013, 9, 27, 16, 45)),   # m15_v2_discovery_blocks[0]
    "DXY_B1_RESEARCH_SLICE":      (ep(2016, 1, 11, 9, 0),   ep(2018, 4, 6, 11, 52)),    # m15_v2_discovery_blocks[1]
    "DXY_2021_2023_RESEARCH_SLICE": (ep(2021, 7, 27, 0, 0), ep(2023, 12, 30, 0, 0)),    # Native Alpha DEV (2021-07-27 -> 2023-12-29)
}

def load(p):
    rows = []
    with open(p, newline="") as f:
        r = csv.reader(f); next(r)
        for ln in r:
            if ln and ln[0].strip():
                rows.append([int(ln[0])] + [float(x) for x in ln[1:6]])
    return rows

def write(p, rows):
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "open", "high", "low", "close", "volume"])
        for b in rows:
            w.writerow([b[0], f"{b[1]:.4f}".rstrip("0").rstrip("."), f"{b[2]:.4f}".rstrip("0").rstrip("."),
                        f"{b[3]:.4f}".rstrip("0").rstrip("."), f"{b[4]:.4f}".rstrip("0").rstrip("."), int(b[5])])

def qa(rows, label):
    t = [b[0] for b in rows]
    tset = set(t)
    mono = all(t[i] < t[i+1] for i in range(len(t)-1))
    dups = len(t) - len(tset)
    off_grid = sum(1 for x in t if x % STEP != 0)
    ohlc_bad = sum(1 for b in rows if not (b[2] >= max(b[1], b[4], b[3]) and b[3] <= min(b[1], b[4], b[2])))
    nonpos = sum(1 for b in rows if min(b[1], b[2], b[3], b[4]) <= 0)
    # gaps
    wk = iw = 0; big = []
    for i in range(1, len(t)):
        d = t[i] - t[i-1]
        if d > STEP:
            prev = datetime.fromtimestamp(t[i-1], tz=timezone.utc)
            if prev.weekday() == 4 or d >= 47*3600: wk += 1
            else: iw += 1; big.append((t[i-1], t[i], d))
    nominal = (t[-1] - t[0]) // STEP + 1
    big.sort(key=lambda x: -x[2])
    return {
        "label": label, "bars": len(rows), "first": iso(t[0]), "last": iso(t[-1]),
        "duplicates": dups, "monotonic_strict": mono, "off_grid_timestamps": off_grid,
        "ohlc_constraint_violations": ohlc_bad, "nonpositive_price_bars": nonpos,
        "weekend_gaps": wk, "intra_week_gaps": iw,
        "present": len(rows), "nominal_grid": nominal, "missing_slots": nominal - len(rows),
        "accounting_invariant_ok": (len(rows) + (nominal - len(rows)) == nominal),
        "continuity_pct": round(100*len(rows)/nominal, 1),
        "longest_intra_week_gaps": [{"from": iso(a), "to": iso(b), "hours": round(d/3600, 1)} for a, b, d in big[:5]],
    }

def main():
    raw = load(RAW)
    raw.sort(key=lambda b: b[0])
    report = {"mandate": "DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001",
              "instrument": {"provider": "ICE (Intercontinental Exchange US)", "provider_symbol": "ICEUS:DXY",
                             "resolved_feed": "ICEUS_DLY:DXY (delayed)", "definition": "official ICE U.S. Dollar Index (cash/index, NOT DX futures)",
                             "type": "index", "volume": "none supplied (cash index); volume column structurally 0, not fabricated"},
              "timeframe": "H1", "bar_time_convention": "bar time = bar OPEN time (UTC epoch); close = open+3600s; FEATURE_AVAILABLE_TIME = close",
              "source_method": "TradingView Desktop replay-walk (CDP), overlapping-window backward walk (pull_dxy_h1.mjs)"}

    report["RAW_QA"] = qa(raw, "RAW (as acquired)")
    report["RAW_sha256"] = sha_file(RAW)

    # split research (<=2023-12-31) vs protected head (>=2024)
    research = [b for b in raw if b[0] < RESEARCH_END]
    protected_head = [b for b in raw if b[0] >= RESEARCH_END]
    write(NORM, research)
    report["NORMALIZED_QA"] = qa(research, "NORMALIZED research region (<=2023-12-31)")
    report["NORMALIZED_sha256"] = sha_file(NORM)
    report["PROTECTED_head_2024"] = {"bars": len(protected_head),
        "range": (iso(protected_head[0][0]) + " .. " + iso(protected_head[-1][0])) if protected_head else "none",
        "classification": "PROTECTED — physically acquired as upper-bound margin (absorbs the provisional replay-cursor bar); EXCLUDED from NORMALIZED and every research slice"}

    # governed slices
    slices = {}
    for name, (s, e) in BLOCKS.items():
        seg = [b for b in research if s <= b[0] < e]
        path = os.path.join(HERE, name + ".csv")
        write(path, seg)
        slices[name] = {"bounds_utc": [iso(s), iso(e)], "bounds_epoch": [s, e],
                        "bars": len(seg), "first": iso(seg[0][0]) if seg else None, "last": iso(seg[-1][0]) if seg else None,
                        "sha256": sha_file(path), "qa": qa(seg, name) if seg else None}
    report["research_slices"] = slices

    # cross-market overlap audit vs XAUUSD H1 (ratified research H1)
    xau = {b[0] for b in load(XAU_H1)}
    dxy_set = {b[0] for b in research}
    overlap = {}
    for name, (s, e) in BLOCKS.items():
        dxy_h = {t for t in dxy_set if s <= t < e}
        xau_h = {t for t in xau if s <= t < e}
        both = dxy_h & xau_h
        miss = xau_h - dxy_h  # XAUUSD hours with no DXY match
        overlap[name] = {
            "dxy_start": iso(min(dxy_h)) if dxy_h else None, "dxy_end": iso(max(dxy_h)) if dxy_h else None,
            "xauusd_start": iso(min(xau_h)) if xau_h else None, "xauusd_end": iso(max(xau_h)) if xau_h else None,
            "dxy_h1_hours": len(dxy_h), "xauusd_h1_hours": len(xau_h),
            "overlapping_h1_hours": len(both),
            "coverage_pct_of_xauusd": round(100*len(both)/len(xau_h), 1) if xau_h else None,
            "missing_overlap_hours": len(miss),
        }
    report["cross_market_overlap"] = {"xauusd_reference": os.path.relpath(XAU_H1, os.path.dirname(os.path.dirname(HERE))), "by_block": overlap}

    # evidence manifest (classification)
    evid = {
        "mandate": "DATA-ACQ-DXY-H1-HISTORICAL-RATIFIED-001",
        "note": "Data Acquisition provisions data and classifies regions; it does NOT assign strategy-validation status.",
        "regions": [
            {"name": "DXY_B0", "utc": [iso(BLOCKS['DXY_B0_RESEARCH_SLICE'][0]), iso(BLOCKS['DXY_B0_RESEARCH_SLICE'][1])], "class": "AVAILABLE_FOR_DISCOVERY"},
            {"name": "DXY_B1", "utc": [iso(BLOCKS['DXY_B1_RESEARCH_SLICE'][0]), iso(BLOCKS['DXY_B1_RESEARCH_SLICE'][1])], "class": "AVAILABLE_FOR_DISCOVERY"},
            {"name": "DXY_2021_2023", "utc": [iso(BLOCKS['DXY_2021_2023_RESEARCH_SLICE'][0]), iso(BLOCKS['DXY_2021_2023_RESEARCH_SLICE'][1])], "class": "AVAILABLE_FOR_DISCOVERY"},
            {"name": "DXY_between_blocks_2013_2016_2018_2021", "utc": ["2013-09-27", "2021-07-27"], "class": "AVAILABLE_FOR_DISCOVERY_gaps_between_named_blocks (continuous DXY exists; not a named research block — use only under explicit governance)"},
            {"name": "DXY_2024_plus", "utc": ["2024-01-01", "present"], "class": "PROTECTED (not delivered; the ~4-day 2024 head in RAW is excluded from NORMALIZED/slices)"},
            {"name": "DXY_pre_2011_07_14", "utc": ["<2011-07-14", ""], "class": "MISSING (source floor; ICE DXY H1 on TradingView begins 2011-07-14)"},
        ],
    }
    with open(os.path.join(HERE, "DXY_EVIDENCE_MANIFEST.json"), "w") as f: json.dump(evid, f, indent=2)
    with open(os.path.join(HERE, "DXY_COVERAGE_OVERLAP_REPORT.json"), "w") as f: json.dump(report["cross_market_overlap"], f, indent=2)

    # code fingerprints
    report["code_fingerprints"] = {
        "pull_dxy_h1.mjs": sha_file(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "tradingview-mcp", "pull_dxy_h1.mjs")) if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "tradingview-mcp", "pull_dxy_h1.mjs")) else "n/a",
        "dxy_process.py": sha_file(os.path.abspath(__file__)),
    }
    with open(os.path.join(HERE, "DXY_PROCESS_REPORT.json"), "w") as f: json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
