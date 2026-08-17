"""ve_n1_replay — metadate + identitățile de sursă EXACTE + amprentele de integritate ale closure-ului vendat.

Artefact N1 replay INDEPENDENT de ai_trader: împachetează byte-identic modulele AI Trader @21ae632 + detectorii
@61cbd58c și consumă `ve_brain` 0.1.3 ca dependență externă pinuită. NU reutilizează detectorii ve_tower
(market_structure @61cbd58c = blob 52bb1eba…, DIFERIT de ve_tower).
"""

from __future__ import annotations

VE_N1_REPLAY_VERSION: str = "0.1.1"
N1_REPLAY_CONTRACT_VERSION: str = "n1-replay-request-v1"
SNAPSHOT_SCHEMA_VERSION: str = "n1-replay-snapshot-v1"
REASON_CODE_SCHEMA_VERSION: str = "n1-replay-reason-codes-v1"

# ── 0.1.1: remediere de performanță O(n²)→O(n)/mărginit-amortizat (motor N1 INCREMENTAL) ──
# Orizontul de istoric = maximul lookback-ului axelor MĂRGINITE (COMPRESSION_WINDOW), derivat din cod
# (N1_INCREMENTAL_HORIZON.md), NU ghicit. Legat în identitatea de ledger/snapshot, NU în evaluation_identity
# (care rămâne = 0.1.0 pentru ca rezultatul per-bară să fie byte-identic).
HISTORY_HORIZON: int = 460
HISTORY_HORIZON_VERSION: str = "n1-history-horizon-v1"
LEDGER_SCHEMA_VERSION: str = "n1-incremental-ledger-v1"
INCREMENTAL_SNAPSHOT_SCHEMA_VERSION: str = "n1-incremental-snapshot-v1"

# sursele EXACTE
AI_SOURCE_REPO: str = "ai_quant_lab-wp5b"
AI_SOURCE_BRANCH: str = "discovery-mk-matrix-v1"
AI_SOURCE_COMMIT: str = "21ae632"                                   # handoff-ul AI Trader
DETECTOR_SOURCE_REPO: str = "ai_quant_lab-alpha-automation"
DETECTOR_SUBMODULE_COMMIT: str = "61cbd58c3d5da19001b125b65d669ddad54a14c4"   # submodul pinuit (NU ve_tower)

# dependența externă
VE_BRAIN_VERSION: str = "0.1.3"
VE_BRAIN_WHEEL_SHA256: str = "edd208ad6c2c943b17a11759ece1fdf5ab2a7025779b191764c383ecce987d11"

# GIT-BLOB SHA1 — verificabile INDEPENDENT de Red Team (git rev-parse <commit>:<path>). Byte-identitate SEPARATĂ
# pentru modulele AI Trader (@21ae632) și detectori (@61cbd58c).
VENDORED_AI_BLOB_SHA1: dict[str, str] = {
    "n1_replay/__init__.py": "5e3d1d9520f883a2b2a86d4ecec71422db66bfa9",
    "n1_replay/engine.py": "f2df0402907c7eb689ba6b53937a6eee055f216f",
    "n1_replay/errors.py": "2eff7d3371f0d376c79c5b575f52228f098c83b6",
    "n1_replay/identity.py": "08611d44ab6dba40094051734de546789f6e40b0",
    "n1_replay/types.py": "c58d40016736e5bc35df08714f0cbfc288dc2e58",
    "n1_replay/fixtures/__init__.py": "2f481def8b9be154e8861fcf3d16898d0488774d",
    "n1_replay/fixtures/canonical_bars.py": "4c13daf4864b7e4c3143d2fe02d236ab8cee0a26",
    "live_signal_source/types.py": "fc5d534e95d2973f5b6e66dade8119ee81fef774",
    "signal_engine/types.py": "16fba869be2205cad66f2117a0a799e5e6447fc2",
    "market_scanner/types.py": "09ef62241a16e24bd52f31705af00658cd887e35",
    "market_scanner/exceptions.py": "729eb8f80782b4df577c2d58914471c846ac9899",
    "strategy_manager/contract.py": "30bb43f3e0a715dbde9416d307e9d2da795720fe",
    "mandate2_readiness/wheel_verification.py": "99066d6386f3e830408deab11265439860c36b6b",
    "new_brain_bridge/raw_axes_builder.py": "d071c8cbd993cb9377b70af6b61e353d4c101966",
    "structural_observer/vendor_bridge.py": "bb53680c2180a23366b9aa5a08130b4410ea6683",
}
VENDORED_DETECTOR_BLOB_SHA1: dict[str, str] = {
    "market_structure.py": "52bb1eba76d1dee96fae3ed5f5e434c53612176a",   # DIFERIT de ve_tower (d734ac9a)
    "market_state.py": "3f88f8c88988d2b74caf70c199907cf0871c3019",
    "imbalance_mechanics.py": "aa1c6d36d6395a1266b17848296a4c74631ab7c1",
    "order_flow.py": "23b0470086efa24f7b50048e973ecc90fa4a8cb7",
    "order_block_void.py": "2b0f3f37154c4df475e1e7ef0fa782d6f808de9b",
}

RAW_AXES_BUILDER_IMPL_COMMIT: str = AI_SOURCE_COMMIT   # commitul implementării RawAxesBuilder (parte din identitate)


def build_info() -> dict[str, object]:
    return {
        "ve_n1_replay_version": VE_N1_REPLAY_VERSION, "n1_replay_contract_version": N1_REPLAY_CONTRACT_VERSION,
        "ai_source_commit": AI_SOURCE_COMMIT, "detector_submodule_commit": DETECTOR_SUBMODULE_COMMIT,
        "ve_brain_version": VE_BRAIN_VERSION, "ve_brain_wheel_sha256": VE_BRAIN_WHEEL_SHA256,
        "snapshot_schema_version": SNAPSHOT_SCHEMA_VERSION, "reason_code_schema_version": REASON_CODE_SCHEMA_VERSION,
        "history_horizon": HISTORY_HORIZON, "history_horizon_version": HISTORY_HORIZON_VERSION,
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "incremental_snapshot_schema_version": INCREMENTAL_SNAPSHOT_SCHEMA_VERSION,
    }
