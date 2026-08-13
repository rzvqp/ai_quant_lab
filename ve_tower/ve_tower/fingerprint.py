"""Amprente ale TURNULUI — identitatea evenimentului + configuration fingerprint, CONSTANTE prin tot lanțul N3→N4.

`market_event_id` se propagă neschimbat. `configuration_fingerprint` acoperă identitatea artefactului (versiune +
comiturile-sursă vendate) ‖ identitatea evenimentului (symbol/timeframe/as_of) — deci e IDENTIC la N3 și N4 pentru
același eveniment (versiunile de nod, diferite, se raportează separat, nu în amprenta partajată). Un consumator care
compară ieșirile N3 și N4 poate verifica identitatea de eveniment fără să depindă de nodul care le-a produs.
"""

from __future__ import annotations

import hashlib
import json

from .version import VE_TOWER_VERSION, VENDORED_SOURCE_COMMITS


def _artifact_identity() -> str:
    payload = {"ve_tower_version": VE_TOWER_VERSION, "vendored_source_commits": VENDORED_SOURCE_COMMITS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def configuration_fingerprint(*, market_event_id: str, symbol: str, as_of: int) -> str:
    """Amprentă CONSTANTĂ prin lanț: identitatea artefactului ‖ identitatea evenimentului (id·symbol·as_of).
    NU include timeframe: N3 lucrează pe M15, N4 pe M5, dar evenimentul de decizie e ACELAȘI (același as_of) —
    deci amprenta e IDENTICĂ la N3 și N4. Timeframe-ul e detaliu de nod, nu identitate de eveniment."""
    payload = {
        "artifact": _artifact_identity(),
        "market_event_id": market_event_id, "symbol": symbol, "as_of": as_of,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def same_event(fp_a: str, event_a: str, fp_b: str, event_b: str) -> bool:
    """Adevărat dacă două ieșiri (ex. N3 și N4) aparțin ACELUIAȘI eveniment (id + fingerprint)."""
    return fp_a == fp_b and event_a == event_b
