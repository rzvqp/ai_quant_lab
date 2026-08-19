"""Benchmark RangeSemanticEngineV3 (0.4.0) — cost per-bară MĂRGINIT (N1 O(1)/460 + V3 O(1) amortizat/bară,
vezi fix-ul medianei incrementale din `_RunningMedian`: fără el, un segment lung era O(n^2) pe durata lui de
viață — verificat empiric și corectat înainte de acest benchmark).

Datele reale XAUUSD M15 sunt SIGILATE ⇒ serie sintetică deterministă, structurată să exercite explicit toate
căile: range (oscilație+touches) => ESTABLISHED, breach+reintrare => SWEEP, breach susținut => BREAKOUT,
drift monoton periodic => CHANNEL. Măsoară wall/CPU/bars-sec/scaling/mem + overhead snapshot/restore.
Țintă: sub 4h la 355.696 bare, scalare ~liniară (NU pătratică — asta e exact ce verifică acest benchmark).
"""
from __future__ import annotations

import ctypes
import json
import sys
import time
from ctypes import wintypes

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import RangeSemanticEngineV3, RangeConfigV3

Bar = r.Bar
FULL = 355_696


def synth_bars(n: int) -> list:
    """Ciclu de 96 bare: 40 oscilație (range) + 24 breach/reintrare (sweep) + 16 rupere susținută (breakout)
    + 16 drift monoton (canal) — determinist din index, fără Date/random."""
    bars = []
    base = 2400.0
    for i in range(n):
        cyc = i % 96
        if cyc < 40:
            phase = cyc % 8
            amp = [8, 16, 20, 12, -4, -16, -20, -8][phase]
            c = base + amp; h = c + 3 + (2 if phase == 2 else 0); l = c - 3 - (2 if phase == 6 else 0)
        elif cyc < 64:
            sub = cyc - 40
            if sub < 12:
                c = base - 25 - sub * 0.5; h = c + 1.5; l = c - 1.5 - (3 if sub == 0 else 0)
            else:
                c = base + 15 - (sub - 12) * 0.3; h = c + 1.5; l = c - 1.5
        elif cyc < 80:
            c = base + 40 + (cyc - 64) * 1.2; h = c + 3; l = c - 3
        else:
            c = base + (cyc - 80) * 2.0; h = c + 1.5; l = c - 1.5
        o = c - 1
        bars.append(Bar(symbol="XAUUSD", ts_open=i * 900, ts_close=(i + 1) * 900,
                        open=round(o, 3), high=round(h, 3), low=round(l, 3), close=round(c, 3), volume=100.0))
    return bars


def peak_ws_mb() -> float:
    class PMC(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    pmc = PMC(); pmc.cb = ctypes.sizeof(PMC)
    k32 = ctypes.windll.kernel32; k32.GetCurrentProcess.restype = wintypes.HANDLE
    g = ctypes.windll.psapi.GetProcessMemoryInfo
    g.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]; g.restype = wintypes.BOOL
    g(k32.GetCurrentProcess(), ctypes.byref(pmc), pmc.cb)
    return round(pmc.PeakWorkingSetSize / 1024 / 1024, 1)


def bench(n: int) -> dict:
    bars = synth_bars(n)
    cfg = RangeConfigV3(K=4, N=8, w_atr=0.5, acknowledge_construction_only=True, d_min_bars=24,
                        segment_history_limit=64)
    eng = RangeSemanticEngineV3(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                implementation_commit=IC, range_config=cfg)
    w0, c0 = time.perf_counter(), time.process_time()
    led = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0
    s0 = time.perf_counter(); snap = eng.snapshot(); snap_t = time.perf_counter() - s0
    eng2 = RangeSemanticEngineV3(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                 implementation_commit=IC, range_config=cfg)
    r0 = time.perf_counter(); eng2.restore(snap); rest_t = time.perf_counter() - r0
    return {"bars": n, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3), "bars_per_sec": round(n / wall, 1),
            "us_per_bar": round(wall / n * 1e6, 2), "run_hash": led.run_hash[:12], "n_guards": led.n_guards,
            "events_total": sum(len(rec.events) for rec in led.records),
            "confirmed_segments": len(led.confirmed_segments),
            "snapshot_s": round(snap_t, 6), "restore_s": round(rest_t, 6), "peak_ws_mb": peak_ws_mb()}


def main() -> None:
    raw = sys.argv[1:]
    out = None; args = []; skip = False
    for i, a in enumerate(raw):
        if skip:
            skip = False; continue
        if a == "--out":
            out = raw[i + 1] if i + 1 < len(raw) else None; skip = True; continue
        if a.startswith("--"):
            continue
        args.append(a)
    sizes = [int(a) for a in args] if args else [20_000, 100_000, FULL]
    results = [bench(n) for n in sizes]
    for res in results:
        print(json.dumps(res)); sys.stdout.flush()
    summary = {"results": results}
    full = next((x for x in results if x["bars"] == FULL), None)
    if full:
        summary["under_4h"] = full["wall_s"] < 4 * 3600
    if len(results) >= 2:
        a, b = results[0], results[-1]
        summary["linear_index"] = round((b["wall_s"] / a["wall_s"]) / (b["bars"] / a["bars"]), 3)
    print("SUMMARY " + json.dumps(summary))
    if out:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print("WROTE " + out)


if __name__ == "__main__":
    main()
