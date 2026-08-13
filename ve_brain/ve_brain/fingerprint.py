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


def decision_fingerprint(
    *, measurement_run_hash: str, strategy_id: str, strategy_version: str,
    engine_version: str, measurement_contract_version: str,
) -> str:
    """Cele CINCI dimensiuni, într-un singur hash. `measurement_run_hash` = run_hash-ul canonic (date ‖ config)."""
    payload = {
        "d1_data_and_config": measurement_run_hash,                 # DATELE + CONFIGURAȚIA (canonical run_hash)
        "d2_strategy": f"{strategy_id}@{strategy_version}",         # STRATEGIA
        "d3_engine": engine_version,                               # MOTORUL EV
        "d4_measurement_contract": measurement_contract_version,   # VERSIUNEA CONTRACTULUI de măsurare
        "d5_ve_brain": VE_BRAIN_VERSION,                           # versiunea artefactului
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
