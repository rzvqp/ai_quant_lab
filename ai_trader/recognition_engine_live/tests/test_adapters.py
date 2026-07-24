from __future__ import annotations

from ai_trader.context_memory.enums import ContextTrendDirection
from ai_trader.recognition_engine_live.adapters import build_context_snapshot
from ai_trader.recognition_engine_live.tests._fixtures import make_mi_snapshot


def test_translates_session_and_trend_verbatim() -> None:
    snapshot = build_context_snapshot(make_mi_snapshot(session_name="NY"))
    assert snapshot.session_state == "NY"
    assert snapshot.trend_m15 is ContextTrendDirection.UP


def test_translates_symbol_and_as_of() -> None:
    snapshot = build_context_snapshot(make_mi_snapshot())
    assert snapshot.instrument == "XAUUSD"
    assert snapshot.as_of == 1_700_000_000
