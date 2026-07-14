"""Unit tests for :mod:`ai_trader.signal_engine.engine` -- ``SignalEngine`` against controllable
fake strategy handles. Real-Strategy-Manager integration lives in ``test_engine_integration.py``.
"""

from __future__ import annotations

import time
from dataclasses import replace
from typing import Any

import pytest

from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.engine import SignalEngine
from ai_trader.signal_engine.exceptions import EngineNotConfiguredError
from ai_trader.signal_engine.types import EngineOverallHealth, NotFound, QualityFlag, SignalState
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle


def _slow_health(context: object, trader_state: object) -> dict[str, Any]:
    time.sleep(0.5)
    return {"state": "OK"}


class TestConfigurationGate:
    def test_evaluate_before_configure_raises(self) -> None:
        engine = SignalEngine()
        handle, _ = make_fake_handle()
        with pytest.raises(EngineNotConfiguredError):
            engine.evaluate(make_context(), [handle], trader_state=None)

    def test_evaluate_strategy_before_configure_raises(self) -> None:
        engine = SignalEngine()
        handle, _ = make_fake_handle()
        with pytest.raises(EngineNotConfiguredError):
            engine.evaluate_strategy(make_context(), handle, trader_state=None)

    def test_shutdown_before_configure_raises(self) -> None:
        engine = SignalEngine()
        with pytest.raises(EngineNotConfiguredError):
            engine.shutdown()

    def test_configure_is_idempotent(self) -> None:
        engine = SignalEngine()
        engine.configure()
        engine.configure()
        assert engine.statistics().cycles == 0

    def test_health_before_configure_is_failed(self) -> None:
        engine = SignalEngine()
        assert engine.health().overall is EngineOverallHealth.FAILED


class TestEvaluate:
    def test_scoped_handle_is_evaluated(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"XAUUSD"}))
        batch = engine.evaluate(make_context(symbol="XAUUSD"), [handle], trader_state=None)
        assert len(batch.signals) == 1
        assert batch.signals[0].strategy_id == handle.id

    def test_unscoped_handle_is_skipped(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"EURUSD"}))
        batch = engine.evaluate(make_context(symbol="XAUUSD"), [handle], trader_state=None)
        assert batch.signals == ()

    def test_signals_sorted_by_strategy_id(self) -> None:
        engine = SignalEngine()
        engine.configure()
        h3, _ = make_fake_handle(strategy_id="S3")
        h1, _ = make_fake_handle(strategy_id="S1")
        h2, _ = make_fake_handle(strategy_id="S2")
        batch = engine.evaluate(make_context(), [h3, h1, h2], trader_state=None)
        assert [s.strategy_id for s in batch.signals] == ["S1", "S2", "S3"]

    def test_counts_by_state_reflects_signals(self) -> None:
        engine = SignalEngine()
        engine.configure()
        h1, api1 = make_fake_handle(strategy_id="S1")
        api1.detect_response = {"setup_forming": False}
        h2, api2 = make_fake_handle(strategy_id="S2")
        api2.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.9, "required_confirmations_met": True,
        }
        batch = engine.evaluate(make_context(), [h1, h2], trader_state=None)
        assert batch.counts_by_state.get("NO_SIGNAL") == 1
        assert batch.counts_by_state.get("BUY") == 1

    def test_missing_as_of_produces_one_invalid_signal_per_scoped_handle(self) -> None:
        """API §1 'failures': a mismatched/stale context (missing as_of) produces a batch with ALL
        signals INVALID -- never a crash, and never a silently-empty/dropped batch either."""
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context()
        del context["meta"]["as_of"]
        batch = engine.evaluate(context, [handle], trader_state=None)
        assert len(batch.signals) == 1
        assert batch.signals[0].state is SignalState.INVALID
        assert QualityFlag.MISSING_TIMESTAMP in batch.signals[0].quality_flags
        assert engine.health().overall is EngineOverallHealth.DEGRADED

    def test_missing_as_of_unscoped_handle_produces_no_signal(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"EURUSD"}))
        context = make_context(symbol="XAUUSD")
        del context["meta"]["as_of"]
        batch = engine.evaluate(context, [handle], trader_state=None)
        assert batch.signals == ()

    def test_empty_handle_list_produces_empty_batch(self) -> None:
        engine = SignalEngine()
        engine.configure()
        batch = engine.evaluate(make_context(), [], trader_state=None)
        assert batch.signals == ()
        assert batch.counts_by_state == {}


