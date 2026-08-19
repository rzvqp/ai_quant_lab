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
# ── 0.3.0: SPEC V2 semantică RANGE_STATE — remediu SEMANTIC_SPEC_DEFECT (0.2.0 rămâne neatins, păstrat audit) ──
from .version import (
    PKG_N1_CONTRACT_VERSION_V2, PKG_RAW_AXIS_SCHEMA_VERSION_V2, PKG_ROUTER_VERSION_V2,
    RANGE_STATE_CONTRACT_VERSION_V2, RANGE_EVENT_CONTRACT_VERSION_V2, RANGE_SNAPSHOT_SCHEMA_VERSION_V2,
    RANGE_LEDGER_SCHEMA_VERSION_V2, RANGE_STATE_SCHEMA_VERSION_V2, RANGE_STATE_MACHINE_VERSION_V2,
    RANGE_PRODUCER_VERSION_V2, RANGE_REASON_CODE_SCHEMA_VERSION_V2,
    RANGE_V2_STATISTICIAN_SOURCE_COMMIT, RANGE_V2_STATISTICIAN_MANIFEST_COMMIT,
    RANGE_V2_STATISTICIAN_MANIFEST_VERSION, RANGE_V2_RULING,
    PREDECESSOR_0_2_0_VERSION, PREDECESSOR_0_2_0_WHEEL_SHA256, PREDECESSOR_0_2_0_BUILD_COMMIT,
    PREDECESSOR_0_2_0_DELIVERY_COMMIT, PREDECESSOR_0_2_0_RANGE_STATE_HANDOFF_PASS_COMMIT,
    N1_BASELINE_VERSION, N1_BASELINE_INCREMENTAL_PASS_COMMIT,
    BARS_PER_INTRADAY_SESSION_M15,
)
from .range_state_v2 import (   # noqa: E402
    RangeConfigV2, RangeStateProducerV2, RangeStateResultV2, RangeEventV2, RangeEventKindV2,
    BoundaryValidityV2, ConsolidationStateV2, StructureClass, MachineStateV2,
    EntryDecisionV2, entry_decision_v2, RangeContractErrorV2,
)
from .range_engine_v2 import (  # noqa: E402
    RangeStateReplayEngineV2, RangeLedgerV2, RangeReplayRecordV2, RangeSnapshotV2, RangeSnapshotErrorV2,
)
# ── 0.3.1: PIN de configurație V2 — w_atr RATIFICAT (0,30), s_max DERIVAT structural (2×w_atr) ──
from .version import (
    W_ATR_CANONICAL, S_MAX_DERIVATION_MULTIPLIER, S_MAX_DERIVATION_FORMULA,
    RANGE_PRODUCER_VERSION_V2_1, RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1, RANGE_LEDGER_SCHEMA_VERSION_V2_1,
    RANGE_CONFIG_SCHEMA_VERSION_V2_1, RANGE_V2_1_STATISTICIAN_PREREG_COMMIT,
    RANGE_V2_1_STATISTICIAN_RESULT_COMMIT, RANGE_V2_1_STATISTICIAN_ADDENDUM_COMMIT,
    RANGE_V2_1_MANIFEST_COMMIT, RANGE_V2_1_MANIFEST_VERSION, RANGE_V2_1_MANIFEST_FINGERPRINT,
    RANGE_V2_1_CONSTRUCTION_CONTROL_EPISODE_ID, LEGACY_S_MAX_REJECTED,
    PREDECESSOR_0_3_0_VERSION, PREDECESSOR_0_3_0_WHEEL_SHA256, PREDECESSOR_0_3_0_BUILD_COMMIT,
    PREDECESSOR_0_3_0_DELIVERY_COMMIT,
)
from .range_state_v2_1 import (   # noqa: E402
    RangeConfigV2Pinned, LegacyConfigRejectedError,
)
from .range_engine_v2_1 import (  # noqa: E402
    RangeStateReplayEngineV2Pinned, RangeLedgerV2Pinned, RangeReplayRecordV2Pinned,
    RangeSnapshotV2Pinned, RangeSnapshotErrorV2Pinned,
)
# ── 0.4.0: RANGE SEMANTIC V3 — redesign longitudinal (segmente, NU un patch peste 0.3.x, NEATINS) ──
from .version import (
    RANGE_SEMANTIC_CONTRACT_VERSION_V3, RANGE_STATE_MACHINE_VERSION_V3, RANGE_EVENT_CONTRACT_VERSION_V3,
    RANGE_SNAPSHOT_SCHEMA_VERSION_V3, RANGE_LEDGER_SCHEMA_VERSION_V3, RANGE_REASON_CODE_CONTRACT_VERSION_V3,
    RANGE_CONFIG_SCHEMA_VERSION_V3, RANGE_EVALUATION_IDENTITY_VERSION_V3, RANGE_PRODUCER_VERSION_V3,
    RANGE_V3_STATISTICIAN_SPEC_COMMIT, RANGE_V3_MANIFEST_COMMIT, RANGE_V3_MANIFEST_VERSION,
    RANGE_V3_MANIFEST_FINGERPRINT, RANGE_V3_HBL_BATCH_PDF_SHA256, RANGE_V3_HBL_PROVENANCE,
    RANGE_V3_D_MIN_INHERITED, RANGE_V3_N_TOUCH_INHERITED, RANGE_V3_K_STATUS, RANGE_V3_N_ACCEPTANCE_STATUS,
    RANGE_V3_W_ATR_STATUS, RANGE_V3_ANCHOR_WINDOW_RULE,
    PREDECESSOR_0_3_1_VERSION, PREDECESSOR_0_3_1_WHEEL_SHA256, PREDECESSOR_0_3_1_BUILD_COMMIT,
    PREDECESSOR_0_3_1_DELIVERY_COMMIT,
)
from .range_semantic_v3 import (   # noqa: E402
    RangeConfigV3, RangeSemanticProducerV3, RangeSemanticResultV3, RangeEventV3,
    SegmentEventKindV3, SegmentLifecycleV3, ConfirmedSegmentRecordV3,
    EntryDecisionV3, entry_decision_v3, ConfigNotRatifiedError, RangeSemanticContractErrorV3,
    REASON_CODES_V3,
)
from .range_engine_v3 import (   # noqa: E402
    RangeSemanticEngineV3, RangeLedgerV3, RangeReplayRecordV3, RangeSnapshotV3, RangeSnapshotErrorV3,
)
# ── 0.4.1: PERFORMANCE DELTA FIX — remediu §12 RT-RANGE-0004 (pantă OLS incrementală O(1)/bară, 0.4.0 NEATINS) ──
from .version import (
    RANGE_PRODUCER_VERSION_V3_1, RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1,
    RANGE_V3_1_RED_TEAM_COMMIT, RANGE_V3_1_RED_TEAM_ENTRY, RANGE_V3_1_RED_TEAM_VERDICT,
    RANGE_V3_1_RED_TEAM_DEFECT_SECTION, RANGE_V3_1_FIX_VARIANT,
    PREDECESSOR_0_4_0_VERSION, PREDECESSOR_0_4_0_WHEEL_SHA256, PREDECESSOR_0_4_0_BUILD_COMMIT,
    PREDECESSOR_0_4_0_DELIVERY_COMMIT,
)
from .range_semantic_v3_1 import RangeConfigV31, RangeSemanticProducerV31   # noqa: E402
from .range_engine_v3_1 import (   # noqa: E402
    RangeSemanticEngineV31, RangeSnapshotV31, RangeSnapshotErrorV31,
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
    # 0.3.0 RANGE SPEC V2
    "RangeStateReplayEngineV2", "RangeConfigV2", "RangeStateProducerV2", "RangeStateResultV2", "RangeEventV2",
    "RangeEventKindV2", "BoundaryValidityV2", "ConsolidationStateV2", "StructureClass", "MachineStateV2",
    "EntryDecisionV2", "entry_decision_v2", "RangeContractErrorV2",
    "RangeLedgerV2", "RangeReplayRecordV2", "RangeSnapshotV2", "RangeSnapshotErrorV2",
    "PKG_N1_CONTRACT_VERSION_V2", "PKG_RAW_AXIS_SCHEMA_VERSION_V2", "PKG_ROUTER_VERSION_V2",
    "RANGE_STATE_CONTRACT_VERSION_V2", "RANGE_EVENT_CONTRACT_VERSION_V2", "RANGE_SNAPSHOT_SCHEMA_VERSION_V2",
    "RANGE_LEDGER_SCHEMA_VERSION_V2", "RANGE_STATE_SCHEMA_VERSION_V2", "RANGE_STATE_MACHINE_VERSION_V2",
    "RANGE_PRODUCER_VERSION_V2", "RANGE_REASON_CODE_SCHEMA_VERSION_V2",
    "RANGE_V2_STATISTICIAN_SOURCE_COMMIT", "RANGE_V2_STATISTICIAN_MANIFEST_COMMIT",
    "RANGE_V2_STATISTICIAN_MANIFEST_VERSION", "RANGE_V2_RULING",
    "PREDECESSOR_0_2_0_VERSION", "PREDECESSOR_0_2_0_WHEEL_SHA256", "PREDECESSOR_0_2_0_BUILD_COMMIT",
    "PREDECESSOR_0_2_0_DELIVERY_COMMIT", "PREDECESSOR_0_2_0_RANGE_STATE_HANDOFF_PASS_COMMIT",
    "N1_BASELINE_VERSION", "N1_BASELINE_INCREMENTAL_PASS_COMMIT", "BARS_PER_INTRADAY_SESSION_M15",
    # 0.3.1 PIN de configurație V2
    "RangeConfigV2Pinned", "LegacyConfigRejectedError",
    "RangeStateReplayEngineV2Pinned", "RangeLedgerV2Pinned", "RangeReplayRecordV2Pinned",
    "RangeSnapshotV2Pinned", "RangeSnapshotErrorV2Pinned",
    "W_ATR_CANONICAL", "S_MAX_DERIVATION_MULTIPLIER", "S_MAX_DERIVATION_FORMULA",
    "RANGE_PRODUCER_VERSION_V2_1", "RANGE_SNAPSHOT_SCHEMA_VERSION_V2_1", "RANGE_LEDGER_SCHEMA_VERSION_V2_1",
    "RANGE_CONFIG_SCHEMA_VERSION_V2_1", "RANGE_V2_1_STATISTICIAN_PREREG_COMMIT",
    "RANGE_V2_1_STATISTICIAN_RESULT_COMMIT", "RANGE_V2_1_STATISTICIAN_ADDENDUM_COMMIT",
    "RANGE_V2_1_MANIFEST_COMMIT", "RANGE_V2_1_MANIFEST_VERSION", "RANGE_V2_1_MANIFEST_FINGERPRINT",
    "RANGE_V2_1_CONSTRUCTION_CONTROL_EPISODE_ID", "LEGACY_S_MAX_REJECTED",
    "PREDECESSOR_0_3_0_VERSION", "PREDECESSOR_0_3_0_WHEEL_SHA256", "PREDECESSOR_0_3_0_BUILD_COMMIT",
    "PREDECESSOR_0_3_0_DELIVERY_COMMIT",
    # 0.4.0 RANGE SEMANTIC V3 (longitudinal, segment-based)
    "RangeConfigV3", "RangeSemanticProducerV3", "RangeSemanticResultV3", "RangeEventV3",
    "SegmentEventKindV3", "SegmentLifecycleV3", "ConfirmedSegmentRecordV3",
    "EntryDecisionV3", "entry_decision_v3", "ConfigNotRatifiedError", "RangeSemanticContractErrorV3",
    "REASON_CODES_V3",
    "RangeSemanticEngineV3", "RangeLedgerV3", "RangeReplayRecordV3", "RangeSnapshotV3", "RangeSnapshotErrorV3",
    "RANGE_SEMANTIC_CONTRACT_VERSION_V3", "RANGE_STATE_MACHINE_VERSION_V3", "RANGE_EVENT_CONTRACT_VERSION_V3",
    "RANGE_SNAPSHOT_SCHEMA_VERSION_V3", "RANGE_LEDGER_SCHEMA_VERSION_V3", "RANGE_REASON_CODE_CONTRACT_VERSION_V3",
    "RANGE_CONFIG_SCHEMA_VERSION_V3", "RANGE_EVALUATION_IDENTITY_VERSION_V3", "RANGE_PRODUCER_VERSION_V3",
    "RANGE_V3_STATISTICIAN_SPEC_COMMIT", "RANGE_V3_MANIFEST_COMMIT", "RANGE_V3_MANIFEST_VERSION",
    "RANGE_V3_MANIFEST_FINGERPRINT", "RANGE_V3_HBL_BATCH_PDF_SHA256", "RANGE_V3_HBL_PROVENANCE",
    "RANGE_V3_D_MIN_INHERITED", "RANGE_V3_N_TOUCH_INHERITED", "RANGE_V3_K_STATUS", "RANGE_V3_N_ACCEPTANCE_STATUS",
    "RANGE_V3_W_ATR_STATUS", "RANGE_V3_ANCHOR_WINDOW_RULE",
    "PREDECESSOR_0_3_1_VERSION", "PREDECESSOR_0_3_1_WHEEL_SHA256", "PREDECESSOR_0_3_1_BUILD_COMMIT",
    "PREDECESSOR_0_3_1_DELIVERY_COMMIT",
    # 0.4.1 PERFORMANCE DELTA FIX (pantă OLS incrementală O(1)/bară — remediu §12 RT-RANGE-0004)
    "RangeConfigV31", "RangeSemanticProducerV31",
    "RangeSemanticEngineV31", "RangeSnapshotV31", "RangeSnapshotErrorV31",
    "RANGE_PRODUCER_VERSION_V3_1", "RANGE_SNAPSHOT_SCHEMA_VERSION_V3_1",
    "RANGE_V3_1_RED_TEAM_COMMIT", "RANGE_V3_1_RED_TEAM_ENTRY", "RANGE_V3_1_RED_TEAM_VERDICT",
    "RANGE_V3_1_RED_TEAM_DEFECT_SECTION", "RANGE_V3_1_FIX_VARIANT",
    "PREDECESSOR_0_4_0_VERSION", "PREDECESSOR_0_4_0_WHEEL_SHA256", "PREDECESSOR_0_4_0_BUILD_COMMIT",
    "PREDECESSOR_0_4_0_DELIVERY_COMMIT",
]
