"""`N1ReplayEngine` -- the versioned replay interface around the REAL, running N1/Router pipeline
(RT-N1-REPLAY-0001). Wraps exactly three real sources, reimplements none of them:

- `ai_trader.new_brain_bridge.raw_axes_builder.RawAxesBuilder` (the real, stateful, vendored-detector
  N1 producer -- `.observe(bar) -> ve_brain.RawAxes`)
- `ve_brain.applicable_regimes` (the real pure function from `RawAxes` to a regime set)
- `ve_brain.StrategyRouter` (the real router/eligibility engine)

The N1-input-fingerprint / N1-output-fingerprint / Router-input-fingerprint formulas mirror
`ai_trader.new_brain_bridge.bridge.evaluate_bar`'s own real recipe EXACTLY (same field order, same
`_fp` hash scheme) so a replayed `N1ReplayResult.n1_output_fingerprint` is byte-for-byte comparable
against a live-produced `NodeTrace.output` for the same bar -- this is what the mandatory "live vs
replay identical" tests verify.

State machine: `initialize` (`__init__`) -> `observe_closed_bar` (repeatable) -> `snapshot`/`restore`
(repeatable, at any point) -> `replay` (a convenience batch wrapper over `observe_closed_bar`) ->
`reset` (returns to zero bars observed, same identity). Every state transition either succeeds
producing a result, or raises one of `ai_trader.n1_replay.errors`' fail-closed exceptions and leaves
state exactly as it was before the call."""

from __future__ import annotations

import math
import time
from typing import Callable, Sequence

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.n1_replay.errors import (
    BarNotClosedError,
    DuplicateBarError,
    FutureBarError,
    IncompatibleSnapshotError,
    NonFiniteAxesInputError,
    OutOfOrderBarError,
    StaleStateError,
)
from ai_trader.n1_replay.identity import ROUTER_VERSION, EvaluationIdentity, _fp, build_evaluation_identity
from ai_trader.n1_replay.types import N1ReplayResult, N1ReplaySnapshot
from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder


def _finite_bar_values(bar: Bar) -> tuple[float, ...]:
    values = [bar.open, bar.high, bar.low, bar.close]
    if bar.volume is not None:
        values.append(bar.volume)
    return tuple(values)


