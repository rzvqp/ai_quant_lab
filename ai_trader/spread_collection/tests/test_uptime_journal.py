"""`UptimeReportLog` tests -- persistence round-trip, same convention as `test_journal.py`."""

from __future__ import annotations

from pathlib import Path

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.uptime import SessionUptimeReport
from ai_trader.spread_collection.uptime_journal import UptimeReportLog


def _report(session: str = "asia", ratio: float | None = 0.5) -> SessionUptimeReport:
    return SessionUptimeReport(
        session=session, window_start=0, window_end=900, bars_passed=2, bars_recorded=1,
        ratio=ratio, computed_as_of=1000,
    )


def test_record_and_read_back_in_memory() -> None:
    log = UptimeReportLog()
    report = _report()
    log.record(report)
    assert log.entries == (report,)


def test_persists_across_a_new_store_connection(tmp_path: Path) -> None:
    db_path = tmp_path / "uptime.db"
    store1 = SqliteStateStore(db_path)
    UptimeReportLog(store1).record(_report(session="london"))
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        log2 = UptimeReportLog(store2)
        assert len(log2.entries) == 1
        assert log2.entries[0].session == "london"
    finally:
        store2.close()


def test_none_ratio_round_trips(tmp_path: Path) -> None:
    db_path = tmp_path / "uptime.db"
    store1 = SqliteStateStore(db_path)
    UptimeReportLog(store1).record(_report(ratio=None))
    store1.close()

    store2 = SqliteStateStore(db_path)
    try:
        log2 = UptimeReportLog(store2)
        assert log2.entries[0].ratio is None
    finally:
        store2.close()


def test_record_all_persists_every_report_in_order(tmp_path: Path) -> None:
    db_path = tmp_path / "uptime.db"
    store = SqliteStateStore(db_path)
    try:
        log = UptimeReportLog(store)
        reports = (_report(session="asia"), _report(session="london"), _report(session="ny"))
        log.record_all(reports)
        assert [r.session for r in log.entries] == ["asia", "london", "ny"]
    finally:
        store.close()
