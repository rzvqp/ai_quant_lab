from __future__ import annotations

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.risk_sizer import (
    INVALID_EQUITY,
    INVALID_SL_DISTANCE,
    LOSS_CALCULATION_FAILED,
    MIN_VOLUME_EXCEEDS_RISK_BUDGET,
    compute_risk_sized_volume,
)
from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.tests._fixtures import FakeMT5BridgeGateway
from ai_trader.signal_engine.types import Direction

SYMBOL = "XAUUSD"


def _size(**overrides: object) -> object:
    gw = overrides.pop("gateway", None) or FakeMT5BridgeGateway(order_calc_profit_result=-10.0)  # $10 loss per lot
    kwargs: dict[str, object] = dict(
        gateway=gw, equity=10_000.0, side=Direction.LONG, symbol=SYMBOL, entry_price=2000.0, sl_price=1990.0,
        volume_min=0.01, volume_max=100.0, volume_step=0.01, risk_fraction=0.05,
    )
    kwargs.update(overrides)
    return compute_risk_sized_volume(**kwargs)  # type: ignore[arg-type]


def test_5pct_equity_sizing_basic() -> None:
    # risk_budget = 10000*0.05 = 500; loss_per_1_lot = 10; raw_volume = 50.0
    result = _size()
    assert result.approved is True  # type: ignore[attr-defined]
    assert abs(result.volume - 50.0) < 1e-9  # type: ignore[attr-defined]
    assert abs(result.modeled_risk_fraction - 0.05) < 1e-9  # type: ignore[attr-defined]


def test_current_equity_change_affects_lot_size() -> None:
    small = _size(equity=1_000.0)
    large = _size(equity=50_000.0, volume_max=10_000.0)  # raise volume_max so this isn't the thing capping it
    assert small.volume < large.volume  # type: ignore[attr-defined]
    assert abs(small.volume - 5.0) < 1e-9  # type: ignore[attr-defined]  # 1000*0.05/10
    assert abs(large.volume - 250.0) < 1e-9  # type: ignore[attr-defined]  # 50000*0.05/10


def test_wide_sl_produces_smaller_lot_than_narrow_sl() -> None:
    gw_wide = FakeMT5BridgeGateway(order_calc_profit_result=-100.0)  # bigger loss per lot for a wider SL
    gw_narrow = FakeMT5BridgeGateway(order_calc_profit_result=-10.0)
    wide = _size(gateway=gw_wide, sl_price=1900.0)
    narrow = _size(gateway=gw_narrow, sl_price=1990.0)
    assert wide.volume < narrow.volume  # type: ignore[attr-defined]


def test_minimum_lot_exceeding_risk_budget_is_rejected() -> None:
    # loss_per_1_lot huge -> even volume_min=0.01 costs more than the 5% budget
    result = _size(gateway=FakeMT5BridgeGateway(order_calc_profit_result=-1_000_000.0), volume_min=0.01)
    assert result.approved is False  # type: ignore[attr-defined]
    assert result.reason == MIN_VOLUME_EXCEEDS_RISK_BUDGET  # type: ignore[attr-defined]


def test_volume_rounds_down_never_up_through_budget() -> None:
    # risk_budget=500, loss_per_1_lot=33 -> raw=15.1515..., step=0.1 -> must floor to 15.1, never 15.2
    result = _size(gateway=FakeMT5BridgeGateway(order_calc_profit_result=-33.0), volume_step=0.1)
    assert result.approved is True  # type: ignore[attr-defined]
    assert abs(result.volume - 15.1) < 1e-9  # type: ignore[attr-defined]
    assert result.modeled_risk_money <= result.risk_budget_money  # type: ignore[attr-defined]


def test_max_lot_cap_never_exceeds_risk_budget_and_reports_actual_risk() -> None:
    # raw_volume=50 exceeds volume_max=10 -> capped, risk drops from 5% to 1%, never increases
    result = _size(volume_max=10.0)
    assert result.approved is True  # type: ignore[attr-defined]
    assert result.capped_by_volume_max is True  # type: ignore[attr-defined]
    assert abs(result.volume - 10.0) < 1e-9  # type: ignore[attr-defined]
    assert abs(result.modeled_risk_fraction - 0.01) < 1e-9  # type: ignore[attr-defined]
    assert result.modeled_risk_fraction < 0.05  # type: ignore[attr-defined]


def test_zero_sl_distance_rejected_long() -> None:
    result = _size(sl_price=2000.0)  # SL == entry
    assert result.approved is False  # type: ignore[attr-defined]
    assert result.reason == INVALID_SL_DISTANCE  # type: ignore[attr-defined]


def test_wrong_side_sl_distance_rejected() -> None:
    result = _size(sl_price=2010.0)  # SL above entry for a LONG -- invalid
    assert result.approved is False  # type: ignore[attr-defined]
    assert result.reason == INVALID_SL_DISTANCE  # type: ignore[attr-defined]


def test_short_side_requires_sl_above_entry() -> None:
    ok = _size(side=Direction.SHORT, entry_price=2000.0, sl_price=2010.0)
    assert ok.approved is True  # type: ignore[attr-defined]
    bad = _size(side=Direction.SHORT, entry_price=2000.0, sl_price=1990.0)
    assert bad.approved is False  # type: ignore[attr-defined]
    assert bad.reason == INVALID_SL_DISTANCE  # type: ignore[attr-defined]


def test_broker_pl_calculation_failure_rejected() -> None:
    result = _size(gateway=FakeMT5BridgeGateway(order_calc_profit_result=None))
    assert result.approved is False  # type: ignore[attr-defined]
    assert result.reason == LOSS_CALCULATION_FAILED  # type: ignore[attr-defined]


def test_invalid_equity_rejected() -> None:
    for bad_equity in (0.0, -100.0, float("nan"), float("inf")):
        result = _size(equity=bad_equity)
        assert result.approved is False  # type: ignore[attr-defined]
        assert result.reason == INVALID_EQUITY  # type: ignore[attr-defined]


def test_never_uses_leverage_or_margin_in_sizing_source() -> None:
    """Mandate section 18 -- static, AST-based proof `compute_risk_sized_volume`'s own function BODY
    never references a `margin`/`leverage` identifier as an input to the size computation (module-level
    docstring prose mentioning the word is fine and expected -- disclosure, not a violation -- so this
    inspects the function's AST, not the raw source text)."""
    import ast
    import inspect

    from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.risk_sizer import compute_risk_sized_volume

    tree = ast.parse(inspect.getsource(compute_risk_sized_volume))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            names.add(node.attr.lower())
    assert not any("margin" in n for n in names)
    assert not any("leverage" in n for n in names)