class N1ReplayEngine:
    def __init__(
        self, *, symbol: str, timeframe: str, bar_interval_seconds: int, implementation_commit: str,
        catalog: tuple[ve_brain.StrategyContract, ...] = ve_brain.CANONICAL_STRATEGIES,
        router_bias_direction: str | None = None, confidence: float = 1.0,
        clock: Callable[[], float] = time.time, max_staleness_seconds: float | None = None,
    ) -> None:
        self._symbol = symbol
        self._timeframe = timeframe
        self._bar_interval_seconds = bar_interval_seconds
        self._catalog = catalog
        self._router_bias_direction = router_bias_direction
        self._confidence = confidence
        self._clock = clock
        self._max_staleness_seconds = max_staleness_seconds
        self._identity = build_evaluation_identity(
            implementation_commit=implementation_commit, symbol=symbol, timeframe=timeframe,
            bar_interval_seconds=bar_interval_seconds,
        )
        self._axes_builder = RawAxesBuilder(symbol)
        self._observed_bars: list[Bar] = []
        self._last_result: N1ReplayResult | None = None

    @property
    def identity(self) -> EvaluationIdentity:
        return self._identity

    @property
    def last_closed_bar(self) -> Bar | None:
        return self._observed_bars[-1] if self._observed_bars else None

    @property
    def bars_observed(self) -> int:
        return len(self._observed_bars)

    def _build_result(self, bar: Bar, axes: ve_brain.RawAxes) -> N1ReplayResult:
        """Pure given `(bar, axes, self._catalog, self._router_bias_direction, self._confidence)` --
        used by both `observe_closed_bar` (live accumulation path) and `restore` (snapshot replay
        path), which is exactly what makes "restart + restore produces an identical result" true by
        construction rather than by a separate proof."""
        market_event_id = f"{bar.symbol}:{self._timeframe}:{bar.ts_close}"
        n1_output_fp = _fp(
            str(axes.is_compressed), str(axes.is_displacement), str(axes.direction), str(axes.structure),
        )
        regime_axes_status = tuple(
            "available" if value is not None else "unavailable"
            for value in (axes.is_compressed, axes.is_displacement, axes.direction, axes.structure)
        )
        applicable = frozenset(regime.value for regime in ve_brain.applicable_regimes(axes))

        router = ve_brain.StrategyRouter(self._catalog)
        eligibility_decisions = router.eligible(
            axes, market_event_id, self._router_bias_direction, self._confidence,
        )
        router_output_components = tuple(
            _fp(str(d.eligible), str(d.mode.value), ",".join(d.matched_regimes))
            for d in eligibility_decisions
        )
        router_output_fp = _fp(*router_output_components)
        reason_codes = tuple(sorted({code for d in eligibility_decisions for code in d.reason_codes}))

        available_count = sum(1 for status in regime_axes_status if status == "available")
        if available_count == len(regime_axes_status):
            availability_status = "FULL"
        elif available_count > 0:
            availability_status = "PARTIAL"
        else:
            availability_status = "UNAVAILABLE"

        return N1ReplayResult(
            raw_axes=axes, applicable_regimes=applicable, eligibility_decisions=eligibility_decisions,
            n1_contract_version=axes.n1_contract_version, router_version=ROUTER_VERSION,
            detector_configuration_fingerprint=self._identity.detector_configuration_fingerprint,
            input_data_identity=market_event_id, output_fingerprint=_fp(n1_output_fp, router_output_fp),
            last_closed_bar=bar, reason_codes=reason_codes, regime_axes_status=regime_axes_status,
            availability_status=availability_status, n1_output_fingerprint=n1_output_fp,
            router_output_fingerprint=router_output_fp, evaluation_identity=self._identity,
        )

    def observe_closed_bar(self, bar: Bar, *, as_of: int | None = None) -> N1ReplayResult:
        if bar.symbol != self._symbol:
            raise ValueError(f"N1ReplayEngine for {self._symbol!r} received a bar for {bar.symbol!r}")
        if not all(math.isfinite(value) for value in _finite_bar_values(bar)):
            raise NonFiniteAxesInputError(
                f"bar at ts_open={bar.ts_open} carries a NaN/Infinite OHLCV value: {_finite_bar_values(bar)!r}"
            )
        if as_of is not None and bar.ts_close > as_of:
            raise FutureBarError(
                f"bar ts_close={bar.ts_close} is beyond the requested replay horizon as_of={as_of}"
            )
        now = self._clock()
        if bar.ts_close > now:
            raise BarNotClosedError(f"bar ts_close={bar.ts_close} has not yet passed clock()={now}")

        last = self._observed_bars[-1] if self._observed_bars else None
        if last is not None:
            if bar.ts_open == last.ts_open:
                if bar == last:
                    assert self._last_result is not None  # invariant: a bar was observed, a result exists
                    return self._last_result
                raise DuplicateBarError(
                    f"bar at ts_open={bar.ts_open} conflicts with an already-observed bar for the same slot"
                )
            if bar.ts_open < last.ts_open:
                raise OutOfOrderBarError(
                    f"bar ts_open={bar.ts_open} is before the last-observed ts_open={last.ts_open}"
                )

        axes = self._axes_builder.observe(bar)
        result = self._build_result(bar, axes)
        self._observed_bars.append(bar)
        self._last_result = result
        return result

    def replay(self, bars: Sequence[Bar], *, as_of: int | None = None) -> tuple[N1ReplayResult, ...]:
        return tuple(self.observe_closed_bar(bar, as_of=as_of) for bar in bars)

    def snapshot(self) -> N1ReplaySnapshot:
        return N1ReplaySnapshot(
            identity=self._identity, observed_bars=tuple(self._observed_bars),
            snapshot_taken_at_bars_observed=len(self._observed_bars),
        )

    def restore(self, snapshot: N1ReplaySnapshot) -> None:
        if not self._identity.matches(snapshot.identity):
            raise IncompatibleSnapshotError(
                f"snapshot identity {snapshot.identity.fingerprint()!r} != "
                f"this engine's identity {self._identity.fingerprint()!r}"
            )
        new_builder = RawAxesBuilder(self._symbol)
        new_observed: list[Bar] = []
        last_result: N1ReplayResult | None = None
        for bar in snapshot.observed_bars:
            axes = new_builder.observe(bar)
            last_result = self._build_result(bar, axes)
            new_observed.append(bar)
        self._axes_builder = new_builder
        self._observed_bars = new_observed
        self._last_result = last_result

    def reset(self) -> None:
        self._axes_builder = RawAxesBuilder(self._symbol)
        self._observed_bars = []
        self._last_result = None

    def assert_not_stale(self, *, now: float | None = None) -> None:
        """Distinct from `observe_closed_bar`'s own checks -- this is an explicit health check a live
        caller invokes between bars (e.g. before trusting `last_closed_bar` for a downstream decision),
        never invoked automatically inside `observe_closed_bar`/`replay` (which must remain safe to use
        for pure historical replay of old fixtures, where "stale" has no meaning)."""
        if self._max_staleness_seconds is None or not self._observed_bars:
            return
        current = now if now is not None else self._clock()
        elapsed = current - self._observed_bars[-1].ts_close
        if elapsed > self._max_staleness_seconds:
            raise StaleStateError(
                f"{elapsed:.0f}s since last observed bar exceeds max_staleness_seconds="
                f"{self._max_staleness_seconds!r}"
            )
