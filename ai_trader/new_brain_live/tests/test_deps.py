"""`NewBrainLiveDepsFactory` tests -- with fakes only, never a real terminal."""

from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_live.deps import NewBrainLiveDepsFactory
from ai_trader.new_brain_live.tests._fixtures import CONTRACT_SIZE, SYMBOL, TICK_SIZE, TICK_VALUE, FakeNewBrainLiveGateway


def test_account_and_instrument_are_real_reads_not_fixtures(tmp_path: Path) -> None:
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(), tmp_path)
    account = factory.account()
    instrument = factory.instrument()
    assert account.balance == 10_000.0
    assert instrument.point_value == TICK_VALUE / TICK_SIZE


def test_point_value_per_unit_formula_matches_pdh_pdl_precedent(tmp_path: Path) -> None:
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(), tmp_path)
    config = factory.risk_config()
    expected_per_unit = TICK_VALUE / TICK_SIZE / CONTRACT_SIZE
    assert config.sizing.point_value[SYMBOL] == expected_per_unit


def test_spread_falls_back_to_a_conservative_nonzero_placeholder_when_tick_unreadable(tmp_path: Path) -> None:
    """`symbol_info_tick` returns `None` (transient real-feed gap) -- the reference-spread filter must
    still reflect a real, non-zero, disclosed placeholder, never silently 0.0 (which would UNDERSTATE
    cost, the wrong fail direction)."""
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(tick=None), tmp_path)
    config = factory.risk_config()
    assert config.filters.reference_spread[SYMBOL] > 0.0


def test_reference_spread_reflects_a_real_tick_when_available(tmp_path: Path) -> None:
    from types import SimpleNamespace

    tick = SimpleNamespace(bid=2400.0, ask=2400.5, time=1_700_000_000)
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(tick=tick), tmp_path)
    config = factory.risk_config()
    assert config.filters.reference_spread[SYMBOL] == 0.5 * 3


def test_portfolio_state_is_a_real_read(tmp_path: Path) -> None:
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(), tmp_path)
    portfolio = factory.portfolio()
    assert portfolio.equity == 10_000.0


def test_risk_context_carries_the_requested_as_of(tmp_path: Path) -> None:
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(), tmp_path)
    context = factory.risk_context(as_of=1_700_000_000)
    assert context.as_of == 1_700_000_000
    assert SYMBOL in context.per_symbol


def test_state_persists_via_the_state_dir(tmp_path: Path) -> None:
    factory = NewBrainLiveDepsFactory(SYMBOL, FakeNewBrainLiveGateway(), tmp_path)
    factory.portfolio()
    assert (tmp_path / "new_brain_live_pnl_state.db").exists()
