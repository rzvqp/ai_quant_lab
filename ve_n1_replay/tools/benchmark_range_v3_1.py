"""Benchmark RangeSemanticEngineV31 (0.4.1) — remediu §12 RT-RANGE-0004 (pantă OLS incrementală O(1)/bară).

Reutilizează `synth_bars()` din `tools/benchmark_range_v3.py` (0.4.0, NEATINS) BYTE-IDENTIC (import direct,
NU re-implementare) — aceeași metodologie exactă pt. o comparație corectă. Două moduri:

  --canonical : 355.696 bare, d_min_bars=96 (valoarea EXPLICITĂ cerută de mandatul 0.4.1 §7 -- NOTĂ: diferă
                de d_min_bars=24 folosit în benchmark-ul canonic PROPRIU al lui 0.4.0, care a măsurat 30m41s;
                96 e o configurație STRICT mai grea pt. varianta O(d_min_bars) veche -- deci un benchmark
                canonic mai conservator, nu unul slăbit). Țintă: sub 4 ore.
  --adversarial : d_min_bars=200000 (fără plafon introdus -- vezi mandatul §3), 250.000 bare = 200.000 pt.
                umplerea COMPLETĂ a ferestrei + 50.000 coadă POST-umplere, ca să demonstreze stabilitatea
                costului/bară DUPĂ umplere (mandat §7), nu doar un microbenchmark.
"""
from __future__ import annotations

import json
import sys
import time

sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay")         # repo root -- pachetul local, nu site-packages
sys.path.insert(0, r"C:\Users\MEDION GAMING\ai_quant_lab-wp5b\ve_n1_replay\tools")   # sibling script (0.4.0, NEATINS)
from benchmark_range_v3 import synth_bars, peak_ws_mb, FULL   # noqa: E402  (0.4.0, NEATINS -- date reutilizate)

import ve_n1_replay as r
from ve_n1_replay.version import RAW_AXES_BUILDER_IMPL_COMMIT as IC
from ve_n1_replay import RangeSemanticEngineV31, RangeConfigV31

ADVERSARIAL_D_MIN = 200_000
ADVERSARIAL_TOTAL = ADVERSARIAL_D_MIN + 50_000   # umplere completă + coadă post-umplere de 50k


def _engine(d_min_bars: int) -> RangeSemanticEngineV31:
    cfg = RangeConfigV31(K=4, N=8, w_atr=0.5, acknowledge_construction_only=True, d_min_bars=d_min_bars,
                         segment_history_limit=64)
    return RangeSemanticEngineV31(symbol="XAUUSD", timeframe="15m", bar_interval_seconds=900,
                                  implementation_commit=IC, range_config=cfg)


def bench(n: int, d_min_bars: int) -> dict:
    bars = synth_bars(n)
    eng = _engine(d_min_bars)
    w0, c0 = time.perf_counter(), time.process_time()
    led = eng.replay_batch(bars)
    wall, cpu = time.perf_counter() - w0, time.process_time() - c0
    s0 = time.perf_counter(); snap = eng.snapshot(); snap_t = time.perf_counter() - s0
    eng2 = _engine(d_min_bars)
    r0 = time.perf_counter(); eng2.restore(snap); rest_t = time.perf_counter() - r0
    return {"bars": n, "d_min_bars": d_min_bars, "wall_s": round(wall, 3), "cpu_s": round(cpu, 3),
            "bars_per_sec": round(n / wall, 1), "us_per_bar": round(wall / n * 1e6, 2),
            "run_hash": led.run_hash[:12], "n_guards": led.n_guards,
            "events_total": sum(len(rec.events) for rec in led.records),
            "confirmed_segments": len(led.confirmed_segments),
            "snapshot_s": round(snap_t, 6), "restore_s": round(rest_t, 6), "peak_ws_mb": peak_ws_mb()}


def bench_adversarial_with_stability_split(n_total: int, d_min_bars: int, fill_at: int) -> dict:
    """Măsoară SEPARAT costul/bară în faza de umplere (0..fill_at) vs. coada POST-umplere (fill_at..n_total)
    -- demonstrează stabilitatea, nu doar timpul total (mandat §7)."""
    bars = synth_bars(n_total)
    eng = _engine(d_min_bars)
    w0 = time.perf_counter()
    for b in bars[:fill_at]:
        eng.observe_closed_bar(b)
    fill_wall = time.perf_counter() - w0
    w1 = time.perf_counter()
    for b in bars[fill_at:]:
        eng.observe_closed_bar(b)
    tail_wall = time.perf_counter() - w1
    total_wall = fill_wall + tail_wall
    tail_n = n_total - fill_at
    return {"bars": n_total, "d_min_bars": d_min_bars, "fill_at": fill_at,
            "fill_phase_wall_s": round(fill_wall, 3), "fill_phase_us_per_bar": round(fill_wall / fill_at * 1e6, 3),
            "post_fill_wall_s": round(tail_wall, 3),
            "post_fill_us_per_bar": round(tail_wall / tail_n * 1e6, 3) if tail_n else None,
            "total_wall_s": round(total_wall, 3), "peak_ws_mb": peak_ws_mb()}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "calibrate"
    out = None
    positional = []
    rest = sys.argv[2:]
    i = 0
    while i < len(rest):
        if rest[i] == "--out":
            out = rest[i + 1] if i + 1 < len(rest) else None
            i += 2
            continue
        positional.append(rest[i])
        i += 1

    if mode == "calibrate":
        sizes = [int(a) for a in positional] or [2000, 5000]
        results = [bench(n, ADVERSARIAL_D_MIN) for n in sizes]
        for res in results:
            print(json.dumps(res)); sys.stdout.flush()
        return

    if mode == "canonical":
        sizes = [int(a) for a in positional] or [2_000, 20_000, FULL]
        results = [bench(n, 96) for n in sizes]
        for res in results:
            print(json.dumps(res)); sys.stdout.flush()
        summary: dict = {"mode": "canonical", "d_min_bars": 96, "results": results}
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
        return

    if mode == "adversarial":
        res = bench_adversarial_with_stability_split(ADVERSARIAL_TOTAL, ADVERSARIAL_D_MIN, ADVERSARIAL_D_MIN)
        print(json.dumps(res))
        summary = {"mode": "adversarial", "d_min_bars": ADVERSARIAL_D_MIN, "result": res}
        # ~9h defect (0.4.0, citat Red Team) e considerat ÎNCHIS dacă rularea COMPLETĂ (umplere+coadă) la
        # d_min_bars=200000 rămâne sub aceeași țintă de 4h folosită pt. rularea canonică.
        summary["defect_closed_under_4h"] = res["total_wall_s"] < 4 * 3600
        print("SUMMARY " + json.dumps(summary))
        if out:
            with open(out, "w", encoding="utf-8") as fh:
                json.dump(summary, fh, indent=2)
            print("WROTE " + out)
        return

    raise SystemExit(f"mod necunoscut: {mode!r} (folosește calibrate|canonical|adversarial)")


if __name__ == "__main__":
    main()
