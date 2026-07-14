"""Large-scale replay benchmark + validation harness for Market Scanner v1.

Standalone dev tool (Phase 6.1 validation) -- NOT part of the shipped module, NOT imported by
``ai_trader.market_scanner`` or by any test in ``tests/``. Run directly:

    venv\\Scripts\\python -m ai_trader.market_scanner.benchmarks.bench_market_scanner [options]

Generates a realistic weekday-only (Mon-Fri) synthetic OHLCV dataset with periodic simulated feed
outages and replays it through the full ``ingest_bar`` / ``advance_clock`` / ``build_context`` cycle
with M15+H1+H4+D1 timeframes, logging throughput progress as it goes.

IMPORTANT -- ``tracemalloc`` pitfall (root-caused 2026-07-14, see MARKET_SCANNER_VALIDATION_REPORT.md
at the repo root for the full writeup): an earlier version of this harness called
``tracemalloc.start()`` unconditionally around the entire replay loop. At small/medium scale (up to
~90K contexts) this was barely noticeable. At ~217K contexts (2yr x 3 symbols) it caused the run to
become **catastrophically slow** -- confirmed by direct A/B measurement: the identical replay
completed in 204s with tracemalloc off, and had not finished its first 2,000-context checkpoint after
5.5+ minutes with tracemalloc on (while still visibly consuming CPU, i.e. not deadlocked -- just
pathologically slow). This was mistaken for a Market Scanner defect in the previous session and the
run was left going for 4+ hours before being killed; it was a harness artifact, not a scanner defect
-- the same measured lookahead-safety (0 violations) and throughput curve (mildly, linearly degrading
as rolling windows fill toward their cap) hold at every scale once tracemalloc is off. Because of
this, ``--tracemalloc`` here defaults to OFF and is intended for small diagnostic runs only (the
script prints a loud warning if you combine it with a large scale).
"""

from __future__ import annotations

import argparse
import gc
import random
import sys
import time
import tracemalloc
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from ai_trader.market_scanner import AdapterConfig, Mode, Requirements, SymbolMeta  # noqa: E402
from ai_trader.market_scanner.config import ScannerConfig  # noqa: E402
from ai_trader.market_scanner.scanner import MarketScanner  # noqa: E402
from ai_trader.market_scanner.types import RawBar  # noqa: E402

_M15, _H1, _H4, _D1 = 900, 3600, 14400, 86400
_BARS_PER_DAY = 96  # 24h / 15min (full 24h weekday sessions, FX-style)

# Scale beyond which running with --tracemalloc prints a warning (see module docstring).
_TRACEMALLOC_SAFE_CONTEXT_CEILING = 90_000


@dataclass
class Tick:
    o: float
    h: float
    l: float
    c: float


def gen_weekday_m15(n_weekdays: int, seed: int, start_price: float = 2000.0) -> tuple[list[Tick], list[int]]:
    """Generate M15 ticks for ``n_weekdays`` consecutive Mon-Fri trading days (skips Sat/Sun),
    starting at epoch (Thursday). Returns ``(ticks, ts_opens)`` both aligned 1:1."""
    rng = random.Random(seed)
    ticks: list[Tick] = []
    ts_opens: list[int] = []
    price = start_price
    day_idx = 0
    produced_days = 0
    while produced_days < n_weekdays:
        dow = datetime.fromtimestamp(day_idx * _D1, tz=UTC).weekday()
        if dow < 5:
            base = day_idx * _D1
            for b in range(_BARS_PER_DAY):
                o = price
                drift = rng.uniform(-1.2, 1.2)
                c = max(1.0, o + drift)
                h = max(o, c) + rng.uniform(0.05, 0.8)
                l = min(o, c) - rng.uniform(0.05, 0.8)
                ticks.append(Tick(o, h, l, c))
                ts_opens.append(base + b * _M15)
                price = c
            produced_days += 1
        day_idx += 1
    return ticks, ts_opens


def aggregate(symbol: str, timeframe: str, group_size: int, ticks: list[Tick], ts_opens: list[int]) -> list[RawBar]:
    secs = {"H1": _H1, "H4": _H4, "D1": _D1}[timeframe]
    bars: list[RawBar] = []
    i = 0
    n = len(ticks)
    while i + group_size <= n:
        group = ticks[i:i + group_size]
        ts_open = ts_opens[i]
        bars.append(RawBar(symbol=symbol, timeframe=timeframe, ts_open=ts_open, ts_close=ts_open + secs,
                            open=group[0].o, high=max(t.h for t in group), low=min(t.l for t in group),
                            close=group[-1].c, volume=float(len(group) * 10), complete=True))
        i += group_size
    return bars


