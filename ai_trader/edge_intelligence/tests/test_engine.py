"""Unit tests for :mod:`ai_trader.edge_intelligence.engine` -- the public
``evaluate_edges()``/``present_strategy_ids()`` entry points. Uses a synthetic Strategy Library
(``tmp_path``) containing only two REAL, currently-registered strategy ids (S1, S7) so
``evaluate_edges`` -- which always intersects against the true runtime registry, never a
parameterized one -- has exactly two readings to reason about. Real-data integration coverage
against the actual Strategy Library lives in
``ai_trader/edge_intelligence/tests/test_integration.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.edge_intelligence.engine import evaluate_edges, present_strategy_ids
from ai_trader.edge_intelligence.types import EdgeState
from ai_trader.market_intelligence.tests._fixtures import make_bar, make_context
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict

_M15_BARS = [make_bar(1_700_000_000, 2000, 2001, 1999, 2000.5)]

#: All four timeframes trending UP, normal volatility -- a clean, unambiguous, non-contradicting
#: context every dimension can resolve confidently (no UNKNOWN evidence anywhere).
_STRONG_UP_CONTEXT = make_context(
    m15_bars=_M15_BARS,
    m15_features={
        "m_trend_up": True, "h1_trend_up": True, "h4_trend_up": True, "d1_trend_up": True,
        "m_atr": 1.0, "atr_ma": 1.0,
    },
)


def _write_strategy(tmp_path: Path, folder: str, data: dict) -> None:
    strategy_dir = tmp_path / folder
    strategy_dir.mkdir()
    (strategy_dir / "strategy.json").write_text(json.dumps(data), encoding="utf-8")


def _library(tmp_path: Path) -> Path:
    both_contract = make_contract_dict(id="S1")
    both_contract["execution"]["long_short"] = "BOTH"
    both_contract["execution"]["sessions"] = "All sessions"
    _write_strategy(tmp_path, "S1_test", both_contract)

    short_contract = make_contract_dict(id="S7")
    short_contract["execution"]["long_short"] = "SHORT"
    short_contract["execution"]["sessions"] = "All sessions"
    _write_strategy(tmp_path, "S7_test", short_contract)
    return tmp_path


def test_evaluates_every_readable_registered_strategy_in_the_library(tmp_path: Path) -> None:
    snapshot = evaluate_edges(_STRONG_UP_CONTEXT, library_path=_library(tmp_path))
    assert set(snapshot.readings) == {"S1", "S7"}
    for reading in snapshot.readings.values():
        assert len(reading.evidence) == 6


def test_present_vs_absent_from_declared_directional_scope(tmp_path: Path) -> None:
    # S1 declares BOTH (no directional constraint) in a clean, strongly-trending-UP, non-contradicting
    # context -> PRESENT. S7 declares SHORT while the shared context trends UP -> a real, declared
    # contradiction -> ABSENT, regardless of every other dimension.
    snapshot = evaluate_edges(_STRONG_UP_CONTEXT, library_path=_library(tmp_path))
    assert snapshot.readings["S1"].state is EdgeState.PRESENT
    assert snapshot.readings["S7"].state is EdgeState.ABSENT


def test_present_strategy_ids_returns_only_present_ones_sorted(tmp_path: Path) -> None:
    snapshot = evaluate_edges(_STRONG_UP_CONTEXT, library_path=_library(tmp_path))
    assert present_strategy_ids(snapshot) == ("S1",)


def test_strategy_not_in_the_library_produces_no_reading(tmp_path: Path) -> None:
    # A registered strategy (e.g. S2) that has no strategy.json in THIS synthetic library must not
    # appear -- never a fabricated reading for a strategy this layer could not actually read.
    snapshot = evaluate_edges(_STRONG_UP_CONTEXT, library_path=_library(tmp_path))
    assert "S2" not in snapshot.readings


def test_is_deterministic(tmp_path: Path) -> None:
    library_path = _library(tmp_path)
    first = evaluate_edges(_STRONG_UP_CONTEXT, library_path=library_path)
    second = evaluate_edges(_STRONG_UP_CONTEXT, library_path=library_path)
    assert first == second
