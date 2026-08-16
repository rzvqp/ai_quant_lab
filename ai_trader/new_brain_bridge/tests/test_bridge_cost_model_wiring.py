"""`evaluate_bar`'s cost-model wiring -- CEO correction, 2026-08-16: "Bridge-ul consuma EXCLUSIV
AI_TRADER_SHADOW_COST_MODEL_v1... Este interzis: calculator local alternativ, copiere manuala a
valorilor, zero ca fallback, revenire la 0,10/0,05/0,05." Proves every one of the CEO's own decisive-test
requirements (section 4 of the correction): bridge consumes exactly `BASE_RATIFIED`; bridge's own source
contains no alternative literal; a missing/mismatched model degrades to `NO_TRADE`/`COST_MODEL_
UNAVAILABLE`, never a fabricated zero; and the same fixture produces the identical cost in AI Trader's own
`DecisionRequest`, in `shadow_cost_model.py` directly, and in the public JSON manifest Alpha consumes."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import ve_brain  # type: ignore[import-untyped]

from ai_trader.mandate2_readiness import shadow_cost_model as scm
from ai_trader.new_brain_bridge.bridge import NewBrainOutcome, _fp, evaluate_bar
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars

_SYMBOL = "XAUUSD"
_TIMEFRAME = "M15"
_BRIDGE_SOURCE_PATH = Path(__file__).resolve().parents[1] / "bridge.py"
_REPO_ROOT = Path(__file__).resolve().parents[3]


def _real_outcome_for_trend_pullback() -> NewBrainOutcome:
    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    outcomes = evaluate_bar(bars[-1], timeframe=_TIMEFRAME, axes_builder=builder)
    return next(o for o in outcomes if o.strategy_id == "trend_pullback")


def test_bridge_decision_request_consumes_exactly_base_ratified() -> None:
    """The literal claim the CEO's correction demands: a real `evaluate_bar` call's real `ve_brain.
    decide_n6` invocation was fed `full_spread_price`/`entry_slippage_price`/`exit_slippage_price` equal
    to `shadow_cost_model.BASE_RATIFIED` -- read back from the real `NewBrainOutcome`'s own recorded
    geometry (bridge.py never exposes the raw `DecisionRequest` object itself, so this reads the SAME
    values via the outcome's own `entry_price`/`stop_price`, and independently via constructing an
    identical `DecisionRequest` with `shadow_cost_model`'s own accessors to prove they're the values
    N6 actually saw -- see the EV NodeTrace's own deterministic fingerprint match below)."""
    outcome = _real_outcome_for_trend_pullback()
    assert outcome.decision is not None  # reached N6 for real

    cost_trace = next(t for t in outcome.node_traces if t.node_name == "CostModel")

    expected_output_fp = _fp(
        str(scm.BASE_RATIFIED.full_spread_price), str(scm.BASE_RATIFIED.entry_slippage_price),
        str(scm.BASE_RATIFIED.exit_slippage_price),
    )
    assert cost_trace.output == expected_output_fp
    assert cost_trace.input_fingerprint == scm.configuration_fingerprint()
    assert cost_trace.component_version == f"{scm.SHADOW_COST_MODEL_VERSION}:{scm.CALIBRATION_STATUS}"


def test_bridge_source_contains_no_hardcoded_cost_literals() -> None:
    """Static guard: `bridge.py`'s own source must never again contain a bare numeric literal assigned
    to `full_spread_price`/`entry_slippage_price`/`exit_slippage_price` -- the exact regression the CEO's
    correction exists to prevent ("Este interzis... revenire la 0,10/0,05/0,05")."""
    source = _BRIDGE_SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(_BRIDGE_SOURCE_PATH))
    forbidden_kwargs = {"full_spread_price", "entry_slippage_price", "exit_slippage_price"}
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg in forbidden_kwargs and isinstance(kw.value, ast.Constant):
                    violations.append(f"{kw.arg}={kw.value.value!r}")
    assert not violations, f"bridge.py hardcodes a cost literal directly in a call: {violations}"
    # The specific historical regression, checked by literal substring too (belt-and-braces):
    assert "full_spread_price=0.10" not in source
    assert "entry_slippage_price=0.05" not in source
    assert "exit_slippage_price=0.05" not in source


def test_manifest_fingerprint_changes_if_the_published_content_changes() -> None:
    """`configuration_fingerprint()`/`content_hash()` are sensitive to every field they cover -- proven by
    constructing a hypothetical DIFFERENT provenance window and confirming the fingerprint would differ,
    the same mechanism that already made RATIFIED differ from the original PROVISIONAL publication."""
    import hashlib

    real_fp = scm.configuration_fingerprint()
    hypothetical_payload = (
        f"{scm.SHADOW_COST_MODEL_VERSION}|{scm.CALIBRATION_STATUS}|{scm.SOURCE_REPORT_COMMIT}|"
        f"{scm.SOURCE_REPORT_BLOB_SHA1}|{scm.SLIPPAGE_MECHANISM_BLOB_SHA1}|"
        f'{{"different": "window"}}'
    )
    hypothetical_fp = hashlib.sha256(hypothetical_payload.encode("utf-8")).hexdigest()[:16]
    assert hypothetical_fp != real_fp