def m15_bars(symbol: str, ticks: list[Tick], ts_opens: list[int]) -> list[RawBar]:
    return [RawBar(symbol=symbol, timeframe="M15", ts_open=ts, ts_close=ts + _M15,
                    open=t.o, high=t.h, low=t.l, close=t.c, volume=10.0, complete=True)
            for t, ts in zip(ticks, ts_opens, strict=True)]


def build_scanner(symbols: list[str]) -> MarketScanner:
    scanner = MarketScanner(ScannerConfig(history_buffer_bars=100))
    metas = [SymbolMeta(symbol=s, tick_size=0.1, point_value=1.0, price_precision=2) for s in symbols]
    scanner.configure(metas, AdapterConfig(mode=Mode.REPLAY, source_id="benchmark"))
    req = Requirements(
        timeframes=frozenset({"M15", "H1", "H4", "D1"}),
        fields_by_timeframe={"M15": frozenset({"m_atr", "m_rsi", "pdh", "pdl", "h1_trend_up", "rmax20", "m_volrank"})},
        lookback_by_timeframe={"M15": 50, "H1": 30, "H4": 20, "D1": 10},
        symbols=frozenset(symbols),
    )
    scanner.register_requirements(req)
    return scanner


def run_replay(
    symbols: list[str],
    n_weekdays: int,
    seed: int,
    drop_gap_every_n_days: int | None,
    budget_s: float,
    progress_every: int = 2000,
    use_tracemalloc: bool = False,
) -> dict[str, Any]:
    """Full replay with live progress logging and a hard wall-clock abort budget.

    The budget is checked every M15 cycle (not just at progress checkpoints) so a run that stalls
    between checkpoints still aborts close to the budget instead of blocking indefinitely.
    """
    scanner = build_scanner(symbols)

    t_build0 = time.perf_counter()
    all_events: list[tuple[int, int, RawBar]] = []
    per_symbol_bar_count: dict[str, int] = {}
    for idx, symbol in enumerate(symbols):
        ticks, ts_opens = gen_weekday_m15(n_weekdays, seed=seed + idx)
        if drop_gap_every_n_days:
            keep_ticks, keep_ts = [], []
            bars_per_block = _BARS_PER_DAY * drop_gap_every_n_days
            for i, (t, ts) in enumerate(zip(ticks, ts_opens, strict=True)):
                if bars_per_block and (i % bars_per_block) in range(40, 45):
                    continue
                keep_ticks.append(t); keep_ts.append(ts)
            ticks, ts_opens = keep_ticks, keep_ts
        per_symbol_bar_count[symbol] = len(ticks)
        m15 = m15_bars(symbol, ticks, ts_opens)
        for b in m15:
            all_events.append((b.ts_close, 1, b))
        for tf, group in (("H1", 4), ("H4", 16), ("D1", 96)):
            for b in aggregate(symbol, tf, group, ticks, ts_opens):
                all_events.append((b.ts_close, 0, b))
    t_build1 = time.perf_counter()
    print(f"  [build] {len(all_events)} events assembled in {t_build1 - t_build0:.2f}s", flush=True)

    t_sort0 = time.perf_counter()
    all_events.sort(key=lambda e: (e[0], e[1]))
    t_sort1 = time.perf_counter()
    print(f"  [sort] done in {t_sort1 - t_sort0:.2f}s", flush=True)

    if use_tracemalloc:
        expected_contexts = sum(per_symbol_bar_count.values())
        if expected_contexts > _TRACEMALLOC_SAFE_CONTEXT_CEILING:
            print(f"  [WARNING] --tracemalloc requested with an expected {expected_contexts} contexts "
                  f"(> {_TRACEMALLOC_SAFE_CONTEXT_CEILING} safe ceiling). tracemalloc's per-allocation "
                  f"bookkeeping is known to become catastrophically slow at this scale (see module "
                  f"docstring) -- proceeding anyway, but expect this run to stall.", flush=True)
        gc.collect()
        tracemalloc.start()

    n_contexts = 0
    lookahead_violations = 0
    t0 = time.perf_counter()
    last_checkpoint_t = t0
    aborted = False
    last_symbol_ts: tuple[str, int] | None = None
    for ts_close, _prio, bar in all_events:
        scanner.ingest_bar(bar)
        if bar.timeframe == "M15":
            scanner.advance_clock(ts_close)
            ctx = scanner.build_context(bar.symbol, ts_close)
            n_contexts += 1
            last_symbol_ts = (bar.symbol, ts_close)

            as_of = ctx["meta"]["as_of"]
            for tf_ctx in ctx["timeframes"].values():
                for bd in tf_ctx["bars"]:
                    if bd["available_at"] > as_of:
                        lookahead_violations += 1

            now = time.perf_counter()
            if now - t0 > budget_s:
                print(f"  [ABORT] exceeded budget {budget_s}s at {n_contexts} contexts "
                      f"({now - t0:.1f}s elapsed) -- stopping this run early, it did NOT finish", flush=True)
                aborted = True
                break

            if n_contexts % progress_every == 0:
                batch_dt = now - last_checkpoint_t
                batch_rate = progress_every / batch_dt if batch_dt > 0 else float("inf")
                total_dt = now - t0
                overall_rate = n_contexts / total_dt if total_dt > 0 else float("inf")
                mem_note = ""
                if use_tracemalloc:
                    cur, peak = tracemalloc.get_traced_memory()
                    mem_note = f" traced_cur={cur / 1024 / 1024:.1f}MB traced_peak={peak / 1024 / 1024:.1f}MB"
                print(f"  [progress] contexts={n_contexts:>7} total_elapsed={total_dt:7.1f}s "
                      f"batch_rate={batch_rate:8.1f} ctx/s overall_rate={overall_rate:8.1f} ctx/s "
                      f"gc_counts={gc.get_count()}{mem_note}", flush=True)
                last_checkpoint_t = now
    elapsed = time.perf_counter() - t0
    if use_tracemalloc:
        tracemalloc.stop()

    return dict(
        total_bars=len(all_events), n_contexts=n_contexts, elapsed_s=elapsed,
        lookahead_violations=lookahead_violations, aborted=aborted, scanner=scanner,
        build_s=t_build1 - t_build0, sort_s=t_sort1 - t_sort0,
        per_symbol_bar_count=per_symbol_bar_count, last_symbol_ts=last_symbol_ts,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0] if __doc__ else "")
    parser.add_argument("--years", type=float, default=2.0, help="years of weekday data per symbol (default: 2)")
    parser.add_argument("--symbols", type=int, default=3, help="number of symbols (default: 3)")
    parser.add_argument("--budget", type=float, default=300.0, help="hard wall-clock abort budget in seconds (default: 300)")
    parser.add_argument("--progress-every", type=int, default=2000, help="contexts between progress log lines (default: 2000)")
    parser.add_argument("--tracemalloc", action="store_true", help="enable tracemalloc memory tracking (see module docstring for the pitfall at large scale)")
    parser.add_argument("--bisect", action="store_true", help="instead of one run, step weekday count upward (252/300/350/400/450/504 x years-scaled) to find where throughput degrades")
    args = parser.parse_args()

    symbols = [f"SYM{i}" for i in range(args.symbols)]

    if args.bisect:
        steps = [252, 300, 350, 400, 450, 504]
        max_wd = int(args.years * 252)
        steps = [s for s in steps if s <= max_wd] or [max_wd]
        for wd in steps:
            _run_one(symbols, wd, args.budget, args.progress_every, args.tracemalloc)
        print("=== BISECTION DONE ===", flush=True)
        return

    weekdays = int(args.years * 252)
    result = _run_one(symbols, weekdays, args.budget, args.progress_every, args.tracemalloc)

    if not result["aborted"] and result["last_symbol_ts"] is not None:
        print("\n--- schema validation proof ---")
        from ai_trader.market_scanner.schema_validation import validate_context
        scanner: MarketScanner = result["scanner"]
        # re-derive the final context to sanity-check validate_context() directly (build_context()
        # itself already validated every context in strict mode during the run -- if any had failed
        # it would have raised and this line would never be reached).
        last_symbol, last_ts = result["last_symbol_ts"]
        errs = validate_context(scanner.build_context(last_symbol, last_ts))
        print(f"all {result['n_contexts']} contexts validated during the run (strict mode raises on "
              f"first failure; none raised) + explicit re-check of the final context: "
              f"{'VALID' if not errs else errs}")


