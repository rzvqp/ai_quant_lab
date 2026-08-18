"""ve_n1_replay — replay canonic N1 pentru Alpha, INDEPENDENT de ai_trader.

Suprafața publică păstrează contractul livrat: `N1ReplayEngine` (initialize prin constructor · observe_closed_bar ·
replay · snapshot · restore · reset) + tipurile, erorile și identitatea. Wrapează RawAxesBuilder-ul REAL @21ae632 +
`ve_brain.RawAxes`/`StrategyRouter` fără reimplementare. Consumatorul rulează într-un venv separat; niciun import
`ai_trader` bare nu scapă în afara namespace-ului izolat, iar coliziunea cu detectorii ve_tower e fail-closed.

INTERZIS (absent prin construcție): MT5/broker/ve_tower/set_authority/order_send/probability_inputs/fallback legacy.
"""

from __future__ import annotations

from typing import Any

from ._bootstrap import ensure_loaded, vendored_module, N1ReplayLoadCollisionError
from .version import (
    VE_N1_REPLAY_VERSION, N1_REPLAY_CONTRACT_VERSION, SNAPSHOT_SCHEMA_VERSION, REASON_CODE_SCHEMA_VERSION,
    AI_SOURCE_COMMIT, DETECTOR_SUBMODULE_COMMIT, VE_BRAIN_VERSION, VE_BRAIN_WHEEL_SHA256,
    VENDORED_AI_BLOB_SHA1, VENDORED_DETECTOR_BLOB_SHA1, RAW_AXES_BUILDER_IMPL_COMMIT, build_info,
)

__version__ = VE_N1_REPLAY_VERSION

ensure_loaded()   # încarcă izolat closure-ul (fail-closed la coliziune) ÎNAINTE de a expune suprafața

# suprafața reală, din pachetul vendat (byte-identic @21ae632)
_pkg: Any = vendored_module("ai_trader.n1_replay")
N1ReplayEngine = _pkg.N1ReplayEngine
N1ReplayResult = _pkg.N1ReplayResult
N1ReplaySnapshot = _pkg.N1ReplaySnapshot
EvaluationIdentity = _pkg.EvaluationIdentity
build_evaluation_identity = _pkg.build_evaluation_identity
N1ReplayError = _pkg.N1ReplayError
BarNotClosedError = _pkg.BarNotClosedError
DuplicateBarError = _pkg.DuplicateBarError
FutureBarError = _pkg.FutureBarError
IncompatibleSnapshotError = _pkg.IncompatibleSnapshotError
NonFiniteAxesInputError = _pkg.NonFiniteAxesInputError
OutOfOrderBarError = _pkg.OutOfOrderBarError
StaleStateError = _pkg.StaleStateError

# tipul Bar al intrării (bare închise) — din closure-ul vendat
_lss: Any = vendored_module("ai_trader.live_signal_source.types")
Bar = _lss.Bar

# ── 0.1.1: motorul N1 INCREMENTAL (O(n)/mărginit-amortizat) + ledger canonic precompute-once ──
from .version import (
    HISTORY_HORIZON, HISTORY_HORIZON_VERSION, LEDGER_SCHEMA_VERSION, INCREMENTAL_SNAPSHOT_SCHEMA_VERSION,
)
from .incremental import (   # noqa: E402  (după ensure_loaded — closure-ul trebuie încărcat întâi)
    IncrementalRawAxesBuilder, N1IncrementalReplayEngine, N1IncrementalSnapshot,
    N1IncrementalLedger, N1IncrementalLedgerRecord,
)
# ── 0.2.0: producător ADITIV RANGE_STATE + evenimente longitudinale (N1 rămâne byte-identic) ──
from .version import (
    PKG_N1_CONTRACT_VERSION, PKG_RAW_AXIS_SCHEMA_VERSION, PKG_ROUTER_VERSION,
    RANGE_STATE_CONTRACT_VERSION, RANGE_EVENT_CONTRACT_VERSION, RANGE_SNAPSHOT_SCHEMA_VERSION,
    RANGE_LEDGER_SCHEMA_VERSION, RANGE_STATE_SCHEMA_VERSION,
)
from .range_state import (   # noqa: E402
    RangeConfig, RangeStateProducer, RangeStateResult, RangeEvent, RangeEventKind,
    BoundaryValidity, DataReadiness, ConsolidationState, MachineState,
    EntryDecision, entry_decision, SAFETY_GUARD_RANGE_MID_NO_ENTRY, SAFETY_GUARDS_REGISTER,
    RangeContractError,
)
from .range_engine import (  # noqa: E402
    RangeStateReplayEngine, RangeLedger, RangeReplayRecord, RangeSnapshot, RangeSnapshotError,
)


