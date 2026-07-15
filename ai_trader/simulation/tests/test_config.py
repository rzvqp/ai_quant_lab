"""Tests for ``SimulationContext``/config validation."""

from __future__ import annotations

import pytest

from ai_trader.simulation.config import DateRange, MarginModel, SimulationContext
from ai_trader.simulation.exceptions import InvalidContextError


def _ctx(**overrides: object) -> SimulationContext:
    defaults: dict[str, object] = dict(
        run_id="R1", date_range=DateRange(1_600_000_000, 1_600_100_000), symbols=("XAUUSD",),
        timeframes=("M15",), starting_balance=100_000.0, run_seed=1,
    )
    defaults.update(overrides)
    return SimulationContext(**defaults)  # type: ignore[arg-type]


def test_valid_context_constructs() -> None:
    ctx = _ctx()
    assert ctx.deterministic is True


def test_empty_run_id_rejected() -> None:
    with pytest.raises(InvalidContextError):
        _ctx(run_id="")


def test_empty_symbols_rejected() -> None:
    with pytest.raises(InvalidContextError):
        _ctx(symbols=())


def test_base_timeframe_must_be_in_timeframes() -> None:
    with pytest.raises(InvalidContextError):
        _ctx(timeframes=("H1",), base_timeframe="M15")


def test_non_positive_starting_balance_rejected() -> None:
    with pytest.raises(InvalidContextError):
        _ctx(starting_balance=0.0)


def test_date_range_start_must_be_before_end() -> None:
    with pytest.raises(InvalidContextError):
        DateRange(100, 100)


def test_margin_model_requires_maintenance_below_initial() -> None:
    with pytest.raises(InvalidContextError):
        MarginModel(initial_margin_pct=0.01, maintenance_margin_pct=0.02)


def test_seed_for_is_deterministic_and_key_sensitive() -> None:
    ctx = _ctx(run_seed=7)
    a1 = ctx.seed_for("order-1:100")
    a2 = ctx.seed_for("order-1:100")
    b = ctx.seed_for("order-2:100")
    assert a1 == a2
    assert a1 != b


def test_seed_for_differs_across_run_seed() -> None:
    ctx1 = _ctx(run_seed=1)
    ctx2 = _ctx(run_seed=2)
    assert ctx1.seed_for("k") != ctx2.seed_for("k")
