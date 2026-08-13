"""ve_brain — „creierul" livrat de Validation Engine către AI Trader (Mandat 1).

Artefact VERSIONAT, instalabil FĂRĂ: copiere de cod, importuri prin căi locale, acces de scriere în repo-ul VE,
reconstruirea detectoarelor, dependențe ascunse de branch-ul de dezvoltare. Aceeași semantică în research/replay/
shadow/live. Eroare EXPLICITĂ la incompatibilitate.

API public: contractele, motorul EV adaptat, contractul strategiilor + rutarea per regim, nodul de decizie N6.
"""

from __future__ import annotations

from .version import (
    VE_BRAIN_VERSION, SOURCE_COMMIT, SOURCE_BRANCH, MEASUREMENT_CONTRACT_VERSION, MEASUREMENT_CONTRACT_STATUS,
    BROKER_ORDER_SUBMISSION, RANGE_STRATEGY_ROUTING, RANGE_BLOCKER, IncompatibleContractError, assert_compatible,
    build_info,
)
from .reason_codes import ReasonCode
from .contracts import (
    DecisionRequest, DecisionResponse, ProbabilityInputs, OutcomeCell, HierarchyLevel,
    validate_request, validate_response, SchemaValidationError, INPUT_CONTRACT_ID, OUTPUT_CONTRACT_ID,
)
from .strategy_contract import ValidationStatus, can_reach_n6, can_execute_real, TradeProposal
from .regime_routing import (
    SemanticRegime, applicable_regimes, StrategyContract, StrategyRegistry, StrategyRouter, RoutingMode,
    EligibilityDecision, n4_triggers_breakout,
)
from .ev_engine import run_ev, ENGINE_VERSION, EV_ENGINE_SOURCE_COMMIT
from .fingerprint import decision_fingerprint, require_comparable, compare_decisions, NonComparableDecisionError
from .n6 import decide_n6

__version__ = VE_BRAIN_VERSION

__all__ = [
    "VE_BRAIN_VERSION", "SOURCE_COMMIT", "SOURCE_BRANCH", "MEASUREMENT_CONTRACT_VERSION",
    "MEASUREMENT_CONTRACT_STATUS", "BROKER_ORDER_SUBMISSION", "IncompatibleContractError", "assert_compatible",
    "build_info", "ReasonCode", "DecisionRequest", "DecisionResponse", "ProbabilityInputs", "OutcomeCell",
    "HierarchyLevel", "validate_request", "validate_response", "SchemaValidationError", "INPUT_CONTRACT_ID",
    "OUTPUT_CONTRACT_ID", "ValidationStatus", "can_reach_n6", "can_execute_real", "TradeProposal",
    "SemanticRegime", "applicable_regimes", "StrategyContract", "RANGE_STRATEGY_ROUTING", "RANGE_BLOCKER", "StrategyRegistry", "StrategyRouter", "RoutingMode",
    "EligibilityDecision", "n4_triggers_breakout", "run_ev", "ENGINE_VERSION", "EV_ENGINE_SOURCE_COMMIT",
    "decision_fingerprint", "require_comparable", "compare_decisions", "NonComparableDecisionError", "decide_n6",
]
