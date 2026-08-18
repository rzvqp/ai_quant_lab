"""Benchmark comparativ SCURT 0.3.0 vs 0.3.1 — delta e STRICT de configurație (w_atr/s_max), acelasi cod
(`RangeStateProducerV2`/`N1IncrementalReplayEngine`, 0.3.0, NEATINS, reutilizat literal de 0.3.1). Conform
mandatului: „nu repeta inutil o regresie de 6 ore" — fără rulare completă 355.696 (rezervată pt. o schimbare de
algoritm, care NU s-a întâmplat aici). Scop: dovedește operații/O(n)/timp/memorie NESCHIMBATE structural.
"""
from __future__ import annotations

import ctypes
import json
import sys
import time
from ctypes import wintypes

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import RangeStateReplayEngineV2, RangeConfigV2, RangeStateReplayEngineV2Pinned, RangeConfigV2Pinned

Bar = r.Bar


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


def bench_030(n: int) -> dict:
    bars = synth_bars(n)
    cfg = RangeConfigV2.multiday(w_atr=0.25, s_max=0.15, d_min_bars=96)
    eng = RangeStateReplayEngineV2(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                   implementation_commit=IC, range_config=cfg)
    w0, c0 = time.perf_counter(), time.process_time()
    led = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0
    return {"version": "0.3.0", "bars": n, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3),
            "bars_per_sec": round(n / wall, 1), "us_per_bar": round(wall / n * 1e6, 2),
            "n_guards": led.n_guards, "peak_ws_mb": peak_ws_mb()}


def bench_031(n: int) -> dict:
    bars = synth_bars(n)
    cfg = RangeConfigV2Pinned.multiday()   # w_atr=0.30 canonical, s_max=0.60 derived, d_min_bars=96 default
    eng = RangeStateReplayEngineV2Pinned(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                         implementation_commit=IC, range_config=cfg)
    w0, c0 = time.perf_counter(), time.process_time()
    led = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0
    return {"version": "0.3.1", "bars": n, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3),
            "bars_per_sec": round(n / wall, 1), "us_per_bar": round(wall / n * 1e6, 2),
            "n_guards": led.n_guards, "peak_ws_mb": peak_ws_mb()}


def main() -> None:
    sizes = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else [5_000, 20_000]
    results = []
    for n in sizes:
        r030 = bench_030(n); results.append(r030); print(json.dumps(r030)); sys.stdout.flush()
        r031 = bench_031(n); results.append(r031); print(json.dumps(r031)); sys.stdout.flush()
    # verdict de scalare per versiune (2 puncte -> linear_index) + delta relativ intre versiuni la fiecare marime
    by_ver = {"0.3.0": [x for x in results if x["version"] == "0.3.0"],
             "0.3.1": [x for x in results if x["version"] == "0.3.1"]}
    summary = {"results": results}
    for ver, rows in by_ver.items():
        if len(rows) >= 2:
            a, b = rows[0], rows[-1]
            li = round((b["wall_s"] / a["wall_s"]) / (b["bars"] / a["bars"]), 3)
            summary[f"linear_index_{ver}"] = li
    deltas = []
    for n in sizes:
        r030 = next(x for x in results if x["version"] == "0.3.0" and x["bars"] == n)
        r031 = next(x for x in results if x["version"] == "0.3.1" and x["bars"] == n)
        deltas.append({"bars": n, "wall_ratio_031_over_030": round(r031["wall_s"] / r030["wall_s"], 3),
                       "us_per_bar_030": r030["us_per_bar"], "us_per_bar_031": r031["us_per_bar"]})
    summary["deltas"] = deltas
    print("SUMMARY " + json.dumps(summary))


if __name__ == "__main__":
    main()
