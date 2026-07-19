"""Unit tests for :class:`ai_trader.context_memory.contracts.ContextSnapshot`."""

from __future__ import annotations

import dataclasses

import pytest

from ai_trader.context_memory.contracts import ContextSnapshot
from ai_trader.context_memory.enums import ContextTrendDirection
from ai_trader.context_memory.identities import compute_context_snapshot_id
from ai_trader.context_memory.tests._fixtures import make_snapshot
from ai_trader.context_memory.validation import ContextMemoryValidationError


def test_valid_construction() -> None:
    snap = make_snapshot()
    assert snap.instrument == "XAUUSD"
    assert snap.as_of == 1_700_000_000


def test_immutable() -> None:
    snap = make_snapshot()
    with pytest.raises(dataclasses.FrozenInstanceError):
        snap.instrument = "EURUSD"  # type: ignore[misc]


def test_rejects_empty_instrument() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(instrument="")


def test_rejects_non_positive_as_of() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(as_of=0)
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(as_of=-5)


def test_rejects_non_int_as_of() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(as_of="1700000000")
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(as_of=1700000000.5)


def test_rejects_non_numeric_confidence_score() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(context_confidence_score="high")


def test_rejects_wrong_enum_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(trend_m15="UP")  # a raw string, not ContextTrendDirection.UP


def test_rejects_confidence_score_outside_unit_interval() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(context_confidence_score=1.5)
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(context_confidence_score=-0.1)


def test_rejects_non_finite_confidence_score() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(context_confidence_score=float("nan"))
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(context_confidence_score=float("inf"))


def test_confidence_score_none_is_accepted() -> None:
    snap = make_snapshot(context_confidence_score=None)
    assert snap.context_confidence_score is None


def test_session_state_none_is_accepted() -> None:
    snap = make_snapshot(session_state=None)
    assert snap.session_state is None


def test_no_future_data_fields() -> None:
    forbidden = {
        "realized_return", "future_price", "mfe", "mae", "max_favorable_excursion",
        "max_adverse_excursion", "win_loss_label", "trade_result", "future_volatility",
        "strategy_verdict", "execution_result", "pnl", "pnl_r",
    }
    actual_fields = {f.name for f in dataclasses.fields(ContextSnapshot)}
    assert actual_fields.isdisjoint(forbidden), f"forbidden future-data fields present: {actual_fields & forbidden}"


def test_id_is_deterministic() -> None:
    a = make_snapshot()
    b = make_snapshot()
    assert compute_context_snapshot_id(a) == compute_context_snapshot_id(b)


def test_id_differs_on_material_change() -> None:
    a = make_snapshot()
    b = make_snapshot(trend_m15=ContextTrendDirection.DOWN)
    assert compute_context_snapshot_id(a) != compute_context_snapshot_id(b)


def test_id_differs_on_as_of() -> None:
    a = make_snapshot(as_of=1_700_000_000)
    b = make_snapshot(as_of=1_700_000_900)
    assert compute_context_snapshot_id(a) != compute_context_snapshot_id(b)


def test_rejects_wrong_market_intelligence_schema_version_type() -> None:
    with pytest.raises(ContextMemoryValidationError):
        make_snapshot(market_intelligence_schema_version="mi-v1")  # a raw string, not a SchemaVersion


def test_id_fixed_expected_value() -> None:
    # A hardcoded, independently-computed expected hash -- NOT computed via the same production helper
    # this test would otherwise be validating circularly. Any future accidental change to the ID
    # algorithm (canonicalization rules, field set, hash function) must be caught here.
    snap = make_snapshot()
    result = compute_context_snapshot_id(snap)
    assert result.value == "5c7478f8f517010ccd7ac0c9039cc52667d9fbd4ba64e298b5be6bb05c578312"