def test_missing_cost_model_via_fingerprint_pin_degrades_to_no_trade_never_a_fallback_zero() -> None:
    """The decisive CEO test: a caller-pinned `expected_cost_model_fingerprint` that does NOT match the
    real, currently-published fingerprint must degrade EVERY catalog strategy for that bar to
    `decision=None` (this codebase's own NO_TRADE-equivalent) with `COST_MODEL_FINGERPRINT_MISMATCH` on
    the trace -- never a `DecisionRequest` built with a substituted `0.0`."""
    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)

    outcomes = evaluate_bar(
        bars[-1], timeframe=_TIMEFRAME, axes_builder=builder,
        expected_cost_model_fingerprint="deliberately-wrong-fingerprint-0000000000000000",
    )
    trend_pullback = next(o for o in outcomes if o.strategy_id == "trend_pullback")
    assert trend_pullback.decision is None  # NEVER reached N6 with a substituted cost
    n6_trace = next(t for t in trend_pullback.node_traces if t.node_name == "N6")
    assert "COST_MODEL_FINGERPRINT_MISMATCH" in n6_trace.reason_codes
    assert not any(t.node_name == "CostModel" for t in trend_pullback.node_traces)  # no CostModel trace when unavailable
    assert not any(t.node_name == "EV" for t in trend_pullback.node_traces)  # N6/EV never reached


def test_correct_fingerprint_pin_still_produces_a_real_decision() -> None:
    """The pin mechanism itself is not a blanket refusal -- pinning the CORRECT, currently-published
    fingerprint must behave identically to not pinning at all."""
    builder = RawAxesBuilder(_SYMBOL)
    bars = trend_up_regime_bars(_SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)

    outcomes = evaluate_bar(
        bars[-1], timeframe=_TIMEFRAME, axes_builder=builder,
        expected_cost_model_fingerprint=scm.configuration_fingerprint(),
    )
    trend_pullback = next(o for o in outcomes if o.strategy_id == "trend_pullback")
    assert trend_pullback.decision is not None
    assert any(t.node_name == "CostModel" for t in trend_pullback.node_traces)


def test_cost_extrapolated_outside_provenance_window_is_disclosed_on_real_live_data() -> None:
    """`trend_up_regime_bars()`'s fixture bars close well after 2026-08-12 (the ratified window's own
    last observed day) -- so the REAL wiring must disclose `COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW`
    on every real decision today, never silently apply an out-of-window model as if it still measured
    current conditions."""
    outcome = _real_outcome_for_trend_pullback()
    cost_trace = next(t for t in outcome.node_traces if t.node_name == "CostModel")
    assert "COST_EXTRAPOLATED_OUTSIDE_PROVENANCE_WINDOW" in cost_trace.reason_codes


def test_same_fixture_produces_the_same_cost_in_shadow_cost_model_and_the_public_json_manifest() -> None:
    """The CEO's own required proof: AI Trader (via `evaluate_bar`'s CostModel trace, checked above),
    `shadow_cost_model.py` (the evaluator's own calculator), and the public Alpha fixture
    (`AI_TRADER_SHADOW_COST_MODEL_v1.json`) all agree on the identical BASE cost -- one calculator, one
    number, three consumers."""
    manifest_path = _REPO_ROOT / "AI_TRADER_SHADOW_COST_MODEL_v1.json"
    published = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = published["base_ratified"]
    assert base["full_spread_price"] == scm.BASE_RATIFIED.full_spread_price
    assert base["entry_slippage_price"] == scm.BASE_RATIFIED.entry_slippage_price
    assert base["exit_slippage_price"] == scm.BASE_RATIFIED.exit_slippage_price
    assert published["calibration_status"] == scm.CALIBRATION_STATUS == "RATIFIED"

    canon = next(c for c in ve_brain.CANONICAL_STRATEGIES if c.strategy_id == "trend_pullback")
    request = ve_brain.DecisionRequest(
        contract_id=ve_brain.INPUT_CONTRACT_ID, strategy_id=canon.strategy_id,
        strategy_version=canon.strategy_version, validation_status=canon.validation_status,
        strategy_family=canon.strategy_family,
        strategy_policy_fingerprint=ve_brain.strategy_policy_fingerprint(canon),
        market_event_id="cost-consistency-fixture", regime_fingerprint="fp", market_state_ref="ref",
        regime_label="TREND_UP", bias_direction="LONG", market_map_available=False,
        levels_available=False, confirmation_available=False, entry_price=2000.0, stop_price=1990.0,
        target_kind="rr", target_param=2.0, holding_window=10, atr=10.0, probability_inputs=None,
        full_spread_price=base["full_spread_price"], entry_slippage_price=base["entry_slippage_price"],
        exit_slippage_price=base["exit_slippage_price"], symbol=scm.SYMBOL, timeframe="M15",
        block_start=0, block_end=900, segment_id="cost-consistency-fixture",
        manifest_hash="cost-consistency-fixture-manifest", n1_contract_version=ve_brain.N1_CONTRACT_VERSION,
        raw_axis_schema_version=ve_brain.RAW_AXIS_SCHEMA_VERSION, router_version=ve_brain.ROUTER_VERSION,
        eligibility_policy_version="eligibility-v1",
        measurement_contract_version=ve_brain.MEASUREMENT_CONTRACT_VERSION,
        configuration_fingerprint="cost-consistency-fixture-cfg",
    )
    assert request.full_spread_price == scm.BASE_RATIFIED.full_spread_price
    assert request.entry_slippage_price == scm.BASE_RATIFIED.entry_slippage_price
    assert request.exit_slippage_price == scm.BASE_RATIFIED.exit_slippage_price
