"""AMPRENTA DE DECIZIE (T17, AMENDAMENT CEO A5). `configuration_fingerprint`-ul unei decizii identifică ÎMPREUNĂ:
DATELE · CONFIGURAȚIA · STRATEGIA · MOTORUL · VERSIUNEA CONTRACTULUI. Existența hash-ului fără enforcement NU
închide T17 — comparatorul REFUZĂ EFECTIV rezultatele cu amprente diferite, pe TOATE căile.

Nivelul de MĂSURARE (canonical_evaluator.run_hash) acoperă DATELE + CONFIGURAȚIA; amprenta de DECIZIE se construiește
PESTE el, adăugând strategia, motorul și versiunea contractului — cele trei dimensiuni pe care run_hash-ul de
măsurare nu le acoperea.
"""

from __future__ import annotations

import hashlib
import json

from .version import VE_BRAIN_VERSION


class NonComparableDecisionError(RuntimeError):
    """Comparația între decizii cu amprente diferite e IMPOSIBILĂ, nu descurajată."""


def data_identity(*, symbol: str, timeframe: str, block_start: int, block_end: int, segment_id: str,
                  manifest_hash: str) -> str:
    """A5: identitatea COMPLETĂ a datelor. Populația oficială = 4 blocuri; `manifest_hash` le codifică."""
    payload = {"symbol": symbol, "timeframe": timeframe, "block_start": block_start, "block_end": block_end,
               "segment_id": segment_id, "manifest_hash": manifest_hash}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def decision_fingerprint(
    *, measurement_run_hash: str, data_id: str, strategy_id: str, strategy_version: str,
    engine_version: str, measurement_contract_version: str, n1_contract_version: str,
    raw_axis_schema_version: str, router_version: str, eligibility_policy_version: str,
) -> str:
    """Amprenta de decizie: date ‖ config ‖ STRATEGIE ‖ MOTOR ‖ contract ‖ contractul N1 ‖ politicile de rutare."""
    payload = {
        "d1_measurement_run_hash": measurement_run_hash,           # config de măsurare (‖ date, canonical)
        "d2_data_identity": data_id,                              # A5: symbol/timeframe/blocuri/manifest
        "d3_strategy": f"{strategy_id}@{strategy_version}",
        "d4_engine": engine_version,
        "d5_measurement_contract": measurement_contract_version,
        "d6_n1_contract": n1_contract_version, "d7_raw_axis_schema": raw_axis_schema_version,
        "d8_router": router_version, "d9_eligibility_policy": eligibility_policy_version,
        "d10_ve_brain": VE_BRAIN_VERSION,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def require_comparable(*fingerprints: str) -> None:
    """GARDĂ unică de comparație — ridică `NonComparableDecisionError` dacă vreo amprentă diferă. TREBUIE apelată pe
    ORICE cale care compară două decizii; comparația directă a câmpurilor e INTERZISĂ prin contract."""
    uniq = list(dict.fromkeys(fingerprints))
    for i in range(1, len(uniq)):
        if uniq[i] != uniq[0]:
            raise NonComparableDecisionError(
                f"NON_COMPARABLE: amprente diferite {uniq[0]} != {uniq[i]} (date/config/strategie/motor/contract)")


def compare_decisions(fp_a: str, fp_b: str) -> None:
    """Comparatorul sancționat: REFUZĂ (ridică) dacă amprentele diferă. Singura poartă legitimă de comparație."""
    require_comparable(fp_a, fp_b)
