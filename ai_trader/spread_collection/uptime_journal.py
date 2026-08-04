"""`UptimeReportLog` -- append-only persistence for `SessionUptimeReport`, same convention as
`SpreadObservationLog`. This is the durable artifact the Statistician's own requirement asks for:
without a PERSISTED record, distinguishing "rare event" from "collector wasn't running" requires
re-running the ground-truth query every time -- a log makes it a fact of record instead."""

from __future__ import annotations

import json

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.uptime import SessionUptimeReport

_DEFAULT_LOG_NAME = "spread_collection.uptime_reports"


def _serialize(report: SessionUptimeReport) -> str:
    return json.dumps({
        "session": report.session, "window_start": report.window_start, "window_end": report.window_end,
        "bars_passed": report.bars_passed, "bars_recorded": report.bars_recorded, "ratio": report.ratio,
        "computed_as_of": report.computed_as_of,
    })


def _deserialize(payload: str) -> SessionUptimeReport:
    data = json.loads(payload)
    return SessionUptimeReport(
        session=data["session"], window_start=data["window_start"], window_end=data["window_end"],
        bars_passed=data["bars_passed"], bars_recorded=data["bars_recorded"], ratio=data["ratio"],
        computed_as_of=data["computed_as_of"],
    )


class UptimeReportLog:
    def __init__(
        self, state_store: SqliteStateStore | None = None, log_name: str = _DEFAULT_LOG_NAME,
    ) -> None:
        self._state_store = state_store
        self._log_name = log_name
        if state_store is None:
            self._entries: list[SessionUptimeReport] = []
        else:
            self._entries = [
                _deserialize(payload) for payload in state_store.read_log_entries(log_name)
            ]

    def record(self, report: SessionUptimeReport) -> None:
        self._entries.append(report)
        if self._state_store is not None:
            self._state_store.append_log_entry(self._log_name, _serialize(report))

    def record_all(self, reports: tuple[SessionUptimeReport, ...]) -> None:
        for report in reports:
            self.record(report)

    @property
    def entries(self) -> tuple[SessionUptimeReport, ...]:
        return tuple(self._entries)
