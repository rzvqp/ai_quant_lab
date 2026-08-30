"""Mandate section 14's explicit requirement: "A test named 'no lookahead' must actually attempt to
access future information" -- not merely assert a property by construction. Also houses Parity Test
A (mandate section 10, source parity) and Parity Test B (mandate section 11, ledger/state parity)
as executable tests against the REAL materialized sealed fixture, not synthetic data -- the results
these tests establish are what `CSV_Q4_PARITY_1_378_V1.md` reports.
"""

from __future__ import annotations

import csv

import pytest

from ai_trader.csv_causal_replay.errors import SealedBoundaryError
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.tests.conftest import SEALED_FIXTURE_PATH

Q4_START_TS = 1_601_510_400
BAR_378_TS = 1_602_036_900
BAR_379_TS = 1_602_037_800


# ── the mandate's own explicitly-required "no lookahead" ACTIVE ATTEMPT ────────────────────────

def test_no_lookahead_actively_attempts_to_read_bar_379_via_the_reader_and_is_refused(seeded_engine):
    """Not a passive assertion about the sealed fixture's row count -- this ACTS: seeds the engine
    at the real bar-378 boundary (exactly where a real resumed session would be) and actually calls
    step(), the real production entry point a reasoning layer would use, attempting to obtain bar
    379. The refusal is the only acceptable outcome."""
    with pytest.raises(SealedBoundaryError):
        seeded_engine.step(expected_pointer_before=BAR_378_TS)


def test_no_lookahead_actively_attempts_a_direct_reader_read_one_bar_past_an_authorized_ceiling(sealed_fixture_path):
    """A second, independent attempt at the lower `SealedReader` level (bypassing `engine.py`
    entirely) -- proves the refusal is not merely an engine-level policy check but a property of the
    reader every caller (including any future, differently-written caller) would hit. Uses a ceiling
    of 377 (one less than the sealed fixture's own 378-bar content) so the reader is FORCED to
    actually attempt reading bar 378 and be refused -- not merely reach the fixture's own natural
    end-of-file with nothing left to refuse (that would prove nothing about the refusal MECHANISM;
    see `test_against_the_real_unsealed_source_reading_stops_exactly_at_bar_378` in
    test_sealed_reader.py for the equivalent proof at the REAL boundary, 378 vs 379, against the
    actual unsealed multi-year source)."""
    config = SealedReaderConfig(
        symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=377,
    )
    attempted_to_reach_378 = False
    with pytest.raises(SealedBoundaryError):
        with SealedReader(sealed_fixture_path, config=config) as reader:
            for row in reader.iter_rows():
                if row.q4_bar_index == 377:
                    attempted_to_reach_378 = True  # the NEXT iteration is the actual lookahead attempt
    assert attempted_to_reach_378, "test did not actually reach the boundary before the expected refusal"


def test_no_lookahead_the_sealed_fixture_itself_contains_zero_bytes_of_bar_379(sealed_fixture_path):
    """The strongest possible negative: bar 379's own timestamp string does not appear ANYWHERE in
    the sealed fixture file at all -- there is no row to leak even if every check above had a bug."""
    content = sealed_fixture_path.read_text(encoding="utf-8")
    assert str(BAR_379_TS) not in content


# ── Parity Test A (mandate section 10): source parity, bars 1-378 ──────────────────────────────

