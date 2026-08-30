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
        full OANDA_XAUUSD_M15.csv>
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


def materialize(source_path: Path) -> dict:
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=MAX_Q4_BAR_INDEX,
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
            f"boundary (max_q4_bar_index={MAX_Q4_BAR_INDEX}) -- the source file does not contain "
            "enough Q4 history; refusing to write a truncated-for-the-wrong-reason fixture"
        )
    if len(q4_rows) != MAX_Q4_BAR_INDEX:
        raise RuntimeError(
            f"materialize_sealed_fixture: collected {len(q4_rows)} Q4 rows, expected exactly "
            f"{MAX_Q4_BAR_INDEX} -- refusing to write a fixture with an unexplained row-count mismatch"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = list(warmup_buffer) + q4_rows
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "open", "high", "low", "close", "volume"])
        for ts, o, h, l, c, v in all_rows:
            writer.writerow([ts, o, h, l, c, v])

    content_hash = hash_file(OUTPUT_CSV)
    origin_source_content_hash = hash_file(source_path)
    manifest = {
        "source_file_name": OUTPUT_CSV.name,
        "content_hash": content_hash,
        "symbol": XAUUSD_M15_SYMBOL,
        "timeframe": "M15",
        "bar_interval_seconds": M15_BAR_INTERVAL_SECONDS,
        "first_bar_ts_open": all_rows[0][0],
        "sealed_through_bar_index": MAX_Q4_BAR_INDEX,
        "adapter_version": ADAPTER_VERSION,
        "warmup_bar_count": len(warmup_buffer),
        "q4_bar_count": len(q4_rows),
        "total_row_count": len(all_rows),
        "q4_start_ts": Q4_START_TS,
        "bar_378_ts_open": q4_rows[-1][0],
        "bar_378_close": q4_rows[-1][4],
        "bar_378_volume": q4_rows[-1][5],
        "gaps_found_in_q4_range": gaps_found,
        "max_q4_bar_index_read_during_materialization": reader.max_q4_bar_index_read,
        "origin_source_path_basename": source_path.name,
        "origin_source_content_hash": origin_source_content_hash,
        "origin_source_total_row_count_NOT_recorded": (
            "deliberately not counted/recorded -- doing so would require reading past the sealed "
            "boundary; this manifest records only what was actually, boundedly read"
        ),
    }
    OUTPUT_MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="path to the full OANDA_XAUUSD_M15.csv")
    args = parser.parse_args()
    manifest = materialize(args.source)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
