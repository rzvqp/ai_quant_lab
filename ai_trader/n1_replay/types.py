"""N1 replay result/snapshot contract (RT-N1-REPLAY-0001 section 1). `N1_REPLAY_SCHEMA_VERSION`
(`identity.py`) versions this shape -- bump it whenever a field here is added, removed, or its
meaning changes, since a schema change must change `EvaluationIdentity.fingerprint()`."""

from __future__ import annotations

import dataclasses

import ve_brain  # type: ignore[import-untyped]

from ai_trader.live_signal_source.types import Bar
from ai_trader.n1_replay.identity import EvaluationIdentity


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1ReplayResult:
    """One bar's complete N1 + Router reading -- everything downstream of `RawAxesBuilder.observe()`
    and `ve_brain.StrategyRouter.eligible()`, nothing invented. Every field here is either the real
    object those two real calls returned, or a fingerprint/status derived from it."""

    raw_axes: ve_brain.RawAxes
    applicable_regimes: frozenset[str]
    eligibility_decisions: tuple[object, ...]  # tuple[ve_brain.EligibilityDecision, ...] -- the "router verdict"
    n1_contract_version: str
    router_version: str
    detector_configuration_fingerprint: str
    input_data_identity: str
    output_fingerprint: str
    last_closed_bar: Bar
    reason_codes: tuple[str, ...]
    regime_axes_status: tuple[str, ...]
    availability_status: str
    n1_output_fingerprint: str
    router_output_fingerprint: str
    evaluation_identity: EvaluationIdentity


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class N1ReplaySnapshot:
    """A point-in-time, restorable capture of one `N1ReplayEngine`'s full state. Carries the ORDERED
    bar history rather than `RawAxesBuilder`'s internal accumulator arrays directly, because
    `RawAxesBuilder` exposes no restore primitive of its own -- `restore()` rebuilds a fresh builder
    and deterministically replays every bar through it, which is also exactly what guarantees
    "replay after snapshot/restore produces identical results to continuous running" (it IS the same
    computation, run again from the same inputs)."""

    identity: EvaluationIdentity
    observed_bars: tuple[Bar, ...]
    snapshot_taken_at_bars_observed: int

    def __post_init__(self) -> None:
        if len(self.observed_bars) != self.snapshot_taken_at_bars_observed:
            raise ValueError(
                "N1ReplaySnapshot: observed_bars length "
                f"{len(self.observed_bars)} != snapshot_taken_at_bars_observed "
                f"{self.snapshot_taken_at_bars_observed}"
            )
