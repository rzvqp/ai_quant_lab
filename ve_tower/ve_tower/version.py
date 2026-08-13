"""ve_tower — metadate de versiune + comiturile-sursă EXACTE ale fiecărui modul vendat + versiuni contractuale.

Turnul (N1-N4 + primitivele oficiale) e furnizat de Validation Engine către AI Trader ca artefact SEPARAT de ve_brain
(profil de dependențe diferit: numpy + pandas, Python ≥3.12). Modulele vendate sunt BYTE-IDENTICE cu cele ratificate
din `code/` (verificat de `tests/test_vendor_integrity.py` contra comiturilor de mai jos). NU sunt reconstruite.
"""

from __future__ import annotations

VE_TOWER_VERSION: str = "0.1.0"

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

# amprenta de INTEGRITATE a fiecărui modul vendat (sha256 al conținutului) — gardă anti-tampering post-vendare
VENDORED_CONTENT_SHA256: dict[str, str] = {
    "regime_classifier": "f72e4c386c0e2f01f2423f4b9f29c919e98d9f1f19328d990fe1097950cf7df7",
    "bias_h1": "8ab67aa6e7f4501b85a155effd8c09ad3ee13094cf189da84026268c5ca464c7",
    "zone_map": "3e3e52178053df93148fe966fd8c4440c5698b3857efaabac81ea0b2e7c5277b",
    "zone_confirmation": "273b28ff88ef42d6f4eeec59b51c14c4d39d945b7813f394cde781759f7ab6c3",
    "level_output": "b72b36cf0d9c1cabe106c4c010af5bd0ce8a33a30dae97affa482c3e4913b03b",
    "market_state": "823cf66a7baa21a6a1268a05706d31c9449d1e2c5c56e70cd5ace01a8840504f",
    "market_structure": "629e662c4ce903e4d1e1d33f14e5234b6766bd18b8a469c40229adafb593e981",
    "imbalance_mechanics": "aa676f59cdf23524d47a2c201550ffa9a4f8ca656f4b70fea5878cb8432d949e",
    "liquidity_mechanics": "d5bdc1268815e010221d1c330016add27d4cd2fc0814aa699f14331b84f970e7",
    "institutional_levels": "017536199ec21ecd1c4852f67709d9932b48b7b2be1a7da22d907d7b7a8e12fb",
    "session_levels": "2af2b9e6b684676f0dee86992da18a2c595457c37639117052e25773c09858f0",
    "order_flow": "c7e4f5a760828fab1a31b040fd58233ca206bb3c4c6c858268f33bb779645b0e",
    "order_block_void": "6ec7adbfd3bbaab2d4c1e35f1ad6de2631875319bb5312e90fba572ded32b921",
}

# freeze-ul lanțului N1→N6 (magistrala) — referință de context
LEVEL_TOWER_FREEZE_COMMIT: str = "ad8b586"

# versiuni contractuale (intră în fingerprint; consumatorul care nu le înțelege eșuează EXPLICIT)
N3_CONTRACT_VERSION: str = "tower-n3-request-v1"
N4_CONTRACT_VERSION: str = "tower-n4-request-v1"
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
