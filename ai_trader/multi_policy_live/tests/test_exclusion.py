"""`LevelDayExclusion` tests -- writes CAND-0001-shaped `ENTRY_SUBMITTED` entries into a REAL
`SqliteStateStore` (same `log_name="pdh_pdl_demo.audit"` CAND-0001's own `PdhPdlAuditJournal` uses) via
the SAME journal class, then verifies the registry reads them back correctly. Never touches a running
process -- this is exactly the cross-process read path, exercised here against a throwaway file."""

from __future__ import annotations

from pathlib import Path

from ai_trader.multi_policy_live.exclusion import LevelDayExclusion
from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditEntry, PdhPdlAuditKind
from ai_trader.persistent_state.store import SqliteStateStore

DAY1_START = 1_705_356_000


def _write_cand0001_entry(db_path: Path, as_of: int, direction: int, kind: PdhPdlAuditKind = PdhPdlAuditKind.ENTRY_SUBMITTED) -> None:
    store = SqliteStateStore(db_path)
    try:
        journal = PdhPdlAuditJournal(store, log_name="pdh_pdl_demo.audit")
        journal.record(PdhPdlAuditEntry(
            symbol="XAUUSD", as_of=as_of, kind=kind,
            detail={"touch_idx": 17, "direction": direction, "client_order_id": "CID-1"},
        ))
    finally:
        store.close()


def test_detects_a_matching_pdh_entry_same_day(tmp_path: Path) -> None:
    db_path = tmp_path / "pdh_pdl_state.db"
    _write_cand0001_entry(db_path, as_of=DAY1_START + 3600, direction=-1)  # CAND-0001: direction<0 -> PDH

    exclusion = LevelDayExclusion(db_path)
    day_label = day_boundary_start_utc(DAY1_START + 3600)
    assert exclusion.cand0001_already_entered_today(LevelKind.PDH, day_label) is True


def test_no_match_for_the_opposite_level(tmp_path: Path) -> None:
    db_path = tmp_path / "pdh_pdl_state.db"
    _write_cand0001_entry(db_path, as_of=DAY1_START + 3600, direction=-1)  # PDH

    exclusion = LevelDayExclusion(db_path)
    day_label = day_boundary_start_utc(DAY1_START + 3600)
    assert exclusion.cand0001_already_entered_today(LevelKind.PDL, day_label) is False


def test_no_match_for_a_different_day(tmp_path: Path) -> None:
    db_path = tmp_path / "pdh_pdl_state.db"
    _write_cand0001_entry(db_path, as_of=DAY1_START + 3600, direction=-1)

    exclusion = LevelDayExclusion(db_path)
    other_day = day_boundary_start_utc(DAY1_START + 86_400 + 3600)
    assert exclusion.cand0001_already_entered_today(LevelKind.PDH, other_day) is False


def test_non_entry_submitted_kinds_are_ignored(tmp_path: Path) -> None:
    db_path = tmp_path / "pdh_pdl_state.db"
    _write_cand0001_entry(db_path, as_of=DAY1_START + 3600, direction=-1, kind=PdhPdlAuditKind.NO_TRADE)

    exclusion = LevelDayExclusion(db_path)
    day_label = day_boundary_start_utc(DAY1_START + 3600)
    assert exclusion.cand0001_already_entered_today(LevelKind.PDH, day_label) is False


def test_no_entries_at_all_returns_false(tmp_path: Path) -> None:
    db_path = tmp_path / "pdh_pdl_state.db"
    store = SqliteStateStore(db_path)  # creates the file with no entries
    store.close()

    exclusion = LevelDayExclusion(db_path)
    assert exclusion.cand0001_already_entered_today(LevelKind.PDH, DAY1_START) is False
