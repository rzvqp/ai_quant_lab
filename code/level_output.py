"""CONTRACTUL UNIC AVAILABLE / UNAVAILABLE (STAT-INTEGRATION-PHASE-CONTRACT-AND-WIRING-v1.0, 995539a, v2.7.59).

Închide L-U2 (N1) + Z4-L1 (N4) + ZM-U1 (N3): o stare „fără informație" NU are voie să fie reprezentabilă în
același tip ca una informativă. `0` e un număr; `Unavailable` NU e — nu are `value`, deci consumatorul nu poate
atinge payload-ul fără să restrângă tipul mai întâi (mecanism PORTANT, verificat de `mypy --strict`). Extinderea
de mâine se prinde cu `assert_never` pe ramura de cădere (mecanism EXHAUSTIV, care trebuie SCRIS, nu presupus).

`status: str` ca ÂMP se ȘTERGE din ZoneMap / ZoneConfirmationResult / BiasState / Axis: statusul devine
CONSTRUCTORUL, nu un câmp. Două surse de adevăr = niciuna.

MULȚIMEA NECESARĂ (o alegere de MODEL, în `schema_hash`): fiecare consumator declară intrările necesare.
  · intrare în mulțimea necesară + Unavailable  ⇒  ieșire Unavailable, motiv PROPAGAT
  · intrare în afara ei      + Unavailable       ⇒  se continuă, absența SE ÎNREGISTREAZĂ
Fără asta, o axă permanent indisponibilă (N1 știri, N2 momentum) ar face fail-closed → fail-MORT.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import assert_never


@dataclass(frozen=True)
class Ok[T]:
    value: T
    as_of: int                   # indexul barei ÎNCHISE pe care s-a calculat
    valid_until: int             # exclusiv; dincolo de el nu se mai folosește (carry-forward = eroare de tip)
    schema_hash: str


@dataclass(frozen=True)
class Unavailable:
    reason: str                  # motiv MAȘINĂ-LIZIBIL, nu text liber
    as_of: int
    # NU are `value`. NU are `schema_hash`. Absența e DELIBERATĂ (mecanismul portant).


type LevelOutput[T] = Ok[T] | Unavailable


def unwrap_or_none[T](out: LevelOutput[T]) -> T | None:
    """Acces SIGUR: `Ok` → value, `Unavailable` → None. Ramificare pe CONSTRUCTOR, cu `assert_never` la coadă
    ca adăugarea unui al treilea constructor să devină eroare de compilare în toți consumatorii."""
    match out:
        case Ok():
            return out.value
        case Unavailable():
            return None
        case _ as unreachable:
            assert_never(unreachable)


def is_available[T](out: LevelOutput[T]) -> bool:
    return isinstance(out, Ok)