def initialize(*, symbol: str, timeframe: str, bar_interval_seconds: int,
               implementation_commit: str = RAW_AXES_BUILDER_IMPL_COMMIT, **kwargs: object) -> object:
    """Factory convenabil pentru `N1ReplayEngine` (aliniat cu suprafața cerută initialize/observe/…)."""
    return N1ReplayEngine(symbol=symbol, timeframe=timeframe, bar_interval_seconds=bar_interval_seconds,
                          implementation_commit=implementation_commit, **kwargs)


__all__ = [
    "N1ReplayEngine", "N1ReplayResult", "N1ReplaySnapshot", "EvaluationIdentity", "build_evaluation_identity", "Bar",
    "N1ReplayError", "BarNotClosedError", "DuplicateBarError", "FutureBarError", "IncompatibleSnapshotError",
    "NonFiniteAxesInputError", "OutOfOrderBarError", "StaleStateError", "initialize",
    "ensure_loaded", "vendored_module", "N1ReplayLoadCollisionError",
    "IncrementalRawAxesBuilder", "N1IncrementalReplayEngine", "N1IncrementalSnapshot",
    "N1IncrementalLedger", "N1IncrementalLedgerRecord",
    "HISTORY_HORIZON", "HISTORY_HORIZON_VERSION", "LEDGER_SCHEMA_VERSION",
    "INCREMENTAL_SNAPSHOT_SCHEMA_VERSION",
    # 0.2.0 RANGE_STATE + evenimente
    "RangeStateReplayEngine", "RangeConfig", "RangeStateProducer", "RangeStateResult", "RangeEvent",
    "RangeEventKind", "BoundaryValidity", "DataReadiness", "ConsolidationState", "MachineState",
    "EntryDecision", "entry_decision", "SAFETY_GUARD_RANGE_MID_NO_ENTRY", "SAFETY_GUARDS_REGISTER",
    "RangeContractError", "RangeLedger", "RangeReplayRecord", "RangeSnapshot", "RangeSnapshotError",
    "PKG_N1_CONTRACT_VERSION", "PKG_RAW_AXIS_SCHEMA_VERSION", "PKG_ROUTER_VERSION",
    "RANGE_STATE_CONTRACT_VERSION", "RANGE_EVENT_CONTRACT_VERSION", "RANGE_SNAPSHOT_SCHEMA_VERSION",
    "RANGE_LEDGER_SCHEMA_VERSION", "RANGE_STATE_SCHEMA_VERSION",
    "VE_N1_REPLAY_VERSION", "N1_REPLAY_CONTRACT_VERSION", "SNAPSHOT_SCHEMA_VERSION", "REASON_CODE_SCHEMA_VERSION",
    "AI_SOURCE_COMMIT", "DETECTOR_SUBMODULE_COMMIT", "VE_BRAIN_VERSION", "VE_BRAIN_WHEEL_SHA256",
    "VENDORED_AI_BLOB_SHA1", "VENDORED_DETECTOR_BLOB_SHA1", "RAW_AXES_BUILDER_IMPL_COMMIT", "build_info",
]
