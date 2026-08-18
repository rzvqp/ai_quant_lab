"""Benchmark RangeStateReplayEngineV2 (0.3.0) — demonstrează că SPEC V2 (mediană + zonă + regresie pe fereastră
mărginită d_min_bars + contor descriptiv intern) NU reintroduce O(n²). Toate structurile sunt MĂRGINITE
(range_window pt. swing-uri, d_min_bars pt. regresie, HISTORY_HORIZON pt. N1) ⇒ cost O(bounded)/bară, deci
O(n) total pe replay. Date sintetice deterministe (real XAUUSD M15 e SIGILAT/interzis).
"""
from __future__ import annotations

import ctypes
import json
import sys
import time
from ctypes import wintypes

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import RangeStateReplayEngineV2, RangeConfigV2

Bar = r.Bar
FULL = 355_696


def synth_bars(n: int) -> list:
    bars = []
    base = 2400.0
    for i in range(n):
        cyc = i % 40
        if cyc < 32:
            phase = (cyc % 8)
            amp = [8, 16, 20, 12, -4, -16, -20, -8][phase]
            c = base + amp
            h = c + 3 + (2 if phase == 2 else 0)
            l = c - 3 - (2 if phase == 6 else 0)
        else:
            c = base + 40 + (cyc - 32)
            h = c + 3; l = c - 3
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
    cfg = RangeConfigV2.multiday(d_min_bars=96)
    eng = RangeStateReplayEngineV2(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                   implementation_commit=IC, range_config=cfg)
    w0, c0 = time.perf_counter(), time.process_time()
    led = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0

    # observe_closed_bar izolat (nu replay_batch) — cost per-bară incremental
    eng_obs = RangeStateReplayEngineV2(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                       implementation_commit=IC, range_config=cfg)
    o0 = time.perf_counter()
    for b in bars[:min(2000, n)]:
        eng_obs.observe_closed_bar(b)
    observe_wall = time.perf_counter() - o0
    observe_bars = min(2000, n)

    s0 = time.perf_counter(); snap = eng.snapshot(); snap_t = time.perf_counter() - s0
    eng2 = RangeStateReplayEngineV2(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                    implementation_commit=IC, range_config=cfg)
    r0 = time.perf_counter(); eng2.restore(snap); rest_t = time.perf_counter() - r0
    return {"bars": n, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3), "bars_per_sec": round(n / wall, 1),
            "us_per_bar": round(wall / n * 1e6, 2),
            "observe_us_per_bar": round(observe_wall / observe_bars * 1e6, 2),
            "run_hash": led.run_hash[:12], "n_guards": led.n_guards,
            "events_total": sum(len(rec.events) for rec in led.records),
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
