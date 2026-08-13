"""ve_brain — „creierul" livrat de Validation Engine către AI Trader (Mandat 1).

Artefact VERSIONAT, instalabil FĂRĂ: copiere de cod, importuri prin căi locale, acces de scriere în repo-ul VE,
reconstruirea detectoarelor, dependențe ascunse de branch-ul de dezvoltare. Aceeași semantică în research/replay/
shadow/live. Eroare EXPLICITĂ la incompatibilitate.

API public: contractele, motorul EV adaptat, contractul strategiilor + rutarea per regim, nodul de decizie N6.
"""

from __future__ import annotations

from .version import (
    VE_BRAIN_VERSION, SOURCE_COMMIT, SOURCE_BRANCH, MEASUREMENT_CONTRACT_VERSION, MEASUREMENT_CONTRACT_STATUS,
    BROKER_ORDER_SUBMISSION, RANGE_STRATEGY_ROUTING, RANGE_BLOCKER, N1_CONTRACT_VERSION, RAW_AXIS_SCHEMA_VERSION,
    ROUTER_VERSION, ELIGIBILITY_POLICY_VERSION, IncompatibleContractError, assert_compatible, build_info,
)
from .reason_codes import ReasonCode
from .contracts import (
    DecisionRequest, DecisionResponse, ProbabilityInputs, OutcomeCell, HierarchyLevel,
    validate_request, validate_response, SchemaValidationError, INPUT_CONTRACT_ID, OUTPUT_CONTRACT_ID,
)
from .strategy_contract import ValidationStatus, can_reach_n6, can_execute_real, TradeProposal
from .regime_routing import (
    SemanticRegime, RawAxes, applicable_regimes, regime_fingerprint, StrategyContract, StrategyRegistry,
    SealedRegistry, catalog_hash, StrategyRouter, RoutingMode, EligibilityDecision, n4_triggers_breakout,
    requires_true_range, strategy_policy_fingerprint, DuplicateStrategyPolicyError,
)
from ._canonical_catalog import (
    CANONICAL_CATALOG_VERSION, CANONICAL_CATALOG_HASH, CANONICAL_STRATEGIES,
)
from .ev_engine import run_ev, ENGINE_VERSION, EV_ENGINE_SOURCE_COMMIT
from .fingerprint import (
    decision_fingerprint, data_identity, require_comparable, compare_decisions, NonComparableDecisionError,
)
from .n6 import decide_n6

__version__ = VE_BRAIN_VERSION

__all__ = [
    "VE_BRAIN_VERSION", "SOURCE_COMMIT", "SOURCE_BRANCH", "MEASUREMENT_CONTRACT_VERSION",
    "MEASUREMENT_CONTRACT_STATUS", "BROKER_ORDER_SUBMISSION", "IncompatibleContractError", "assert_compatible",
    "build_info", "ReasonCode", "DecisionRequest", "DecisionResponse", "ProbabilityInputs", "OutcomeCell",
    "HierarchyLevel", "validate_request", "validate_response", "SchemaValidationError", "INPUT_CONTRACT_ID",
    "OUTPUT_CONTRACT_ID", "ValidationStatus", "can_reach_n6", "can_execute_real", "TradeProposal",
    "SemanticRegime", "RawAxes", "applicable_regimes", "regime_fingerprint", "data_identity", "N1_CONTRACT_VERSION", "ROUTER_VERSION", "RAW_AXIS_SCHEMA_VERSION", "ELIGIBILITY_POLICY_VERSION", "StrategyContract", "RANGE_STRATEGY_ROUTING", "RANGE_BLOCKER", "StrategyRegistry", "SealedRegistry", "catalog_hash", "StrategyRouter", "RoutingMode",
    "EligibilityDecision", "n4_triggers_breakout", "run_ev", "ENGINE_VERSION", "EV_ENGINE_SOURCE_COMMIT",
    "requires_true_range", "strategy_policy_fingerprint", "DuplicateStrategyPolicyError", "decision_fingerprint", "require_comparable", "compare_decisions", "NonComparableDecisionError", "decide_n6",
    "CANONICAL_CATALOG_VERSION", "CANONICAL_CATALOG_HASH", "CANONICAL_STRATEGIES",
]
