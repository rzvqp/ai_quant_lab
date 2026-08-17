"""Benchmark N1 INCREMENTAL (0.1.1) — wall/CPU/memory/bars-sec/scaling/ledger-size/snapshot-overhead.

Ținta mandatului: replay canonic până la 355.696 bare SUB 4 ore pe aceeași mașină. Datele reale XAUUSD M15
sunt SIGILATE (interzis accesul) — benchmark-ul de PERFORMANȚĂ folosește o serie sintetică deterministă de
ACEEAȘI dimensiune, cu structură reală (swing-uri/rupturi), astfel încât căile swing/break/exp/comp să fie
exercitate. Paritatea SEMANTICĂ e dovedită separat (tests/test_incremental.py) pe fixture-uri + adversarial.

Rulare:  python tools/benchmark_incremental.py [size1 size2 ...] [--out results.json]
"""
from __future__ import annotations

import ctypes
import json
import random
import sys
import time
from ctypes import wintypes

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import N1IncrementalReplayEngine

Bar = r.Bar
FULL = 355_696  # dimensiunea reală a datasetului Alpha (blocaj O(n²) ~ 20+ zile în 0.1.0)


def synth_bars(n: int, seed: int = 20260818) -> list:
    """Serie OHLC deterministă (random-walk cu structură): tendințe + reversări ⇒ swing-uri și rupturi reale."""
    rng = random.Random(seed)
    bars = []
    price = 2400.0
    drift = 0.0
    for i in range(n):
        if i % 137 == 0:                      # schimbare periodică de regim ⇒ structură (BOS/CHoCH)
            drift = rng.uniform(-0.6, 0.6)
        step = drift + rng.uniform(-1.0, 1.0)
        o = price
        c = max(1.0, price + step)
        hi = max(o, c) + abs(rng.uniform(0.0, 0.8))
        lo = min(o, c) - abs(rng.uniform(0.0, 0.8))
        bars.append(Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
                        open=round(o, 3), high=round(hi, 3), low=round(lo, 3), close=round(c, 3), volume=100.0))
        price = c
    return bars


def peak_working_set_bytes() -> int:
    """PeakWorkingSetSize (RSS de vârf real al procesului) — zero overhead, Windows."""
    class PMC(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    k32 = ctypes.windll.kernel32
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    gpmi = ctypes.windll.psapi.GetProcessMemoryInfo
    gpmi.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    gpmi.restype = wintypes.BOOL
    gpmi(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
    return int(pmc.PeakWorkingSetSize)


def bench_one(n: int) -> dict:
    bars = synth_bars(n)
    eng = N1IncrementalReplayEngine(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                    implementation_commit=IC)
    w0, c0 = time.perf_counter(), time.process_time()
    ledger = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0
    # ledger size — serializare canonică a header + records
    payload = {"header": ledger.header(), "records": [rec.as_dict() for rec in ledger.records]}
    ledger_bytes = len(json.dumps(payload, default=str).encode("utf-8"))
    # snapshot/restore overhead (mărginit — nu re-rulează istoricul)
    s0 = time.perf_counter(); snap = eng.snapshot(); snap_t = time.perf_counter() - s0
    eng2 = N1IncrementalReplayEngine(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                     implementation_commit=IC)
    r0 = time.perf_counter(); eng2.restore(snap); restore_t = time.perf_counter() - r0
    return {
        "bars": n, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3),
        "bars_per_sec": round(n / wall, 1), "us_per_bar": round(wall / n * 1e6, 2),
        "ledger_records": ledger.bar_count, "ledger_bytes": ledger_bytes,
        "ledger_key": ledger.ledger_key,
        "snapshot_s": round(snap_t, 6), "restore_s": round(restore_t, 6),
        "peak_working_set_mb": round(peak_working_set_bytes() / 1024 / 1024, 1),
    }


def main() -> None:
    out = None
    raw = sys.argv[1:]
    argv: list[str] = []
    skip = False
    for i, a in enumerate(raw):
        if skip:
            skip = False
            continue
        if a == "--out":
            out = raw[i + 1] if i + 1 < len(raw) else None
            skip = True
            continue
        if a.startswith("--"):
            continue
        argv.append(a)
    sizes = [int(a) for a in argv] if argv else [20_000, 100_000, FULL]
    results = []
    for n in sizes:
        res = bench_one(n)
        results.append(res)
        print(json.dumps(res))
        sys.stdout.flush()
    # verdict de scalare + țintă
    full = next((x for x in results if x["bars"] == FULL), None)
    summary = {"results": results}
    if full:
        summary["full_run"] = full
        summary["under_4h"] = full["wall_s"] < 4 * 3600
        summary["projected_20_days_baseline_note"] = "0.1.0 O(n²) ~20+ zile; 0.1.1 măsurat mai jos"
    if len(results) >= 2:
        a, b = results[0], results[-1]
        ratio_bars = b["bars"] / a["bars"]
        ratio_wall = b["wall_s"] / a["wall_s"]
        summary["scaling_bars_ratio"] = round(ratio_bars, 2)
        summary["scaling_wall_ratio"] = round(ratio_wall, 2)
        summary["linear_index"] = round(ratio_wall / ratio_bars, 3)  # ~1.0 ⇒ O(n)
    print("SUMMARY " + json.dumps(summary))
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2, default=str)
        print("WROTE " + out)


if __name__ == "__main__":
    main()
