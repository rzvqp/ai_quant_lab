"""Tests for the RuntimeEvaluator base class: SetupResult -> detect/generate_signal/explain_signal
dict translation, and per-context caching."""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.strategy_manager.contract import parse_contract
from ai_trader.strategy_runtime.evaluator import RuntimeEvaluator, RuntimeStrategyHandle, SetupResult

S1_CONTRACT_PATH = Path(__file__).resolve().parents[3] / "knowledge" / "strategies" / "S01_confirmed_liquidity_sweep_reversal" / "strategy.json"


def load_s1_contract():  # type: ignore[no-untyped-def]
    return parse_contract(json.loads(S1_CONTRACT_PATH.read_text(encoding="utf-8")))


class _CountingEvaluator(RuntimeEvaluator):
    """Counts how many times ``evaluate()`` actually runs, to prove per-context caching."""

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(*args, **kwargs)
        self.call_count = 0
        self.next_result: SetupResult = SetupResult.no_setup("default")

    def evaluate(self, context):  # type: ignore[no-untyped-def]
        self.call_count += 1
        return self.next_result


def make_context(as_of: int = 1000, symbol: str = "XAUUSD") -> dict:  # type: ignore[type-arg]
    return {"meta": {"as_of": as_of, "symbol": symbol}, "data_quality": {"level": "OK"}, "timeframes": {}}


def make_evaluator() -> _CountingEvaluator:
    contract = load_s1_contract()
    return _CountingEvaluator("S1", contract, frozenset({"XAUUSD"}))


def test_required_context_is_pure_function_of_contract() -> None:
    ev = make_evaluator()
    required = ev.required_context()
    assert "M15" in required.timeframes


def test_health_ok_by_default() -> None:
    ev = make_evaluator()
    assert ev.health(make_context(), None) == {"state": "OK"}


def test_health_disabled_on_stale_data_quality() -> None:
    ev = make_evaluator()
    ctx = make_context()
    ctx["data_quality"] = {"level": "STALE"}
    assert ev.health(ctx, None) == {"state": "DISABLED"}


def test_can_trade_allows_by_default() -> None:
    ev = make_evaluator()
    assert ev.can_trade(make_context(), None) == {"allowed": True}


def test_evaluate_is_cached_across_the_three_calls_for_the_same_context() -> None:
    ev = make_evaluator()
    ev.next_result = SetupResult.no_setup("nope")
    ctx = make_context(as_of=555)
    ev.detect(ctx)
    ev.generate_signal(ctx)
    ev.explain_signal(ctx)
    assert ev.call_count == 1  # cached across all three calls for the SAME (symbol, as_of)


def test_cache_invalidates_on_new_context() -> None:
    ev = make_evaluator()
    ev.next_result = SetupResult.no_setup("nope")
    ev.detect(make_context(as_of=1))
    ev.detect(make_context(as_of=2))
    assert ev.call_count == 2


def test_no_setup_translates_to_detect_false() -> None:
    ev = make_evaluator()
    ev.next_result = SetupResult.no_setup("no pattern")
    ctx = make_context()
    assert ev.detect(ctx) == {"setup_forming": False, "reason": "no pattern"}


def test_waiting_translates_to_present_true_confirmations_false() -> None:
    ev = make_evaluator()
    ev.next_result = SetupResult.waiting(
        direction="LONG", strength=0.4, confidence="LOW", regime=None,
        triggered_conditions=("X",), headline="waiting",
    )
    ctx = make_context()
    assert ev.detect(ctx) == {"setup_forming": True, "reason": None}
    signal = ev.generate_signal(ctx)
    assert signal["present"] is True
    assert signal["required_confirmations_met"] is False
    assert signal["entry"] is None and signal["stop"] is None


def test_actionable_translates_to_full_trade_params() -> None:
    ev = make_evaluator()
    ev.next_result = SetupResult.actionable(
        direction="LONG", entry=100.0, stop=98.0, target=104.0, strength=0.6, confidence="LOW",
        regime=None, risk_R=2.0, triggered_conditions=("A", "B"), headline="confirmed",
    )
    ctx = make_context()
    signal = ev.generate_signal(ctx)
    assert signal == {
        "present": True, "direction": "LONG", "required_confirmations_met": True,
        "strength": 0.6, "confidence": "LOW", "regime": None,
        "entry": 100.0, "stop": 98.0, "target": 104.0, "risk_R": 2.0,
    }
    explanation = ev.explain_signal(ctx)
    assert explanation["headline"] == "confirmed"
    assert explanation["triggered_conditions"] == ["A", "B"]


def test_runtime_strategy_handle_satisfies_signal_engine_protocol() -> None:
    """``StrategyHandleLike``/``StrategyApiLike`` are plain (non-runtime-checkable) ``Protocol``s, so
    the real proof is structural/behavioral: Signal Engine's own pipeline can call every method it
    needs, exactly as it would on the real ``StrategyHandle``."""
    from ai_trader.signal_engine.pipeline import run_pipeline

    ev = make_evaluator()
    ev.next_result = SetupResult.no_setup("no pattern")
    handle = RuntimeStrategyHandle(id="S1", contract=ev.contract, api=ev)
    # An empty `timeframes` context correctly short-circuits at Context Validation
    # (`required_context()` -> `missing_context_items`) before `detect()` is ever called -- proving
    # the pipeline can call every StrategyHandleLike/StrategyApiLike method it needs on this object,
    # exactly as it would the real StrategyHandle.
    outcome = run_pipeline(make_context(), handle, trader_state=None)
    assert outcome.state.value == "NEED_CONTEXT"
    assert ev.call_count == 0  # evaluate() is never reached -- detect() wasn't called
