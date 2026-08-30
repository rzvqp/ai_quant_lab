"""CSV_CAUSAL_REPLAY_ADAPTER_V1 performance benchmark (mandate section 13). Run only AFTER Parity
Tests A/B both pass (mandate: "Do not optimize before parity passes" -- this script does not
optimize anything; it measures the already-parity-passed implementation as delivered).

Unlike `tradingview-mcp/causal_replay_benchmark.mjs` (whose wall-time was dominated by a real,
unavoidable 250ms CDP polling delay inside `step()`, an artifact of what that benchmark COULD
measure under mandate section 13's own "no live connection" constraint), this engine has no
external round-trip of any kind once its sealed fixture is loaded -- every `step()`/`commit_decision()`
call is an in-process dict lookup plus a small JSON file write. The wall-clock number here is
therefore a REAL measurement of this implementation's own throughput, not a mocked-latency artifact
-- disclosed explicitly, not overclaimed as "how fast a live AI Trader session will feel" (that
still depends on the REASONING layer's own per-bar time, which this benchmark does not and cannot
measure).
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from ai_trader.csv_causal_replay.engine import CSVCausalReplayEngine
from ai_trader.csv_causal_replay.persistence import DurablePointerStore

SEALED_FIXTURE_PATH = Path(__file__).parent / "data" / "Q4_SEALED_1_378.csv"
BENCH_BAR_COUNT = 150  # bars 1..150 -- well clear of the real bar-378 boundary, never touches it


def _fresh_engine(tmp_dir: Path) -> CSVCausalReplayEngine:
    store = DurablePointerStore(tmp_dir / "state.json")
    engine = CSVCausalReplayEngine(sealed_csv_path=SEALED_FIXTURE_PATH, store=store)
    # Seed at bar 1 (the earliest valid seed point) -- BENCH_BAR_COUNT then covers bars 2..151,
    # comfortably clear of the real bar-378 boundary this benchmark must never approach.
    engine.seed_from_known_state(session_id="bench", last_committed_bar_index=1, open_event_state_reference=None)
    return engine


def bench_atomic(tmp_dir: Path) -> dict:
    engine = _fresh_engine(tmp_dir)
    calls = 0
    t0 = time.perf_counter()
    for _ in range(BENCH_BAR_COUNT):
        state = engine.status()
        revealed = engine.step(expected_pointer_before=state.last_committed_timestamp)
        calls += 1
        engine.commit_decision(bar_id=revealed.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
        calls += 1
    elapsed = time.perf_counter() - t0
    return {"bars": BENCH_BAR_COUNT, "calls": calls, "calls_per_bar": calls / BENCH_BAR_COUNT, "elapsed_s": elapsed}


def bench_hybrid(tmp_dir: Path) -> dict:
    engine = _fresh_engine(tmp_dir)
    # HYBRID needs open_event_state_reference cleared -- already None from seeding above.
    calls = 0
    bars_done = 0
    t0 = time.perf_counter()
    while bars_done < BENCH_BAR_COUNT:
        state = engine.status()
        result = engine.run_until_gate(
            expected_pointer_before=state.last_committed_timestamp,
            max_bars=min(8, BENCH_BAR_COUNT - bars_done),
        )
        calls += 1
        final_bar = result.bars_processed[-1]
        engine.commit_decision(bar_id=final_bar.bar.ts_open, decision_type="ROUTINE_NO_EVENT", decision_record={})
        calls += 1
        bars_done += len(result.bars_processed)
    elapsed = time.perf_counter() - t0
    return {"bars": bars_done, "calls": calls, "calls_per_bar": calls / bars_done, "elapsed_s": elapsed}


def main() -> None:
    with TemporaryDirectory() as tmp:
        atomic = bench_atomic(Path(tmp))
    with TemporaryDirectory() as tmp:
        hybrid = bench_hybrid(Path(tmp))

    for label, result in (("ATOMIC_MODE", atomic), ("HYBRID_MODE", hybrid)):
        result["bars_per_second_engine_only"] = round(result["bars"] / result["elapsed_s"], 1)

    report = {
        "ATOMIC_MODE": atomic,
        "HYBRID_MODE": hybrid,
        "ESTIMATED_AI_INTERRUPTS_PER_100_ROUTINE_BARS": {
            "ATOMIC": 100,  # one reveal+commit reasoning interrupt per bar, by construction
            "HYBRID": math.ceil(100 / 8) * 2,  # ceil(100/8)=13 run_until_gate calls + 13 commits, all routine
        },
        "note": (
            "Wall-clock here is a REAL measurement (no CDP/UI round-trip exists in this engine at "
            "all) -- NOT comparable to causal_replay_benchmark.mjs's mocked, 250ms-poll-dominated "
            "numbers. It measures this implementation's own in-process throughput only, not "
            "reasoning-layer time per bar, which this benchmark cannot and does not estimate."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