class TestIsolation:
    def test_one_strategy_raising_does_not_affect_another(self) -> None:
        engine = SignalEngine()
        engine.configure()
        h_bad, api_bad = make_fake_handle(strategy_id="S66")
        api_bad.health_fn = lambda ctx, ts: (_ for _ in ()).throw(RuntimeError("boom"))
        h_good, api_good = make_fake_handle(strategy_id="S77")
        api_good.detect_response = {"setup_forming": False}
        batch = engine.evaluate(make_context(), [h_bad, h_good], trader_state=None)
        by_id = {s.strategy_id: s for s in batch.signals}
        assert by_id["S66"].state is SignalState.INVALID
        assert QualityFlag.CORRUPTED_OUTPUT in by_id["S66"].quality_flags
        assert by_id["S77"].state is SignalState.NO_SIGNAL

    def test_malformed_response_is_classified_invalid_not_raised(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, api = make_fake_handle()
        api.health_response = {}  # missing required 'state' key -> MalformedStrategyResponseError
        batch = engine.evaluate(make_context(), [handle], trader_state=None)
        assert batch.signals[0].state is SignalState.INVALID
        assert QualityFlag.CORRUPTED_OUTPUT in batch.signals[0].quality_flags

    def test_broken_contract_property_does_not_crash_the_whole_batch(self) -> None:
        """Regression guard: ``_collect()`` used to read ``handle.contract`` BEFORE its try/except --
        a handle whose ``contract`` property raises would crash evaluate()'s entire batch-building
        tuple(), taking every OTHER strategy in the batch down with it. Now it must be isolated to
        just this one strategy's CORRUPTED_OUTPUT signal."""

        class _BrokenContractHandle:
            id = "S88"
            api = make_fake_handle(strategy_id="S88")[1]

            @property
            def contract(self) -> object:
                raise RuntimeError("contract store unavailable")

        engine = SignalEngine()
        engine.configure()
        h_broken = _BrokenContractHandle()
        h_good, _ = make_fake_handle(strategy_id="S99")
        batch = engine.evaluate(make_context(), [h_broken, h_good], trader_state=None)  # type: ignore[list-item]
        by_id = {s.strategy_id: s for s in batch.signals}
        assert by_id["S88"].state is SignalState.INVALID
        assert QualityFlag.CORRUPTED_OUTPUT in by_id["S88"].quality_flags
        assert by_id["S99"].state is SignalState.BUY


class TestDeduplication:
    def test_duplicate_strategy_id_in_the_same_cycle_is_deduped_keeping_one(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle_a, _ = make_fake_handle(strategy_id="S5")
        handle_b, _ = make_fake_handle(strategy_id="S5")  # a second handle, same id -> duplicate
        batch = engine.evaluate(make_context(), [handle_a, handle_b], trader_state=None)
        matching = [s for s in batch.signals if s.strategy_id == "S5"]
        assert len(matching) == 1

    def test_duplicate_drop_is_recorded_in_degraded_reasons(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle_a, _ = make_fake_handle(strategy_id="S5")
        handle_b, _ = make_fake_handle(strategy_id="S5")
        engine.evaluate(make_context(), [handle_a, handle_b], trader_state=None)
        reasons = engine.health().degraded_reasons
        assert any("duplicate" in r.lower() for r in reasons)

    def test_no_duplicates_produces_no_degraded_reason(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(strategy_id="S5")
        engine.evaluate(make_context(), [handle], trader_state=None)
        assert engine.health().degraded_reasons == ()


class TestTimeout:
    def test_slow_strategy_times_out_and_is_classified_invalid(self) -> None:
        engine = SignalEngine(EngineConfig(eval_timeout_s=0.05))
        engine.configure()
        handle, api = make_fake_handle()
        api.health_fn = _slow_health
        signal = engine.evaluate_strategy(make_context(), handle, trader_state=None)
        assert signal.state is SignalState.INVALID
        assert QualityFlag.EVAL_TIMEOUT in signal.quality_flags
        assert engine.statistics().timeouts == 1

    def test_timeout_does_not_use_the_strategys_contract(self) -> None:
        engine = SignalEngine(EngineConfig(eval_timeout_s=0.05))
        engine.configure()
        handle, api = make_fake_handle()
        api.health_fn = _slow_health
        signal = engine.evaluate_strategy(make_context(), handle, trader_state=None)
        assert signal.mechanism == "unavailable: strategy output could not be read"

    def test_a_hung_strategy_does_not_wedge_the_next_cycle(self) -> None:
        """Regression guard: with the (default-tunable) ``max_workers=1`` pool, ``Future.result
        (timeout=...)`` cannot actually interrupt a genuinely-hung strategy call -- the worker thread
        stays occupied after the timeout is reported. If the engine reused one executor for its whole
        lifetime, that stuck worker would silently swallow every later cycle's submissions too (they'd
        queue forever behind it). The engine must refresh its worker pool every cycle so a hang from
        one call cannot starve the next -- this call must return promptly, not wait out the hang."""
        engine = SignalEngine(EngineConfig(eval_timeout_s=0.05, max_workers=1))
        engine.configure()
        hung_handle, hung_api = make_fake_handle(strategy_id="S1")
        hung_api.health_fn = _slow_health  # sleeps 0.5s -- times out at 0.05s, keeps running after
        timed_out = engine.evaluate_strategy(make_context(), hung_handle, trader_state=None)
        assert timed_out.state is SignalState.INVALID

        healthy_handle, _ = make_fake_handle(strategy_id="S2")
        start = time.perf_counter()
        signal = engine.evaluate_strategy(make_context(), healthy_handle, trader_state=None)
        elapsed = time.perf_counter() - start
        assert signal.state is not SignalState.INVALID or QualityFlag.EVAL_TIMEOUT not in signal.quality_flags
        assert elapsed < 0.3  # nowhere near the hung call's 0.5s sleep -- proves it wasn't queued behind it


class TestEvaluateAll:
    def test_evaluates_every_symbol_in_sorted_order(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"XAUUSD", "EURUSD"}))
        batches = engine.evaluate_all(
            {"EURUSD": make_context(symbol="EURUSD"), "XAUUSD": make_context(symbol="XAUUSD")},
            [handle], trader_state=None,
        )
        assert [b.symbol for b in batches] == ["EURUSD", "XAUUSD"]

    def test_symbols_are_fully_isolated(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"XAUUSD"}))
        batches = engine.evaluate_all(
            {"EURUSD": make_context(symbol="EURUSD"), "XAUUSD": make_context(symbol="XAUUSD")},
            [handle], trader_state=None,
        )
        by_symbol = {b.symbol: b for b in batches}
        assert by_symbol["XAUUSD"].signals != ()
        assert by_symbol["EURUSD"].signals == ()


