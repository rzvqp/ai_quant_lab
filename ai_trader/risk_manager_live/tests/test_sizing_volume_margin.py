"""The two genuinely NEW checks this phase adds (never in the frozen `risk_manager` package): volume-step
rounding/clamping and free-margin sufficiency. Plus the full ALLOW path, proving every field the CEO
explicitly requested is populated correctly."""

from __future__ import annotations

from ai_trader.risk_manager_live.engine import evaluate_trade_proposal
from ai_trader.risk_manager_live.reason_codes import INSUFFICIENT_FREE_MARGIN, VOLUME_STEP_ROUNDING_BELOW_MIN
from ai_trader.risk_manager_live.tests._fixtures import (
    make_account,
    make_config,
    make_instrument,
    make_portfolio,
    make_proposal,
    make_risk_context,
)


def test_full_allow_path_populates_every_ceo_required_field() -> None:
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), make_instrument(), make_risk_context(),
        make_config(),
    )
    assert decision.approved is True
    assert decision.reason_codes == ()
    assert decision.requested_risk == 0.005  # RiskConfig's own default risk_per_trade_pct, unmodified
    assert decision.approved_risk is not None and decision.approved_risk <= decision.requested_risk
    assert decision.calculated_volume is not None and decision.calculated_volume > 0
    assert decision.monetary_risk is not None and decision.monetary_risk > 0
    assert decision.stop_distance == 10.0
    assert decision.margin_estimate is not None and decision.margin_estimate > 0
    assert len(decision.calculation_trace) > 0


def test_calculated_volume_is_rounded_to_lot_step() -> None:
    instrument = make_instrument(lot_step=0.1)  # coarser step than the default 0.01
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(), make_portfolio(), instrument, make_risk_context(), make_config(),
    )
    if decision.approved:
        assert decision.calculated_volume is not None
        # volume / lot_step must be (very nearly) an integer -- proves rounding actually happened
        ratio = decision.calculated_volume / instrument.lot_step
        assert abs(ratio - round(ratio)) < 1e-6


def test_volume_below_min_after_rounding_denies() -> None:
    """A tiny account combined with a coarse lot_step and a high min_volume floor makes even the
    risk-approved size round down to zero -- must DENY, never approve a phantom position."""
    instrument = make_instrument(lot_step=1.0, min_volume=1.0)  # 1 full lot minimum
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(equity=1000.0, margin_free=1000.0),
        make_portfolio(equity=1000.0, equity_high_water_mark=1000.0), instrument, make_risk_context(),
        make_config(),
    )
    assert decision.approved is False
    assert VOLUME_STEP_ROUNDING_BELOW_MIN in decision.reason_codes


def test_volume_clamped_to_max_volume() -> None:
    """A huge account with a very low max_volume ceiling -- the resulting volume must never exceed
    max_volume, and must still be a valid multiple of lot_step."""
    instrument = make_instrument(max_volume=0.5, lot_step=0.01)
    decision = evaluate_trade_proposal(
        make_proposal(), make_account(equity=50_000_000.0, margin_free=50_000_000.0),
        make_portfolio(equity=50_000_000.0, equity_high_water_mark=50_000_000.0), instrument,
        make_risk_context(), make_config(),
    )
    if decision.approved:
        assert decision.calculated_volume is not None
        assert decision.calculated_volume <= instrument.max_volume


def test_insufficient_free_margin_denies() -> None:
    """Ample equity (so sizing/volume succeed) but near-zero free margin (e.g. margin already
    committed elsewhere) -- must DENY on the free-margin gate specifically, not silently approve."""
    account = make_account(equity=200_000.0, margin_free=1.0)  # equity is fine, but margin_free is not
    decision = evaluate_trade_proposal(
        make_proposal(), account, make_portfolio(), make_instrument(), make_risk_context(), make_config(),
    )
    assert decision.approved is False
    assert INSUFFICIENT_FREE_MARGIN in decision.reason_codes


def test_margin_estimate_reflects_leverage() -> None:
    account_low_leverage = make_account(leverage=1.0)  # 1:1 -- margin_estimate should equal full notional
    decision = evaluate_trade_proposal(
        make_proposal(), account_low_leverage, make_portfolio(), make_instrument(), make_risk_context(),
        make_config(),
    )
    if decision.approved:
        assert decision.margin_estimate is not None and decision.calculated_volume is not None
        expected_notional = decision.calculated_volume * 100.0 * 2000.0  # contract_size * entry
        assert abs(decision.margin_estimate - expected_notional) < 1e-6


def test_determinism_same_input_same_output() -> None:
    args = (
        make_proposal(), make_account(), make_portfolio(), make_instrument(), make_risk_context(),
        make_config(),
    )
    d1 = evaluate_trade_proposal(*args)
    d2 = evaluate_trade_proposal(*args)
    assert d1 == d2
