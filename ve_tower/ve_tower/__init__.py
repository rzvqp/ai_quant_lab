"""ve_tower — furnizorul OFICIAL al fenomenelor N3 (zone map) și N4 (zone confirmation) către AI Trader.

Artefact SEPARAT de ve_brain (profil de dependențe diferit: numpy + pandas, Python ≥3.12). Împachetează modulele
turnului RATIFICATE, BYTE-IDENTICE cu comiturile-sursă (`version.VENDORED_SOURCE_COMMITS`) — NU reconstruiește
detectoarele, NU importă `ai_trader/market_intelligence`. Ieșirea alimentează `ve_brain.DecisionRequest`
(market_map_available / levels_available / confirmation_available).

Suprafața publică curentă (scaffold + tower rulabil): încărcătorul izolat + metadatele. Contractele versionate N3/N4
(request/response cu reason codes + fingerprint) sunt adăugate peste această fundație.
"""

from __future__ import annotations

from ._bootstrap import ensure_tower_loaded, tower_module, TowerLoadCollisionError
from .version import (
    VE_TOWER_VERSION, SOURCE_REPO, SOURCE_BRANCH, VENDORED_SOURCE_COMMITS, VENDORED_BLOB_SHA1,
    LEVEL_TOWER_FREEZE_COMMIT, N3_CONTRACT_VERSION, N4_CONTRACT_VERSION, N3_CODE_VERSION, N4_CODE_VERSION,
    N3_EXPECTED_TIMEFRAME, N4_EXPECTED_TIMEFRAME, VE_BRAIN_TARGET_VERSION, IncompatibleTowerContractError, build_info,
)
from .reason_codes import ReasonCode
from .canonical import canonical_hash, canonical_bytes, git_blob_sha1, NonFiniteValueError
from .data_identity import DataIdentity, DataIdentityError, build_data_identity
from .fingerprint import event_fingerprint, same_event
from .contracts import (
    N3Request, N3Response, N3Level, LevelProvenance, N4Request, N4Response,
    SchemaValidationError, SUPPORTED_N3_CONTRACTS, SUPPORTED_N4_CONTRACTS,
    validate_n3_request, validate_n4_request, assert_n3_compatible, assert_n4_compatible,
)
from .n3 import run_n3
from .n4 import run_n4

__version__ = VE_TOWER_VERSION

__all__ = [
    "ensure_tower_loaded", "tower_module", "TowerLoadCollisionError",
    "VE_TOWER_VERSION", "SOURCE_REPO", "SOURCE_BRANCH", "VENDORED_SOURCE_COMMITS", "VENDORED_BLOB_SHA1",
    "LEVEL_TOWER_FREEZE_COMMIT", "N3_CONTRACT_VERSION", "N4_CONTRACT_VERSION", "N3_CODE_VERSION", "N4_CODE_VERSION",
    "N3_EXPECTED_TIMEFRAME", "N4_EXPECTED_TIMEFRAME", "VE_BRAIN_TARGET_VERSION", "IncompatibleTowerContractError",
    "build_info", "ReasonCode", "canonical_hash", "canonical_bytes", "git_blob_sha1", "NonFiniteValueError",
    "DataIdentity", "DataIdentityError", "build_data_identity", "event_fingerprint", "same_event",
    "N3Request", "N3Response", "N3Level", "LevelProvenance", "N4Request", "N4Response",
    "SchemaValidationError", "SUPPORTED_N3_CONTRACTS", "SUPPORTED_N4_CONTRACTS",
    "validate_n3_request", "validate_n4_request", "assert_n3_compatible", "assert_n4_compatible",
    "run_n3", "run_n4",
]
