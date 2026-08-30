"""Mandate section 14: "future-row inaccessibility", "bar 379 sealed boundary". These tests operate
at the lowest level (`SealedReader` itself), independent of `engine.py`, so a boundary bug in the
reader can never be masked by a coincidentally-correct engine-level check.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.errors import SealedBoundaryError
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig

Q4_START_TS = 1_601_510_400
BAR_378_TS = 1_602_036_900

# The full, unsealed, multi-year source (2011-2026) this mandate's fixture was materialized from.
# Present on this development machine but not assumed portable -- tests below that need it skip
# cleanly (not xfail/error) when it is absent, per this repo's own convention for machine-local data.
_LONG_SOURCE_CANDIDATES = [
    Path("/c/Users/MEDION GAMING/ai_quant_lab-alpha-automation/data/market/OANDA_XAUUSD_M15.csv"),
    Path("C:/Users/MEDION GAMING/ai_quant_lab-alpha-automation/data/market/OANDA_XAUUSD_M15.csv"),
]


def _find_long_source() -> Path | None:
    for candidate in _LONG_SOURCE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def test_sealed_fixture_contains_exactly_378_q4_bars_and_2000_warmup(sealed_fixture_path):
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=378,
    )
    warmup_count = 0
    q4_indices = []
    with SealedReader(sealed_fixture_path, config=config) as reader:
        for row in reader.iter_rows():
            if row.q4_bar_index is None:
                warmup_count += 1
            else:
                q4_indices.append(row.q4_bar_index)
    assert warmup_count == 2000
    assert q4_indices == list(range(1, 379))


def test_bar_378_matches_the_authoritative_log_exactly(sealed_fixture_path):
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=378,
    )
    with SealedReader(sealed_fixture_path, config=config) as reader:
        rows = list(reader.iter_rows())
    bar_378 = next(r for r in rows if r.q4_bar_index == 378)
    # AI_TRADER_Q4_M15_LOG.md: "BAR 378 (02:29:59): close 1880.434, vol 523."
    assert bar_378.bar.ts_open == BAR_378_TS
    assert bar_378.bar.close == 1880.434
    assert bar_378.bar.volume == 523.0


def test_reader_refuses_to_yield_a_378th_plus_1_q4_bar_against_the_sealed_fixture(sealed_fixture_path):
    """The sealed fixture physically contains no row past Q4 bar 378 -- so asking for up to 378 is
    the fixture's own natural end. This test instead proves the MECHANISM by asking for fewer than
    the fixture contains and confirming iteration stops exactly there, never silently continuing."""
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=10,
    )
    with pytest.raises(SealedBoundaryError):
        with SealedReader(sealed_fixture_path, config=config) as reader:
            list(reader.iter_rows())


def test_boundary_error_fires_before_the_11th_bars_ohlcv_would_be_parsed(sealed_fixture_path):
    """Directly exercises what `errors.SealedBoundaryError`'s docstring claims: the rows actually
    yielded stop at bar 10, and the exception itself carries no OHLCV data for bar 11."""
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=10,
    )
    yielded = []
    with pytest.raises(SealedBoundaryError) as excinfo:
        with SealedReader(sealed_fixture_path, config=config) as reader:
            for row in reader.iter_rows():
                yielded.append(row)
    q4_rows = [r for r in yielded if r.q4_bar_index is not None]
    assert len(q4_rows) == 10  # the 2000 warm-up rows (q4_bar_index=None) are yielded too, before Q4 starts
    assert max(r.q4_bar_index for r in q4_rows) == 10
    # The error message names the line/index it refused, never an OHLCV value from that row.
    assert "1602037800" not in str(excinfo.value)  # bar 11's ts_open -- must never appear


@pytest.mark.skipif(_find_long_source() is None, reason="full multi-year source CSV not present on this machine")
def test_against_the_real_unsealed_source_reading_stops_exactly_at_bar_378():
    """The strongest available version of this test: runs the SAME bounded reader against the REAL
    355,696-row, 2011-2026 source file (not the already-safe sealed fixture) and proves it never
    reads bar 379 (2020-10-07T02:30:00 UTC open) even though that row is physically present later in
    the file."""
    source = _find_long_source()
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=378,
    )
    with pytest.raises(SealedBoundaryError):
        with SealedReader(source, config=config) as reader:
            for _ in reader.iter_rows():
                pass
            assert reader.max_q4_bar_index_read <= 378