def _run_one(symbols: list[str], weekdays: int, budget_s: float, progress_every: int, use_tracemalloc: bool) -> dict[str, Any]:
    print(f"=== SCALE: {weekdays} weekdays x {len(symbols)} symbols "
          f"(~{weekdays * _BARS_PER_DAY * len(symbols)} M15 bars) ===", flush=True)
    gc.collect()
    t0 = time.perf_counter()
    result = run_replay(symbols, weekdays, seed=100, drop_gap_every_n_days=17,
                         budget_s=budget_s, progress_every=progress_every, use_tracemalloc=use_tracemalloc)
    wall = time.perf_counter() - t0
    status = "ABORTED (budget exceeded)" if result["aborted"] else "COMPLETED"
    rate = result["n_contexts"] / result["elapsed_s"] if result["elapsed_s"] > 0 else 0.0
    print(f"--- {weekdays}wd RESULT: {status}  contexts={result['n_contexts']} "
          f"replay_elapsed={result['elapsed_s']:.1f}s rate={rate:.1f}ctx/s "
          f"build={result['build_s']:.2f}s sort={result['sort_s']:.2f}s "
          f"lookahead_violations={result['lookahead_violations']}  (wall={wall:.1f}s) ---\n", flush=True)
    return result


if __name__ == "__main__":
    main()
