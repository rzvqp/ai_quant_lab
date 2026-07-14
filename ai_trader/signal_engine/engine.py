"""``SignalEngine`` — the public façade implementing ``SIGNAL_ENGINE_API.md`` exactly.

Wires together the per-strategy evaluation pipeline (:mod:`ai_trader.signal_engine.pipeline`), the
Signal Assembler (:mod:`ai_trader.signal_engine.assembler`), and the Output Collector's validation
(:mod:`ai_trader.signal_engine.validator`) into the documented, deterministic, fail-safe evaluation
cycle. A pure evaluation engine: no trading decision, no scoring, no risk, no execution, no learning,
no research access (``SIGNAL_ENGINE_ARCHITECTURE.md`` §1).

**Determinism note on ``timestamp``/``generated_at``**: both are set to the evaluated context's own
``as_of`` (never wall-clock) — this is what makes "identical ``(context, handle, trader_state)`` ⇒
identical signal" (architecture §5, API §5 #2) actually hold bit-for-bit across replays. In LIVE mode
``as_of`` already IS the real current bar-close instant, so this is correct for both LIVE and REPLAY,
not merely a REPLAY-only concession. Only ``evaluation_time_ms`` uses real wall-clock
(``time.perf_counter()``), and it is purely an informational metric that never feeds back into any
STATE decision (architecture §5: "only ``evaluation_time_ms`` is measured, not used in logic").
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from ai_trader.signal_engine import assembler, pipeline, validator
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.exceptions import EngineNotConfiguredError
from ai_trader.signal_engine.pipeline import PipelineOutcome, StrategyHandleLike
from ai_trader.strategy_manager.contract import Contract
from ai_trader.signal_engine.types import (
    ConditionRecord,
    EngineHealth,
    EngineOverallHealth,
    MarketContext,
    NotFound,
    QualityFlag,
    SignalBatch,
    SignalState,
    Statistics,
    StrategySignal,
    ValidationResult,
    VersionInfo,
)


def _is_scoped_to_symbol(handle: StrategyHandleLike, symbol: str) -> bool:
    """Whether ``handle`` declares itself relevant to ``symbol``. The Strategy Manager's own
    ``ManagerConfig.symbols`` universe is applied uniformly to every strategy's
    ``required_context()`` (see its own docstring: the contract schema has no per-strategy symbol
    field at all), so scoping here checks whether ``symbol`` is IN that handle's declared symbol
    set -- an empty/absent set is treated as "not scoped to anything" (fail-safe: never silently
    evaluate a handle against a symbol it never declared).
    """
    try:
        required = handle.api.required_context()
    except Exception:  # noqa: BLE001 -- a broken required_context() gives no real information about
        # this handle's true scope. Fail OPEN (treat it as scoped) rather than silently dropping it
        # from the batch: returning False here would make the strategy vanish with zero trace (no
        # signal, no quality flag, nothing in statistics) for a symbol it may genuinely be scoped to
        # -- violating "one signal per (strategy, symbol), always" (API §5 #1). Treating it as scoped
        # instead routes it into the full pipeline call, whose own timeout+exception boundary
        # correctly classifies it as INVALID/CORRUPTED_OUTPUT -- a visible, disclosed failure.
        return True
    return symbol in required.symbols


class SignalEngine:
    """The Signal Engine. See ``SIGNAL_ENGINE_API.md`` for the full contract."""

    def __init__(self, config: EngineConfig | None = None) -> None:
        self._config = config or EngineConfig()
        self._configured = False
        self._executor: ThreadPoolExecutor | None = None
        self._cycles = 0
        self._signals_total = 0
        self._by_state: dict[str, int] = {s.value: 0 for s in SignalState}
        self._timeouts = 0
        self._invalids = 0
        self._eval_times_ms: list[float] = []
        self._last_cycle_ok = True
        self._degraded_reasons: list[str] = []
        self._last_batches_by_symbol: dict[str, SignalBatch] = {}

    # ------------------------------------------------------------------ 0. configuration

    def configure(self) -> None:
        """Idempotent full reset (mirrors the Market Scanner/Strategy Manager ``configure()``
        convention). Starts the worker pool used for per-strategy timeout enforcement (architecture
        §12: "READY — awaits (MarketContext, active handles) per cycle")."""
        if self._executor is not None:
            self._executor.shutdown(wait=False, cancel_futures=True)
        self._executor = ThreadPoolExecutor(max_workers=self._config.max_workers)
        self._configured = True
        self._cycles = 0
        self._signals_total = 0
        self._by_state = {s.value: 0 for s in SignalState}
        self._timeouts = 0
        self._invalids = 0
        self._eval_times_ms = []
        self._last_cycle_ok = True
        self._degraded_reasons = []
        self._last_batches_by_symbol = {}

    def _require_configured(self) -> None:
        if not self._configured or self._executor is None:
            raise EngineNotConfiguredError("SignalEngine.configure() must be called first")

    def _refresh_executor(self) -> None:
        """Replace the worker pool with a fresh one before every cycle that actually submits work.
        ``Future.result(timeout=...)`` can only stop *waiting* on a hung strategy call -- Python
        cannot forcibly interrupt a running thread -- so a strategy that truly hangs (not merely
        times out) permanently occupies a worker slot. Reusing one executor across the engine's
        entire lifetime would let a single hang from cycle N silently starve every later cycle
        sharing that pool (and eventually deadlock ``shutdown()``'s ``wait=True``). Discarding the
        old executor non-blockingly (never waiting on whatever may still be stuck inside it) and
        starting fresh each cycle bounds a hang's blast radius to the single cycle it occurred in --
        the best a pure-thread-based design can do without process-level isolation (out of scope).
        """
        assert self._executor is not None
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._executor = ThreadPoolExecutor(max_workers=self._config.max_workers)

    def _missing_as_of_signal(self, handle: StrategyHandleLike, context: MarketContext) -> StrategySignal:
        """The classified, schema-valid fallback for a context missing ``meta.as_of`` (API §1
        'failures': "the batch is produced with all signals INVALID/NEED_CONTEXT ... never a
        crash"). ``contract=None`` -- the same safest-fallback rule as the CORRUPTED_OUTPUT/
        EVAL_TIMEOUT paths -- a context this malformed cannot be trusted to safely drive
        contract-dependent fields either."""
        outcome = PipelineOutcome(
            state=SignalState.INVALID, why_failed=(ConditionRecord(code="MISSING_AS_OF", satisfied=False),),
        )
        return assembler.assemble_signal(
            strategy_id=handle.id, contract=None, outcome=outcome, context=context,
            evaluation_time_ms=0.0, config=self._config, now_ts=0,
            extra_quality_flags=(QualityFlag.MISSING_TIMESTAMP,),
        )

    @staticmethod
    def _counts_by_state(signals: tuple[StrategySignal, ...]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for sig in signals:
            counts[sig.state.value] = counts.get(sig.state.value, 0) + 1
        return counts

    def _dedupe(self, signals: tuple[StrategySignal, ...]) -> tuple[StrategySignal, ...]:
        """Output Collector dedup (architecture §7 / SEQUENCE.md §2: "dedupe (strategy_id|symbol|
        as_of) ... keep one, drop extra with [DUPLICATE_SIGNAL]"). Duplicates only arise from a
        caller passing more than one handle for the same strategy id -- not a normal cycle outcome
        -- but the "one signal per (strategy_id, symbol, as_of)" invariant (API §5 #1) must hold
        regardless. The first occurrence is kept (``signals`` is already in the fixed, stable-sorted
        handle order, so "first" is deterministic); every extra is dropped and recorded in
        ``degraded_reasons`` for observability rather than silently vanishing.
        """
        seen: set[tuple[str, str, int]] = set()
        kept: list[StrategySignal] = []
        for sig in signals:
            key = (sig.strategy_id, sig.symbol, sig.as_of)
            if key in seen:
                self._degraded_reasons.append(
                    f"duplicate signal dropped [DUPLICATE_SIGNAL]: {sig.strategy_id}|{sig.symbol}|{sig.as_of}",
                )
                continue
            seen.add(key)
            kept.append(sig)
        return tuple(kept)

    # ------------------------------------------------------------------ 1. evaluation

    def evaluate(
        self, context: MarketContext, handles: Sequence[StrategyHandleLike], trader_state: object,
    ) -> SignalBatch:
        """Evaluate every handle scoped to ``context``'s symbol, in deterministic order, each in
        isolation (``SIGNAL_ENGINE_API.md`` §1)."""
        self._require_configured()
        meta = context.get("meta", {})
        as_of = meta.get("as_of")
        symbol = meta.get("symbol", "")

        scoped = [h for h in handles if _is_scoped_to_symbol(h, symbol)]
        scoped_sorted = sorted(scoped, key=lambda h: h.id)  # fixed order (architecture §5)

        if as_of is None:
            # a mismatched/stale context: every scoped strategy still gets one classified signal
            # (API §1 'failures') -- never an empty, silently-dropped batch.
            self._last_cycle_ok = False
            self._degraded_reasons.append("context missing meta.as_of")
            signals = tuple(self._missing_as_of_signal(h, context) for h in scoped_sorted)
            batch = SignalBatch(
                as_of=0, symbol=symbol, signals=signals, counts_by_state=self._counts_by_state(signals),
                generated_at=0,
            )
            self._record_cycle(batch)
            return batch

        self._refresh_executor()
        pending: list[tuple[StrategyHandleLike, Future[PipelineOutcome]]] = [
            (h, self._submit(context, h, trader_state)) for h in scoped_sorted
        ]
        signals = self._dedupe(tuple(self._collect(h, fut, context, as_of) for h, fut in pending))

        batch = SignalBatch(
            as_of=as_of, symbol=symbol, signals=signals, counts_by_state=self._counts_by_state(signals),
            generated_at=as_of,
        )
        self._last_cycle_ok = True
        self._record_cycle(batch)
        return batch

    def evaluate_all(
        self, context_batch: dict[str, MarketContext], handles: Sequence[StrategyHandleLike], trader_state: object,
    ) -> tuple[SignalBatch, ...]:
        """Evaluate across every symbol in a ``MarketContextBatch`` (``{symbol: MarketContext}``),
        symbols fully isolated (``SIGNAL_ENGINE_API.md`` §1)."""
        self._require_configured()
        return tuple(
            self.evaluate(context_batch[symbol], handles, trader_state)
            for symbol in sorted(context_batch)
        )

    def evaluate_strategy(
        self, context: MarketContext, handle: StrategyHandleLike, trader_state: object,
    ) -> StrategySignal:
        """Evaluate a single strategy against a single-symbol context — the atomic unit
        (``SIGNAL_ENGINE_API.md`` §1). Used for targeted re-evaluation, testing, or explanation."""
        self._require_configured()
        as_of = context.get("meta", {}).get("as_of")
        if as_of is None:
            return self._missing_as_of_signal(handle, context)
        self._refresh_executor()
        future = self._submit(context, handle, trader_state)
        return self._collect(handle, future, context, as_of)

    def _submit(
        self, context: MarketContext, handle: StrategyHandleLike, trader_state: object,
    ) -> Future[PipelineOutcome]:
        assert self._executor is not None
        return self._executor.submit(pipeline.run_pipeline, context, handle, trader_state)

    def _collect(
        self, handle: StrategyHandleLike, future: Future[PipelineOutcome], context: MarketContext, as_of: int,
    ) -> StrategySignal:
        start = time.perf_counter()
        extra_flags: tuple[QualityFlag, ...] = ()
        contract: Contract | None = None
        try:
            # Read INSIDE the try: a StrategyHandleLike.contract implementation is not guaranteed
            # cheap/safe (it's a Protocol property, not a plain attribute) -- if reading it raises,
            # that must be classified as this ONE strategy's CORRUPTED_OUTPUT, not propagate out of
            # _collect and crash evaluate()'s whole batch-building tuple() for every other strategy.
            contract = handle.contract
            outcome = future.result(timeout=self._config.eval_timeout_s)
        except FutureTimeoutError:
            self._timeouts += 1
            outcome = PipelineOutcome(
                state=SignalState.INVALID,
                why_failed=(ConditionRecord(code="EVAL_TIMEOUT", satisfied=False),),
            )
            extra_flags = (QualityFlag.EVAL_TIMEOUT,)
            contract = None  # the strategy never returned control; do not trust its contract read either
        except Exception:  # noqa: BLE001 -- any strategy-side failure becomes classified CORRUPTED_OUTPUT
            outcome = PipelineOutcome(
                state=SignalState.INVALID,
                why_failed=(ConditionRecord(code="CORRUPTED_OUTPUT", satisfied=False),),
            )
            extra_flags = (QualityFlag.CORRUPTED_OUTPUT,)
            contract = None
        eval_ms = (time.perf_counter() - start) * 1000.0

        signal = assembler.assemble_signal(
            strategy_id=handle.id, contract=contract, outcome=outcome, context=context,
            evaluation_time_ms=eval_ms, config=self._config, now_ts=as_of, extra_quality_flags=extra_flags,
        )

        result = validator.validate_signal(signal)
        if not result.valid:
            signal = assembler.assemble_signal(
                strategy_id=handle.id, contract=None, outcome=PipelineOutcome(
                    state=SignalState.INVALID,
                    why_failed=tuple(ConditionRecord(code=r, satisfied=False) for r in result.reasons),
                ),
                context=context, evaluation_time_ms=eval_ms, config=self._config, now_ts=as_of,
                extra_quality_flags=result.quality_flags,
            )

        self._eval_times_ms.append(eval_ms)
        if signal.state is SignalState.INVALID:
            self._invalids += 1
        return signal

    # ------------------------------------------------------------------ 2. retrieval

    def get_signal(self, strategy_id: str, symbol: str, as_of: int) -> StrategySignal | NotFound:
        batch = self._last_batches_by_symbol.get(symbol)
        if batch is None or batch.as_of != as_of:
            return NotFound(f"{strategy_id}|{symbol}|{as_of}")
        for sig in batch.signals:
            if sig.strategy_id == strategy_id:
                return sig
        return NotFound(f"{strategy_id}|{symbol}|{as_of}")

    def get_signals(
        self, as_of: int | None = None, symbol: str | None = None,
        state: SignalState | None = None, strategy_id: str | None = None,
    ) -> list[StrategySignal]:
        pool = list(self._last_batches_by_symbol.values())
        signals: list[StrategySignal] = [s for b in pool for s in b.signals]
        if as_of is not None:
            signals = [s for s in signals if s.as_of == as_of]
        if symbol is not None:
            signals = [s for s in signals if s.symbol == symbol]
        if state is not None:
            signals = [s for s in signals if s.state == state]
        if strategy_id is not None:
            signals = [s for s in signals if s.strategy_id == strategy_id]
        return signals

    # ------------------------------------------------------------------ 3. validation & explanation

    def validate_signal(self, signal: StrategySignal) -> ValidationResult:
        return validator.validate_signal(signal)

    def explain(self, strategy_id: str, symbol: str, as_of: int) -> object:
        sig = self.get_signal(strategy_id, symbol, as_of)
        if isinstance(sig, NotFound):
            return sig
        return sig.explanation

    # ------------------------------------------------------------------ 4. introspection

    def statistics(self) -> Statistics:
        avg_ms = sum(self._eval_times_ms) / len(self._eval_times_ms) if self._eval_times_ms else 0.0
        return Statistics(
            cycles=self._cycles, signals_total=self._signals_total, by_state=dict(self._by_state),
            avg_eval_ms=avg_ms, timeouts=self._timeouts, invalids=self._invalids,
        )

    def health(self) -> EngineHealth:
        if not self._configured:
            overall = EngineOverallHealth.FAILED
        elif self._degraded_reasons:
            overall = EngineOverallHealth.DEGRADED
        else:
            overall = EngineOverallHealth.OK
        return EngineHealth(
            overall=overall, last_cycle_ok=self._last_cycle_ok, degraded_reasons=tuple(self._degraded_reasons),
            supported_versions={
                "interface_major": self._config.supported.interface_major,
                "context_schema_major": self._config.supported.context_schema_major,
            },
        )

    def versions(self) -> VersionInfo:
        return VersionInfo(
            signal_engine_version=self._config.signal_engine_version,
            signal_schema_version=self._config.signal_schema_version,
            explanation_schema_version=self._config.explanation_schema_version,
            supported_interface_major=self._config.supported.interface_major,
            supported_context_schema_major=self._config.supported.context_schema_major,
        )

    # ------------------------------------------------------------------ 5. shutdown

    def shutdown(self) -> EngineHealth:
        """Stop accepting new cycles, drain in-flight work, release state (architecture §12)."""
        self._require_configured()
        assert self._executor is not None
        final_health = self.health()  # captured BEFORE flipping _configured, so shutdown reports
        # the engine's true last-known status, not a synthetic FAILED just because it stopped.
        self._executor.shutdown(wait=True)
        self._executor = None
        self._configured = False
        return final_health

    # ------------------------------------------------------------------ internals

    def _record_cycle(self, batch: SignalBatch) -> None:
        self._cycles += 1
        self._signals_total += len(batch.signals)
        for sig in batch.signals:
            self._by_state[sig.state.value] = self._by_state.get(sig.state.value, 0) + 1
        if batch.symbol:
            self._last_batches_by_symbol[batch.symbol] = batch