class TestParityA_SourceParity:
    @staticmethod
    def _load_q4_rows():
        config = SealedReaderConfig(
            symbol="OANDA:XAUUSD", bar_interval_seconds=900, q4_start_ts=Q4_START_TS, max_q4_bar_index=378,
        )
        with SealedReader(SEALED_FIXTURE_PATH, config=config) as reader:
            return [row for row in reader.iter_rows() if row.q4_bar_index is not None]

    def test_bar_sequence_parity(self):
        rows = self._load_q4_rows()
        assert [r.q4_bar_index for r in rows] == list(range(1, 379))

    def test_timestamp_parity_bar_1_and_bar_378(self):
        rows = self._load_q4_rows()
        assert rows[0].bar.ts_open == Q4_START_TS  # 2020-10-01T00:00:00 UTC, AI_TRADER_Q3_Q4_OPERATING_STANDARD_V1.md section 20
        assert rows[-1].bar.ts_open == BAR_378_TS  # 2020-10-07T02:15:00 UTC open / 02:29:59 close-label

    def test_ohlc_parity_against_the_authoritative_log_bars_375_to_378(self):
        """AI_TRADER_Q4_M15_LOG.md COMPACT BLOCK 370-377 CLOSES list + the standalone BAR 378 line."""
        rows = {r.q4_bar_index: r.bar for r in self._load_q4_rows()}
        expected_closes = {375: 1875.888, 376: 1879.648, 377: 1879.44, 378: 1880.434}
        for idx, expected_close in expected_closes.items():
            assert rows[idx].close == expected_close, f"bar {idx} close mismatch"
        assert rows[378].volume == 523.0

    def test_gap_positions_match_all_four_documented_q4_gaps_exactly(self):
        """REPLAY_DATA_GAP_LEDGER.md GAP-151..154 -- cross-checked by Q4 bar index, not merely by
        count, against an independently-authored document this test suite did not generate."""
        rows = self._load_q4_rows()
        gap_indices = {r.q4_bar_index: r.gap_before.classification.value for r in rows if r.gap_before is not None}
        assert gap_indices == {
            85: "MAINTENANCE",   # GAP-151
            177: "WEEKEND",      # GAP-152
            269: "MAINTENANCE",  # GAP-153
            361: "MAINTENANCE",  # GAP-154
        }

    def test_volume_semantics_disclosed_not_forced(self):
        """Mandate section 10: "If volume semantics differ between sources, report explicitly rather
        than forcing equality." This fixture's volume column is the same OANDA tick-count proxy the
        rest of this repo's `data/market/*.csv` files already use (confirmed: bar 378 volume=523
        matches AI_TRADER_Q4_M15_LOG.md's own "vol 523" verbatim) -- no unit conversion was applied
        or needed, so there is nothing to disclose beyond this direct match."""
        rows = {r.q4_bar_index: r.bar for r in self._load_q4_rows()}
        assert rows[378].volume == 523.0


# ── Parity Test B (mandate section 11): ledger/state parity ────────────────────────────────────

class TestParityB_LedgerStateParity:
    def test_q4_p007_003_reproduced_as_open_at_bar_378(self, seeded_engine):
        assert seeded_engine.status().open_event_state_reference == "Q4-P007-003:OPEN"

    def test_trade_count_zero_through_bar_378(self):
        """AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md contains a header and methodology note only -- zero
        trade rows -- confirmed by direct read, not assumed from the mandate text alone."""
        import re
        from pathlib import Path
        log = Path(__file__).parents[3] / "docs" / "trader_apprenticeship" / "AI_TRADER_Q4_TRADE_EVIDENCE_LOG.md"
        text = log.read_text(encoding="utf-8")
        # A real trade row would need a QUARTER_TRADE_ID like "Q4-001" -- none present.
        assert not re.search(r"Q4-\d{3}", text)

    def test_mgmt004_trigger_count_zero_through_bar_378(self):
        import re
        from pathlib import Path
        log = Path(__file__).parents[3] / "docs" / "trader_apprenticeship" / "AI_TRADER_Q4_MGMT004_PROSPECTIVE_LEDGER.md"
        text = log.read_text(encoding="utf-8")
        assert not re.search(r"Q4-\d{3}", text)

    def test_bar_378_state_matches_the_log(self, seeded_engine):
        state = seeded_engine.status()
        assert state.last_committed_bar == BAR_378_TS
        assert state.next_bar == 379
