"""N1 canonical replay handoff (RT-N1-REPLAY-0001, CEO directive 2026-08-17).

Wraps the REAL, running N1 producer (`ai_trader.new_brain_bridge.raw_axes_builder.RawAxesBuilder`)
and the REAL `ve_brain.RawAxes`/`ve_brain.StrategyRouter` so a separate consumer (Alpha) can replay
the exact same closed-bar regime classification the live `new_brain_bridge`/`new_brain_live` runtime
produces -- same detectors, same configuration, same fingerprint formulas -- without reimplementing
any part of the algorithm and without importing `ai_trader.new_brain_bridge`/`ai_trader.new_brain_live`
live-process internals or touching LIVE_SHADOW in any way.

Status at delivery: `READY_FOR_N1_REPLAY_PACKAGING`. This package does NOT connect Alpha to any AI
Trader live source, does NOT supply `probability_inputs`, does NOT touch the broker gate, and does NOT
stop or restart LIVE_SHADOW. `N1_HANDOFF_PASS` is not self-declared here -- that verdict belongs to
whichever review process the CEO designates next.
"""

from ai_trader.n1_replay.engine import N1ReplayEngine
from ai_trader.n1_replay.errors import (
    BarNotClosedError,
    DuplicateBarError,
    FutureBarError,
    IncompatibleSnapshotError,
    N1ReplayError,
    NonFiniteAxesInputError,
    OutOfOrderBarError,
    StaleStateError,
)
from ai_trader.n1_replay.identity import EvaluationIdentity, build_evaluation_identity
from ai_trader.n1_replay.types import N1ReplayResult, N1ReplaySnapshot

__all__ = [
    "N1ReplayEngine",
    "N1ReplayResult",
    "N1ReplaySnapshot",
    "EvaluationIdentity",
    "build_evaluation_identity",
    "N1ReplayError",
    "BarNotClosedError",
    "DuplicateBarError",
    "FutureBarError",
    "IncompatibleSnapshotError",
    "NonFiniteAxesInputError",
    "OutOfOrderBarError",
    "StaleStateError",
]