class TestEvaluateStrategy:
    def test_returns_a_single_strategy_signal(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        signal = engine.evaluate_strategy(make_context(), handle, trader_state=None)
        assert signal.strategy_id == handle.id

    def test_missing_as_of_returns_a_classified_invalid_signal(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context()
        del context["meta"]["as_of"]
        signal = engine.evaluate_strategy(context, handle, trader_state=None)
        assert signal.state is SignalState.INVALID
        assert QualityFlag.MISSING_TIMESTAMP in signal.quality_flags


class TestRetrieval:
    def test_get_signal_returns_the_matching_signal(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context(as_of=777)
        engine.evaluate(context, [handle], trader_state=None)
        result = engine.get_signal(handle.id, "XAUUSD", 777)
        assert not isinstance(result, NotFound)
        assert result.strategy_id == handle.id

    def test_get_signal_not_found_for_unknown_as_of(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(as_of=1), [handle], trader_state=None)
        assert isinstance(engine.get_signal(handle.id, "XAUUSD", 999), NotFound)

    def test_get_signal_not_found_for_unknown_strategy_id_in_an_existing_batch(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(strategy_id="S1")
        engine.evaluate(make_context(as_of=1), [handle], trader_state=None)
        assert isinstance(engine.get_signal("S2", "XAUUSD", 1), NotFound)

    def test_get_signal_not_found_for_unknown_symbol(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(symbol="XAUUSD", as_of=1), [handle], trader_state=None)
        assert isinstance(engine.get_signal(handle.id, "EURUSD", 1), NotFound)

    def test_get_signals_filters_by_state(self) -> None:
        engine = SignalEngine()
        engine.configure()
        h1, api1 = make_fake_handle(strategy_id="S1")
        api1.detect_response = {"setup_forming": False}
        h2, api2 = make_fake_handle(strategy_id="S2")
        api2.generate_signal_response = {
            "present": True, "direction": "LONG", "strength": 0.9, "required_confirmations_met": True,
        }
        engine.evaluate(make_context(), [h1, h2], trader_state=None)
        buys = engine.get_signals(state=SignalState.BUY)
        assert [s.strategy_id for s in buys] == ["S2"]

    def test_get_signals_filters_by_strategy_id(self) -> None:
        engine = SignalEngine()
        engine.configure()
        h1, _ = make_fake_handle(strategy_id="S1")
        h2, _ = make_fake_handle(strategy_id="S2")
        engine.evaluate(make_context(), [h1, h2], trader_state=None)
        assert [s.strategy_id for s in engine.get_signals(strategy_id="S1")] == ["S1"]

    def test_get_signals_filters_by_as_of(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(as_of=1), [handle], trader_state=None)
        assert len(engine.get_signals(as_of=1)) == 1
        assert engine.get_signals(as_of=999) == []

    def test_get_signals_filters_by_symbol(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle(symbols=frozenset({"XAUUSD"}))
        engine.evaluate(make_context(symbol="XAUUSD"), [handle], trader_state=None)
        assert len(engine.get_signals(symbol="XAUUSD")) == 1
        assert engine.get_signals(symbol="EURUSD") == []


class TestPublicValidateSignal:
    def test_delegates_to_the_validator_module(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context(as_of=1)
        engine.evaluate(context, [handle], trader_state=None)
        signal = engine.get_signals(as_of=1)[0]
        result = engine.validate_signal(signal)
        assert result.valid is True


class TestScopingFailsSafe:
    def test_handle_whose_required_context_raises_is_still_evaluated_and_classified(self) -> None:
        """``_is_scoped_to_symbol``'s except branch fails OPEN (treats a broken ``required_context()``
        as scoped) rather than silently dropping the handle -- the full pipeline call's own
        timeout+exception boundary then correctly classifies it as INVALID/CORRUPTED_OUTPUT, so the
        strategy still produces a visible, disclosed signal instead of vanishing without a trace."""
        engine = SignalEngine()
        engine.configure()
        handle, api = make_fake_handle()
        api.required_context_fn = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        batch = engine.evaluate(make_context(), [handle], trader_state=None)
        assert len(batch.signals) == 1
        assert batch.signals[0].state is SignalState.INVALID
        assert QualityFlag.CORRUPTED_OUTPUT in batch.signals[0].quality_flags


class TestReassemblyOnValidationFailure:
    def test_a_signal_that_fails_post_assembly_validation_is_reassembled_invalid(self) -> None:
        """A context with an empty (but present) context_schema_version passes pipeline evaluation
        cleanly but produces a signal that fails SIGNAL_SCHEMA.json's version pattern -- the engine
        must catch this at the Output Collector stage and reassemble a classified INVALID signal
        rather than emit a schema-violating one."""
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context()
        context["meta"]["context_schema_version"] = ""
        signal = engine.evaluate_strategy(context, handle, trader_state=None)
        assert signal.state is SignalState.INVALID
        assert QualityFlag.SCHEMA_MISMATCH in signal.quality_flags


class TestExplain:
    def test_explain_returns_the_signals_explanation(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context(as_of=1)
        engine.evaluate(context, [handle], trader_state=None)
        explanation = engine.explain(handle.id, "XAUUSD", 1)
        assert not isinstance(explanation, NotFound)

    def test_explain_not_found_when_signal_absent(self) -> None:
        engine = SignalEngine()
        engine.configure()
        assert isinstance(engine.explain("SNONE", "XAUUSD", 1), NotFound)


class TestDeterminism:
    """``evaluation_time_ms`` is explicitly wall-clock (engine.py's own module docstring: "only
    evaluation_time_ms uses real wall-clock... purely an informational metric") and is excluded from
    these equality checks -- every other field must match bit-for-bit."""

    def test_evaluate_strategy_is_deterministic_across_calls(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        context = make_context(as_of=100)
        first = engine.evaluate_strategy(context, handle, trader_state=None)
        second = engine.evaluate_strategy(context, handle, trader_state=None)
        assert replace(first, evaluation_time_ms=0.0) == replace(second, evaluation_time_ms=0.0)

    def test_fresh_engine_same_config_reproduces_the_same_signal(self) -> None:
        handle, _ = make_fake_handle()
        context = make_context(as_of=100)
        e1 = SignalEngine()
        e1.configure()
        s1 = e1.evaluate_strategy(context, handle, trader_state=None)
        e2 = SignalEngine()
        e2.configure()
        s2 = e2.evaluate_strategy(context, handle, trader_state=None)
        assert replace(s1, evaluation_time_ms=0.0) == replace(s2, evaluation_time_ms=0.0)


class TestStatisticsHealthVersions:
    def test_statistics_track_cycles_and_signal_counts(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(), [handle], trader_state=None)
        stats = engine.statistics()
        assert stats.cycles == 1
        assert stats.signals_total == 1

    def test_health_ok_after_a_clean_cycle(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(), [handle], trader_state=None)
        assert engine.health().overall is EngineOverallHealth.OK

    def test_versions_reflect_config(self) -> None:
        engine = SignalEngine(EngineConfig(signal_engine_version="3.1.4"))
        engine.configure()
        info = engine.versions()
        assert info.signal_engine_version == "3.1.4"
        assert info.supported_interface_major == 1


class TestShutdown:
    def test_shutdown_reports_true_last_known_health_not_failed(self) -> None:
        """Regression guard for the shutdown-health-ordering bug: shutdown() must capture health
        BEFORE flipping _configured, so a healthy engine's shutdown result is not synthetically
        reported as FAILED."""
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(), [handle], trader_state=None)
        health = engine.shutdown()
        assert health.overall is EngineOverallHealth.OK

    def test_after_shutdown_engine_requires_reconfigure(self) -> None:
        engine = SignalEngine()
        engine.configure()
        engine.shutdown()
        with pytest.raises(EngineNotConfiguredError):
            engine.evaluate(make_context(), [], trader_state=None)

    def test_shutdown_after_configure_with_no_activity_reports_ok(self) -> None:
        engine = SignalEngine()
        engine.configure()
        assert engine.shutdown().overall is EngineOverallHealth.OK

    def test_reconfigure_after_shutdown_resets_statistics(self) -> None:
        engine = SignalEngine()
        engine.configure()
        handle, _ = make_fake_handle()
        engine.evaluate(make_context(), [handle], trader_state=None)
        engine.shutdown()
        engine.configure()
        assert engine.statistics().cycles == 0
