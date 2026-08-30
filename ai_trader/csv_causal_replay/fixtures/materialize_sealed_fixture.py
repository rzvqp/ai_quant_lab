"""One-time (re-runnable, deterministic) builder for the sealed Q4 1-378 dev/test fixture (mandate
section 4). Run as a script, not imported by `engine`/`tests` at runtime -- the *output* of this
script (`fixtures/data/Q4_SEALED_1_378.csv` + its manifest) is what the rest of this package reads;
this script itself is the only piece of code in this whole mandate that ever opens the full,
unsealed, multi-year source file.

**How this stays bounded even though the source file spans 2011-2026**: it reads that file through
`sealed_reader.SealedReader` configured with `max_q4_bar_index=378` -- the exact same reader class
`tests/test_sealed_reader.py` uses to prove the dev/test fixture itself is sealed. Reading raises
`SealedBoundaryError` and stops the instant Q4 bar 379 would be reached, so this script's own
`max_q4_bar_index_read` (asserted at the end, not merely assumed) is the mechanical proof for
mandate section 17's `MAX_Q4_BAR_READ_DURING_DEVELOPMENT = 378`, covering fixture CREATION, not
only fixture USE.

Usage:
    python -m ai_trader.csv_causal_replay.fixtures.materialize_sealed_fixture --source <path to the
        full OANDA_XAUUSD_M15.csv> [--max-bar N]

**Autonomous-Q4 reachability (Red Team E104, RT-CSV-INCREMENTAL-UNLOCK-BAR379-REVIEW-001, FAIL,
remediated)**: `materialize()`/`--max-bar` below accept an arbitrary boundary and are for
CEO-authorized manual/research use ONLY -- nothing here reads durable state or refuses
`N > current_sealed + 1`. An autonomous Q4-continuation runtime MUST NOT call this module's
`materialize()` or CLI directly (doing so is exactly the "bulk future exposure" finding E104
identified: one `--max-bar 5900`-style call would materialize bars 380..5900 in one step, which the
engine's own per-bar commit handshake does not prevent, since materialization is a separate code
path from `engine.step()`/`commit_decision()`). The autonomous-safe entrypoint is
`fixtures.autonomous_extend.extend_next_bar()`, which derives its target boundary from durable state
internally, refuses everything but exactly `current_sealed + 1`, and calls `materialize()` here only
after that gate passes -- see that module's own docstring for the full remediation.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import deque
from pathlib import Path

from ai_trader.csv_causal_replay.errors import SealedBoundaryError
from ai_trader.csv_causal_replay.identity import (
    ADAPTER_VERSION, M15_BAR_INTERVAL_SECONDS, MAX_Q4_BAR_INDEX, Q4_START_TS, XAUUSD_M15_SYMBOL, hash_file,
)
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import gap_classification_str

WARMUP_BARS_BEFORE_Q4 = 2000
"""~3 weeks of M15 bars (calendar time, accounting for daily-rollover/weekend gaps) before Q4 start
-- disclosed, reasoned choice, not a re-derivation of any documented requirement: EMA(50)'s weight on
a single bar decays below 1% after ~5x its period (~250 bars), so 2000 bars is roughly an 8x safety
margin past full convergence for the causal EMA-50 helper (`ema.py`) this fixture backs. NOT claimed
to reproduce the original live Pine indicator's own EMA-50 internal state bit-for-bit (that indicator
warms up from TradingView's full available chart history, materially more than 2000 bars, and is not
independently reproducible from this repo alone) -- see `docs/.../CSV_Q4_PARITY_1_378_V1.md` section
on indicator causality for the explicit scope of what this fixture's EMA-50 helper is, and is not,
claimed to match."""

OUTPUT_DIR = Path(__file__).parent / "data"
OUTPUT_CSV = OUTPUT_DIR / "Q4_SEALED_1_378.csv"
OUTPUT_MANIFEST = OUTPUT_DIR / "Q4_SEALED_1_378_MANIFEST.json"


def materialize(
    source_path: Path, *, max_q4_bar_index: int = MAX_Q4_BAR_INDEX, output_dir: Path = OUTPUT_DIR,
) -> dict:
    """`max_q4_bar_index` defaults to the originally-sealed 378 boundary (identical behavior/output
    path to before this parameter existed). Passing a larger value materializes a NEW, separately
    named fixture (`Q4_SEALED_1_{max_q4_bar_index}.csv`) extending the sealed boundary by exactly
    that many bars -- it never overwrites an already-materialized lower-boundary fixture, so every
    prior boundary's file + manifest remains on disk as an audit trail of exactly how far the sealed
    boundary has ever been extended, one CEO-authorized step at a time (mandate: "does NOT authorize
    bulk future exposure" -- each call here is still bounded by the same SealedReader/SealedBoundaryError
    mechanism the original 378 fixture and the Red Team's review of it were built and audited against;
    only the boundary value itself is now a parameter instead of a hardcoded constant).

    `output_dir` defaults to the real `fixtures/data/` directory (production behavior, unchanged) --
    overridable only so `tests/test_autonomous_extend.py` can point synthetic-scenario calls at a
    `tmp_path` instead of writing test fixtures into the real directory alongside the genuine Q4
    ones. The CLI (`main()` below) never overrides it."""
    output_csv = output_dir / f"Q4_SEALED_1_{max_q4_bar_index}.csv"
    output_manifest = output_dir / f"Q4_SEALED_1_{max_q4_bar_index}_MANIFEST.json"
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=max_q4_bar_index,
    )
    warmup_buffer: deque[tuple[int, float, float, float, float, float]] = deque(maxlen=WARMUP_BARS_BEFORE_Q4)
    q4_rows: list[tuple[int, float, float, float, float, float]] = []
    gaps_found: list[dict] = []
    reached_boundary = False

    with SealedReader(source_path, config=config) as reader:
        try:
            for row in reader.iter_rows():
                b = row.bar
                record = (b.ts_open, b.open, b.high, b.low, b.close, b.volume)
                if row.q4_bar_index is None:
                    warmup_buffer.append(record)
                else:
                    q4_rows.append(record)
                    if row.gap_before is not None:
                        gaps_found.append({
                            "q4_bar_index": row.q4_bar_index, "gap_start": row.gap_before.gap_start,
                            "gap_end": row.gap_before.gap_end,
                            "duration_seconds": row.gap_before.duration_seconds,
                            "classification": gap_classification_str(row.gap_before),
                        })
        except SealedBoundaryError:
            reached_boundary = True

    if not reached_boundary:
        raise RuntimeError(
            "materialize_sealed_fixture: source file exhausted WITHOUT ever reaching the sealed "
            f"boundary (max_q4_bar_index={max_q4_bar_index}) -- the source file does not contain "
            "enough Q4 history; refusing to write a truncated-for-the-wrong-reason fixture"
        )
    if len(q4_rows) != max_q4_bar_index:
        raise RuntimeError(
            f"materialize_sealed_fixture: collected {len(q4_rows)} Q4 rows, expected exactly "
            f"{max_q4_bar_index} -- refusing to write a fixture with an unexplained row-count mismatch"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    all_rows = list(warmup_buffer) + q4_rows
    with output_csv.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for ts, o, h, l, c, v in all_rows:
            writer.writerow([ts, o, h, l, c, v])

    content_hash = hash_file(output_csv)
    origin_source_content_hash = hash_file(source_path)
    manifest = {
        "source_file_name": output_csv.name,
        "content_hash": content_hash,
        "symbol": XAUUSD_M15_SYMBOL,
        "timeframe": "M15",
        "bar_interval_seconds": M15_BAR_INTERVAL_SECONDS,
        "first_bar_ts_open": all_rows[0][0],
        "sealed_through_bar_index": max_q4_bar_index,
        "adapter_version": ADAPTER_VERSION,
        "warmup_bar_count": len(warmup_buffer),
        "q4_bar_count": len(q4_rows),
        "total_row_count": len(all_rows),
        "q4_start_ts": Q4_START_TS,
        "last_bar_ts_open": q4_rows[-1][0],
        "last_bar_close": q4_rows[-1][4],
        "last_bar_volume": q4_rows[-1][5],
        "gaps_found_in_q4_range": gaps_found,
        "max_q4_bar_index_read_during_materialization": reader.max_q4_bar_index_read,
        "origin_source_path_basename": source_path.name,
        "origin_source_content_hash": origin_source_content_hash,
        "origin_source_total_row_count_NOT_recorded": (
            "deliberately not counted/recorded -- doing so would require reading past the sealed "
            "boundary; this manifest records only what was actually, boundedly read"
        ),
    }
    output_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="path to the full OANDA_XAUUSD_M15.csv")
    parser.add_argument(
        "--max-bar", type=int, default=MAX_Q4_BAR_INDEX,
        help=(
            "sealed boundary (last Q4 bar index to include). Defaults to the originally-sealed 378. "
            "Pass a larger value to extend the boundary by exactly that many bars into a new, "
            "separately-named fixture -- never overwrites a lower-boundary fixture already on disk."
        ),
    )
    args = parser.parse_args()
    manifest = materialize(args.source, max_q4_bar_index=args.max_bar)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
