"""HASH CANONIC — serializare DETERMINISTĂ, documentată și testată, pentru amprentele de nod și identitatea datelor.

Reguli (verificate de teste):
- **timestamps normalizate**: int-uri, serializate ca șiruri zecimale (fără float, fără fus).
- **ordine fixă**: dicționarele → listă de perechi (cheie, valoare) SORTATĂ după cheie; secvențele își păstrează ordinea.
- **reprezentare numerică fixă**: `float` → cei 8 octeți IEEE-754 big-endian în hex (`struct.pack(">d")`). NU se
  folosește `repr()`/`str()` pe float (deși în Python e stabil, hex-ul IEEE-754 e exact și explicit platform-independent).
- **politica NaN/Inf = REFUZ**: orice `float` nefinit ⇒ `NonFiniteValueError` (nu se hash-uiește o valoare fabricabilă).
- **fără `repr()` dependent de tip**: fiecare tip primește o etichetă (`__i__/__f__/__s__/__b__/__none__/__seq__/__map__`)
  ca `1`(int) și `1.0`(float) și `True`(bool) să NU coincidă.
- aceeași intrare ⇒ același hash; schimbarea unui SINGUR element relevant ⇒ alt hash.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from typing import Any


class NonFiniteValueError(ValueError):
    """Un float NaN/Inf a ajuns în intrarea de hash. Politica e REFUZ (fail-closed), nu normalizare tăcută."""


def _canon(obj: object) -> Any:
    if obj is None:
        return {"__none__": True}
    if isinstance(obj, bool):                       # ÎNAINTE de int (bool e subclasă de int)
        return {"__b__": 1 if obj else 0}
    if isinstance(obj, int):
        return {"__i__": str(obj)}
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise NonFiniteValueError(f"valoare nefinită interzisă în hash: {obj!r}")
        return {"__f__": struct.pack(">d", obj).hex()}
    if isinstance(obj, str):
        return {"__s__": obj}
    if isinstance(obj, (list, tuple)):
        return {"__seq__": [_canon(x) for x in obj]}
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda kv: kv[0])
        return {"__map__": [[k, _canon(v)] for k, v in items]}
    raise TypeError(f"tip neserializabil canonic: {type(obj).__name__}")


def canonical_bytes(obj: object) -> bytes:
    """Bytes DETERMINISTE (ASCII, fără spații, structură complet ordonată)."""
    return json.dumps(_canon(obj), ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def canonical_hash(obj: object) -> str:
    """sha256 (hex) peste serializarea canonică. Refuză NaN/Inf. Include TOT ce i se dă — nu doar câmpuri convenabile."""
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    """Identitatea git-blob a unui conținut (`sha1("blob <len>\\0" + data)`) — verificabilă independent cu
    `git rev-parse <commit>:<path>`. Baza gărzii de byte-identitate a modulelor vendate."""
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode("ascii") + b"\x00")
    h.update(data)
    return h.hexdigest()
