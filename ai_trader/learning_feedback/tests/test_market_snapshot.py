"""Tests for market_snapshot.py / observation_builder.py -- Architectural Decision Package Decision 4
(Option C). Every Market Intelligence / Edge Intelligence call uses REAL, unmodified production code
against a real ``MarketContext`` -- never a fabricated or degraded snapshot, per the CEO's own explicit
instruction.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.context_memory.enums import ContextEdgeStatus
from ai_trader.decision_intelligence_v2.adapters import build_context_snapshot
from ai_trader.learning_feedback.market_snapshot import MarketSnapshotBundle, build_market_snapshot
from ai_trader.learning_feedback.observation_builder import build_decision_observation
from ai_trader.market_intelligence.engine import build_market_intelligence
from ai_trader.market_intelligence.tests._fixtures import AS_OF, make_context
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict


def _empty_library(tmp_path: Path) -> Path:
    lib = tmp_path / "empty_library"
    lib.mkdir()
    return lib


def _library_with_registered_strategy(tmp_path: Path, strategy_id: str = "S1") -> Path:
    """A temp Strategy Library containing exactly ONE schema-valid contract, for a strategy id that is
    genuinely registered in Strategy Runtime's own registry (`S1`) -- so `evaluate_edges`'s own
    `registered & contracts.keys()` intersection is non-empty, exercising the real production
    intersection logic rather than a fabricated stand-in for it."""
    lib = tmp_path / "library_with_s1"
    folder = lib / f"{strategy_id}_test"
    folder.mkdir(parents=True)
    contract_dict = make_contract_dict(id=strategy_id)
    (folder / "strategy.json").write_text(json.dumps(contract_dict), encoding="utf-8")
    return lib


# ------------------------------------------------------------------ build_market_snapshot


def test_build_market_snapshot_returns_real_mi_and_ei(tmp_path: Path) -> None:
    context = make_context()
    bundle = build_market_snapshot(context, library_path=_empty_library(tmp_path))
    assert isinstance(bundle, MarketSnapshotBundle)
    assert bundle.mi_snapshot == build_market_intelligence(context)  # byte-for-byte real, not fabricated
    assert bundle.ei_snapshot.symbol == bundle.mi_snapshot.symbol
    assert bundle.ei_snapshot.as_of == bundle.mi_snapshot.as_of


def test_build_market_snapshot_empty_library_yields_no_readings(tmp_path: Path) -> None:
    bundle = build_market_snapshot(make_context(), library_path=_empty_library(tmp_path))
    assert bundle.ei_snapshot.readings == {}


def test_build_market_snapshot_is_deterministic(tmp_path: Path) -> None:
    lib = _empty_library(tmp_path)
    context = make_context()
    a = build_market_snapshot(context, library_path=lib)
    b = build_market_snapshot(context, library_path=lib)
    assert a.mi_snapshot == b.mi_snapshot
    assert a.ei_snapshot == b.ei_snapshot


def test_build_market_snapshot_with_registered_strategy_produces_a_reading(tmp_path: Path) -> None:
    lib = _library_with_registered_strategy(tmp_path, "S1")
    bundle = build_market_snapshot(make_context(), library_path=lib)
    assert "S1" in bundle.ei_snapshot.readings


# ------------------------------------------------------------------ build_decision_observation


def test_build_decision_observation_context_snapshot_matches_direct_adapter_call(tmp_path: Path) -> None:
    lib = _empty_library(tmp_path)
    context = make_context()
    bundle = build_market_snapshot(context, library_path=lib)
    observation = build_decision_observation(bundle, library_path=lib)
    assert observation.context_snapshot == build_context_snapshot(bundle.mi_snapshot)


def test_build_decision_observation_no_present_edges_when_library_empty(tmp_path: Path) -> None:
    lib = _empty_library(tmp_path)
    bundle = build_market_snapshot(make_context(), library_path=lib)
    observation = build_decision_observation(bundle, library_path=lib)
    assert observation.present_edges == ()


def test_build_decision_observation_includes_a_present_or_possible_reading(tmp_path: Path) -> None:
    lib = _library_with_registered_strategy(tmp_path, "S1")
    bundle = build_market_snapshot(make_context(), library_path=lib)
    observation = build_decision_observation(bundle, library_path=lib)

    reading = bundle.ei_snapshot.readings["S1"]
    matching = [ref for ref in observation.present_edges if ref.strategy_id == "S1"]
    if reading.state.value == "ABSENT":
        assert matching == []  # never fabricated -- ABSENT never gets a PresentEdgeReference
    else:
        assert len(matching) == 1
        assert matching[0].declared_status is ContextEdgeStatus(reading.state.value)


def test_build_decision_observation_is_a_valid_observation(tmp_path: Path) -> None:
    # Observation.__post_init__'s own invariants (no duplicate strategy_id, canonical sort order) are
    # exercised for free by successful construction -- this is a real Observation, not a stand-in.
    lib = _library_with_registered_strategy(tmp_path, "S1")
    bundle = build_market_snapshot(make_context(), library_path=lib)
    observation = build_decision_observation(bundle, library_path=lib)
    strategy_ids = [ref.strategy_id for ref in observation.present_edges]
    assert strategy_ids == sorted(strategy_ids)
    assert len(strategy_ids) == len(set(strategy_ids))
