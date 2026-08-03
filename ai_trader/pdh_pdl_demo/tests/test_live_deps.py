"""`LivePdhPdlDepsFactory` tests -- with fakes only, never a real terminal. Proves the twice-corrected
`point_value` derivation (per-lot `InstrumentSpecification.point_value` vs. per-unit
`RiskConfig.sizing.point_value`, `XAUUSD_INFRA_TEST_REPORT.md` attempt 2) is wired correctly here, that
`risk_per_trade_pct` is never touched, and that `demo_deps.adapter` is the SAME object identity
`send_after_dry_run_gate` requires."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from ai_trader.mt5_demo_execution.adapter import MT5DemoBrokerAdapter
from ai_trader.mt5_demo_execution.tests._fixtures import AS_OF, FakeMT5DemoGateway
from ai_trader.mt5_demo_execution.types import MT5DemoConfig
from ai_trader.pdh_pdl_demo.live_deps import LivePdhPdlDepsFactory
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER, STRATEGY_ID, PdhPdlTrigger
from ai_trader.pdh_pdl_demo.risk_snapshot import LiveRiskSnapshotBuilder
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.live_signal_source.types import LiveCandidate
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"
TICK_VALUE = 1.0
TICK_SIZE = 0.01
CONTRACT_SIZE = 100.0


class _FakeHistoryGateway:
    """Satisfies `MT5AccountBridge` (account_info/symbol_select/symbol_info) AND
    `MT5PortfolioStateSource` (positions_get/history_deals_get) AND `LivePdhPdlDepsFactory`'s own raw
    `symbol_info` point_value read -- one gateway, several real consumers, matching production wiring."""

    def __init__(self) -> None:
        self.account = SimpleNamespace(
            trade_mode=0, currency="USD", balance=10_026.83, equity=10_026.83, margin=0.0,
            margin_free=10_026.83, margin_level=None, leverage=100,
        )
        self.symbol = SimpleNamespace(
            trade_tick_size=TICK_SIZE, volume_step=0.01, volume_min=0.01, volume_max=100.0,
            trade_contract_size=CONTRACT_SIZE, trade_tick_value=TICK_VALUE, currency_margin="USD",
        )

    def initialize(
        self, path: str | None = None, login: int | None = None, password: str | None = None,
        server: str | None = None,
    ) -> bool:
        return True

    def shutdown(self) -> None:
        pass

    def terminal_info(self) -> Any:
        return None

    def account_info(self) -> Any:
        return self.account

    def symbols_get(self) -> Any:
        return ()

    def symbol_info(self, symbol: str) -> Any:
        return self.symbol

    def symbol_select(self, symbol: str, enable: bool = True) -> bool:
        return True

    def symbol_info_tick(self, symbol: str) -> Any:
        return None

    def copy_rates_from(self, symbol: str, timeframe: int, date_from: int, count: int) -> Any:
        return None

    def copy_rates_range(self, symbol: str, timeframe: int, date_from: int, date_to: int) -> Any:
        return None

    def copy_ticks_from(self, symbol: str, date_from: int, count: int, flags: int) -> Any:
        return None

    def copy_ticks_range(self, symbol: str, date_from: int, date_to: int, flags: int) -> Any:
        return None

    def orders_get(self, symbol: str | None = None) -> Any:
        return ()

    def last_error(self) -> tuple[int, str]:
        return (0, "Success")

    def positions_get(self, symbol: str | None = None) -> tuple[Any, ...] | None:
        return ()

    def history_deals_get(self, date_from: int, date_to: int) -> tuple[Any, ...] | None:
        return ()


def _make_demo_adapter() -> MT5DemoBrokerAdapter:
    demo_gateway = FakeMT5DemoGateway(tick_time=AS_OF)
    demo_adapter = MT5DemoBrokerAdapter(gateway=demo_gateway, config=MT5DemoConfig(max_order_volume=1000.0))
    demo_adapter.connect()
    return demo_adapter


def _candidate() -> LiveCandidate:
    return LiveCandidate(
        strategy_id=STRATEGY_ID, symbol=SYMBOL, direction=Direction.SHORT, entry=4054.6, stop=4056.0,
        target=4040.0, session="ny", magic_number=MAGIC_NUMBER, comment="CAND-0001 PDH-PDL DEMO", as_of=AS_OF,
    )


def _trigger() -> PdhPdlTrigger:
    return PdhPdlTrigger(
        touch_idx=10, entry_idx=11, direction=-1, strategy_stop_price=4056.0, target_price=4040.0,
        atr_at_touch=1.0, day_boundary_label=1_705_356_000, effective_spread=0.07,
        executable_stop_price=4056.5, tick_size=TICK_SIZE,
    )


def test_point_value_per_unit_formula_used_for_sizing(tmp_path: Path) -> None:
    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    bundle = factory(_candidate(), _trigger())
    expected_per_unit = TICK_VALUE / TICK_SIZE / CONTRACT_SIZE
    assert bundle.demo_deps.risk_config.sizing.point_value[SYMBOL] == expected_per_unit
    assert bundle.dry_run_deps.risk_config.sizing.point_value[SYMBOL] == expected_per_unit


def test_instrument_specification_point_value_stays_per_lot_unmodified(tmp_path: Path) -> None:
    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    bundle = factory(_candidate(), _trigger())
    expected_per_lot = TICK_VALUE / TICK_SIZE
    assert bundle.demo_deps.instrument.point_value == expected_per_lot


def test_risk_per_trade_pct_left_at_default(tmp_path: Path) -> None:
    from ai_trader.risk_manager.config import RiskConfig

    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    bundle = factory(_candidate(), _trigger())
    assert bundle.demo_deps.risk_config.sizing.risk_per_trade_pct == RiskConfig().sizing.risk_per_trade_pct


def test_demo_deps_adapter_is_the_same_object_identity_as_the_injected_demo_adapter(tmp_path: Path) -> None:
    demo_adapter = _make_demo_adapter()
    factory = LivePdhPdlDepsFactory(SYMBOL, _FakeHistoryGateway(), demo_adapter, LiveRiskSnapshotBuilder(), tmp_path)
    bundle = factory(_candidate(), _trigger())
    assert bundle.demo_deps.adapter is demo_adapter  # type: ignore[comparison-overlap]
    assert bundle.demo_adapter is demo_adapter


def test_reference_spread_filter_derived_from_trigger_effective_spread(tmp_path: Path) -> None:
    """Above the `max(..., 1.0)` floor -- a wide spread must be reflected, not clamped away."""
    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    wide_spread_trigger = PdhPdlTrigger(
        touch_idx=10, entry_idx=11, direction=-1, strategy_stop_price=4056.0, target_price=4040.0,
        atr_at_touch=1.0, day_boundary_label=1_705_356_000, effective_spread=0.5,
        executable_stop_price=4056.5, tick_size=TICK_SIZE,
    )
    bundle = factory(_candidate(), wide_spread_trigger)
    assert bundle.demo_deps.risk_config.filters.reference_spread[SYMBOL] == 0.5 * 3


def test_reference_spread_filter_has_a_floor_for_narrow_spreads(tmp_path: Path) -> None:
    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    bundle = factory(_candidate(), _trigger())  # effective_spread=0.07 -> *3=0.21, floored to 1.0
    assert bundle.demo_deps.risk_config.filters.reference_spread[SYMBOL] == 1.0


def test_state_persists_across_repeated_calls_via_the_same_state_dir(tmp_path: Path) -> None:
    factory = LivePdhPdlDepsFactory(
        SYMBOL, _FakeHistoryGateway(), _make_demo_adapter(), LiveRiskSnapshotBuilder(), tmp_path,
    )
    bundle1 = factory(_candidate(), _trigger())
    bundle2 = factory(_candidate(), _trigger())
    assert (tmp_path / "pdh_pdl_pnl_state.db").exists()
    assert bundle1.demo_deps.ledger is bundle2.demo_deps.ledger  # same ledger reused, not rebuilt per call
