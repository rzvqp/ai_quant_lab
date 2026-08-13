"""VE BRAIN — metadate de versiune + amprentă de configurație + compatibilitate controlată.

Artefactul e FURNIZAT de Validation Engine către AI Trader (Mandat 1). AI Trader îl instalează ca pachet versionat —
FĂRĂ copiere de cod, FĂRĂ importuri prin căi locale, FĂRĂ acces de scriere în repo-ul VE, FĂRĂ reconstruirea
detectoarelor. Versiunea, commit-ul sursă și statutul contractului de măsurare se declară EXPLICIT aici.
"""

from __future__ import annotations

# ── versiunea pachetului (semver) ──
VE_BRAIN_VERSION: str = "0.1.3"

# ── commit-ul sursă EXACT din care e construit artefactul (FAIL-4: RE-PIN pe evaluatorul cu geometrie strictă A2) ──
SOURCE_REPO: str = "ai_quant_lab-wp5b"
SOURCE_BRANCH: str = "discovery-mk-matrix-v1"
SOURCE_COMMIT: str = "dc28e4a"          # corectivul A2 (geometrie strictă); NU 3344bff (asimetricul respins)

# ── contractul de MĂSURARE canonic (evaluatorul) — versiune + STATUT declarat EXPLICIT ──
MEASUREMENT_CONTRACT_VERSION: str = "canonical-evaluator-v2.7.66-A2"   # A2, NU asimetricul
MEASUREMENT_CONTRACT_STATUS: str = "v1.0-DRAFT — NOT RATIFIED"   # Red Team continuă ratificarea în paralel

# ── versiuni de contract/politici (intră în fingerprint; consumatorul care nu le înțelege eșuează EXPLICIT) ──
N1_CONTRACT_VERSION: str = "n1-additive-raw-axes-v1"      # FAIL-2: is_compressed/is_displacement separate
RAW_AXIS_SCHEMA_VERSION: str = "raw-axis-v1"
ROUTER_VERSION: str = "router-v1"
ELIGIBILITY_POLICY_VERSION: str = "eligibility-v1"

# ── contractul TURNULUI (nivelurile N1-N4 + magistrala) ──
LEVEL_CONTRACT_VERSION: str = "level-tower-leveloutput-v1"       # LevelOutput = Ok | Unavailable
LEVEL_TOWER_SOURCE_COMMIT: str = "ad8b586"                       # lanțul N1->N6 înghețat

# ── compatibilitate CONTROLATĂ: AI Trader declară ce contract așteaptă; nepotrivire = eroare EXPLICITĂ ──
# Contracte de intrare/ieșire pe care le suportă acest artefact (o cerere în afara listei => IncompatibleContractError).
SUPPORTED_INPUT_CONTRACTS: tuple[str, ...] = ("ve.market_state.v1",)
SUPPORTED_OUTPUT_CONTRACTS: tuple[str, ...] = ("ve.decision.v1",)
SUPPORTED_STRATEGY_CONTRACTS: tuple[str, ...] = ("ve.strategy.v1",)

# ── aceeași semantică în research / replay / shadow / live: o SINGURĂ implementare, un singur set de contracte ──
SEMANTIC_MODES: tuple[str, ...] = ("research", "replay", "shadow", "live")

# ── AMENDAMENT CEO A1: pachetul produce DECIZII (TRADE / SHADOW_TRADE_CANDIDATE / NO_TRADE), NICIODATĂ ordine reale.
# Dreptul de analiză prin N6 ≠ dreptul de execuție. Submisia de ordine la broker e DEZACTIVATĂ în artefact. ──
BROKER_ORDER_SUBMISSION: str = "DISABLED"

# ── DECIZIE CEO pe defectul de range: RANGE real e NEIDENTIFICABIL (Direction.NEUTRAL conflatează range real, lipsă
# de structură, WARMUP și fail-closed sub n_min). Rutarea strategiilor de range e DEZACTIVATĂ mecanic. ──
RANGE_STRATEGY_ROUTING: str = "DISABLED"
RANGE_BLOCKER: str = "TRUE_RANGE_NOT_IDENTIFIABLE"
# Dezambiguizarea range-ului = WORK ITEM SEPARAT (câmpuri ADITIVE data_readiness / consolidation_state), cu
# specificație cauzală, preînregistrare, versiune nouă, run_hash, teste fără lookahead, validare Red Team + CEO.


class IncompatibleContractError(RuntimeError):
    """Ridicată EXPLICIT când AI Trader cere un contract/versiune nesuportat de acest artefact."""


def assert_compatible(input_contract: str, output_contract: str, strategy_contract: str) -> None:
    """Compatibilitate controlată: nepotrivire ⇒ eroare EXPLICITĂ (nu comportament tăcut, nu default ascuns)."""
    if input_contract not in SUPPORTED_INPUT_CONTRACTS:
        raise IncompatibleContractError(
            f"input contract {input_contract!r} nesuportat de ve_brain {VE_BRAIN_VERSION}; "
            f"suportate: {SUPPORTED_INPUT_CONTRACTS}")
    if output_contract not in SUPPORTED_OUTPUT_CONTRACTS:
        raise IncompatibleContractError(
            f"output contract {output_contract!r} nesuportat; suportate: {SUPPORTED_OUTPUT_CONTRACTS}")
    if strategy_contract not in SUPPORTED_STRATEGY_CONTRACTS:
        raise IncompatibleContractError(
            f"strategy contract {strategy_contract!r} nesuportat; suportate: {SUPPORTED_STRATEGY_CONTRACTS}")


def build_info() -> dict[str, object]:
    """Amprenta completă a artefactului — apare în fiecare decizie (audit)."""
    return {
        "ve_brain_version": VE_BRAIN_VERSION,
        "source_repo": SOURCE_REPO, "source_branch": SOURCE_BRANCH, "source_commit": SOURCE_COMMIT,
        "measurement_contract_version": MEASUREMENT_CONTRACT_VERSION,
        "measurement_contract_status": MEASUREMENT_CONTRACT_STATUS,
        "level_contract_version": LEVEL_CONTRACT_VERSION, "level_tower_source_commit": LEVEL_TOWER_SOURCE_COMMIT,
        "supported_input_contracts": list(SUPPORTED_INPUT_CONTRACTS),
        "supported_output_contracts": list(SUPPORTED_OUTPUT_CONTRACTS),
        "supported_strategy_contracts": list(SUPPORTED_STRATEGY_CONTRACTS),
    }
