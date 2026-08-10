"""`build_loop` wiring test -- with a fake gateway, never a real terminal. Confirms the composition
(`LiveBarFeed` + `SpreadCollectingNullRecognitionRule` + `CandidateSignalProducer` + `LiveSignalLoop`)
actually records a `SpreadObservation` when a bar with a live tick is polled."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.spread_collection.entrypoint import build_loop
from ai_trader.spread_collection.journal import SpreadObservationLog

SYMBOL = "XAUUSD"
AS_OF = 1_705_356_000


class _FakeGateway:
    """Stubs the FULL `MT5Gateway` Protocol surface, matching the established convention
    (`mt5_pnl_source/tests/_fixtures.py::FakeMT5HistoryGateway`)."""

    def __init__(self) -> None:
        self._rate = {
            "time": AS_OF, "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "tick_volume": 10,
        }
        # Backs `make_broker_offset`'s own M1 probe (`copy_rates_from(..., timeframe=1, ...)`), kept
        # separate from `self._rate` (M15) since a real gateway would never conflate the two. Set so the
        # derived offset (against `make_broker_offset`'s default REAL wall-clock `system_clock`) shifts
        # the M15 bar's corrected `ts_open` comfortably behind real "now" -- see
        # `live_observation/tests/test_entrypoint.py::_closed_bar_gateway` for the same derivation.
        self._m1_probe_rate = {
            "time": AS_OF + 1_740, "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "tick_volume": 1,
        }
        self._tick = _FakeTick()

    def initialize(
        self,
        path: str | None = None,
        login: int | None = None,
        password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def terminal_info(self) -> Any:
        return None

    def account_info(self) -> Any:
        return None

    def symbols_get(self) -> Any:
        return ()

    def symbol_info(self, symbol: str) -> Any:
        return None

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any:
        return self._tick

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        if timeframe == 1:
            return [self._m1_probe_rate]
        return [self._rate]

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def positions_get(self, symbol: str | None = None) -> Any:
        return ()

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")


class _FakeTick:
    bid = 99.9
    ask = 100.1
    time = AS_OF + 900  # at or after the bar's own ts_close -- make_broker_clock reads this as "now"


def test_build_loop_wires_a_working_loop_that_records_an_observation(tmp_path: Path) -> None:
    gateway = _FakeGateway()
    state_store = SqliteStateStore(tmp_path / "state.db")
    try:
        loop = build_loop(gateway, state_store, symbol=SYMBOL)
        loop.tick()

        journal = SpreadObservationLog(state_store)
        assert len(journal.entries) == 1
        obs = journal.entries[0]
        assert obs.bid == 99.9
        assert obs.ask == 100.1
        assert obs.symbol == SYMBOL
    finally:
        state_store.close()
