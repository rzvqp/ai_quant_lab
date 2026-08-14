"""ve_tower — metadate de versiune + comiturile-sursă EXACTE ale fiecărui modul vendat + versiuni contractuale.

Turnul (N1-N4 + primitivele oficiale) e furnizat de Validation Engine către AI Trader ca artefact SEPARAT de ve_brain
(profil de dependențe diferit: numpy + pandas, Python ≥3.12). Modulele vendate sunt BYTE-IDENTICE cu cele ratificate
din `code/` (verificat de `tests/test_vendor_integrity.py` contra comiturilor de mai jos). NU sunt reconstruite.
"""

from __future__ import annotations

VE_TOWER_VERSION: str = "0.2.0"
# 0.1.0 (contract v1, wheel SHA-256 e5457561604c2bd70ddca98a56b9a4c9ed8a60af95d9048237c768cef08b2db5) a fost
# RESPINS de Red Team (TOWER_HANDOFF_FAIL): fără timeframe strict + fără identitate de date per nod. PĂSTRAT pentru
# audit; 0.2.0 e o schimbare MATERIALĂ de contract (v1→v2), nu o suprascriere.

SOURCE_REPO: str = "ai_quant_lab-wp5b"
SOURCE_BRANCH: str = "discovery-mk-matrix-v1"

# comitul-sursă EXACT al fiecărui modul vendat (heads ratificate; N3/N4 re-ancorate, NU 11ae360/ca683ff)
VENDORED_SOURCE_COMMITS: dict[str, str] = {
    "regime_classifier": "62c447ead295741b88da726488e4f603adfb2fc1",   # N1
    "bias_h1": "850815fa3ddf423a2f335ae219d103e19ea4c508",             # N2
    "zone_map": "588897858277600ff657ae05529584f6c7458ceb",            # N3 (re-anchored)
    "zone_confirmation": "7f2694f67a381d2913f6d790078e54d3ed5f5fd7",    # N4 (W=3)
    "level_output": "c40d33863014bfe3d14f59e324c696d5af04d832",
    "market_state": "a80d8a085dfc26e3042beb512a10aa5c5c1ccb62",
    "market_structure": "362067615d55032ae9105205e640da91c4f248a3",
    "imbalance_mechanics": "1930467631594778d852a1cc19d7cbacf20705e7",
    "liquidity_mechanics": "362067615d55032ae9105205e640da91c4f248a3",
    "institutional_levels": "1930467631594778d852a1cc19d7cbacf20705e7",
    "session_levels": "bf02dd2b91b0c809da1489198d3efe5f28723a95",
    "order_flow": "7d30f59b564577f072ff48336a9e5a185f3ee75c",
    "order_block_void": "edca965fef3504997557160e8bf08d99cfd998be",
}

# GIT-BLOB SHA1 al fiecărui modul vendat — identitatea PE CARE RED TEAM O VERIFICĂ INDEPENDENT cu
# `git rev-parse <source_commit>:code/<mod>.py`. Modulele sunt re-extrase DIRECT din blob (`git cat-file blob`), deci
# byte-identice cu blob-ul (nu „content-identical după normalizare EOL"); `.gitattributes -text` păstrează asta la commit.
VENDORED_BLOB_SHA1: dict[str, str] = {
    "regime_classifier": "7a9f6991b649d4ce5439d97d01da12b97b40b137",
    "bias_h1": "1638c7ddcc362d243b9bfc7d5a3912ca1237cfa9",
    "zone_map": "0607e374af5fec78268bfa5e8f26ad2ad4039e61",
    "zone_confirmation": "347674a7d9bd02cb836b43cce69ff82ea2e1b327",
    "level_output": "8512647cc486be7888dd8497873d04e297a2143f",
    "market_state": "3f88f8c88988d2b74caf70c199907cf0871c3019",
    "market_structure": "d734ac9ae0d30444ace9078a70ca98e41208c3a0",
    "imbalance_mechanics": "aa1c6d36d6395a1266b17848296a4c74631ab7c1",
    "liquidity_mechanics": "45a5219cc8324105ff83622a83c2dc0b375a0310",
    "institutional_levels": "23182f48276d1c3bec9bb01f030a829f3a52d4f0",
    "session_levels": "95dc487b8cbe5c07d2436daeda31de3c840f655f",
    "order_flow": "23b0470086efa24f7b50048e973ecc90fa4a8cb7",
    "order_block_void": "2b0f3f37154c4df475e1e7ef0fa782d6f808de9b",
}

# freeze-ul lanțului N1→N6 (magistrala) — referință de context
LEVEL_TOWER_FREEZE_COMMIT: str = "ad8b586"

# versiuni contractuale (intră în amprente; consumatorul care nu le înțelege eșuează EXPLICIT). v2 = remedierea FAIL.
N3_CONTRACT_VERSION: str = "tower-n3-request-v2"
N4_CONTRACT_VERSION: str = "tower-n4-request-v2"

# TIMEFRAME STRICT — verificat la RUNTIME. Orice altă valoare ⇒ unavailable/INVALID_TIMEFRAME (fail-closed).
N3_EXPECTED_TIMEFRAME: str = "M15"
N4_EXPECTED_TIMEFRAME: str = "M5"
# code_version-urile INTERNE ale modulelor ratificate (din schema lor sigilată)
N3_CODE_VERSION: str = "level3-v2.0-reanchored"
N4_CODE_VERSION: str = "level4-v2.0-w3"

# compatibilitate cu artefactul de decizie (ieșirea turnului alimentează ve_brain.DecisionRequest)
VE_BRAIN_TARGET_VERSION: str = "0.1.3"

SEMANTIC_MODES: tuple[str, ...] = ("research", "replay", "shadow", "live")


class IncompatibleTowerContractError(RuntimeError):
    """Ridicată EXPLICIT când consumatorul cere un contract/versiune de turn nesuportat."""


def build_info() -> dict[str, object]:
    """Amprenta completă a artefactului turn — apare în fiecare ieșire (audit)."""
    return {
        "ve_tower_version": VE_TOWER_VERSION,
        "source_repo": SOURCE_REPO, "source_branch": SOURCE_BRANCH,
        "vendored_source_commits": dict(VENDORED_SOURCE_COMMITS),
        "level_tower_freeze_commit": LEVEL_TOWER_FREEZE_COMMIT,
        "n3_contract_version": N3_CONTRACT_VERSION, "n4_contract_version": N4_CONTRACT_VERSION,
        "n3_code_version": N3_CODE_VERSION, "n4_code_version": N4_CODE_VERSION,
        "ve_brain_target_version": VE_BRAIN_TARGET_VERSION,
    }
