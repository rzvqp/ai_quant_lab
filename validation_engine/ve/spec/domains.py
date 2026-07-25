"""Gramatica închisă a domeniilor din `capabilities.json`.

Registrul descrie domeniul fiecărui parametru printr-un descriptor („integer>=1",
"number in (0,1)", "list[variable_ref]", o listă JSON de valori admise etc.).
Acest modul interpretează exact acele forme.

Regula fail-closed: dacă un descriptor din registru NU este acoperit de gramatică,
`parse` ridică `UnsupportedDomain`, iar validatorul refuză să valideze orice
specificație. Un descriptor neînțeles nu poate fi tratat permisiv — asta ar
însemna un parametru nevalidat, adică exact ce contractul interzice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

NAMED_TYPES = {
    "string": str,
    "boolean": bool,
    "object": dict,
    "integer": int,
    "number": (int, float),
}

#: Tipuri de referință: valoarea trebuie să existe altundeva în specificație
#: sau în registru. Rezolvarea se face de către validatorul de vocabular.
#:
#: `statistic_call` (registru v1.1) este o DECLARAȚIE inline parametrizată, de
#: forma {id, statistic, params} — exact forma pe care schema o cere predicatelor.
#: Rezolvă golul G2: statisticile erau singura categorie cu parametri obligatorii
#: fără loc de declarare în specificație.
REFERENCE_TYPES = {
    "data_source_id",
    "statistic_id",
    "statistic_call",
    "variable_ref",
    "test_ref",         # registru v1.2 (G5): trimite la un test_id declarat
    "predicate_ref",    # registru v1.2 (G5): trimite la id-ul unui predicat declarat
    "predicate",
    "test_target",
    "eligibility_rule", # registru v1.4 (G8): {field, op, value} pe câmpuri PRE-REZULTAT
    "iso8601",
    "window_object",
}

_BOUND = re.compile(r"^(integer|number)\s*(>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)$")
_INTERVAL = re.compile(
    r"^(integer|number)\s+in\s+([\[\(])\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*([\]\)])$"
)
_LIST = re.compile(r"^list\[(.+?)\](?:\s+of\s+length\s+(\d+))?$")
_TUPLE = re.compile(r"^\[(.+)\]$")
_RECORD = re.compile(r"^\{([^}]+)\}$")


class UnsupportedDomain(ValueError):
    """Descriptor de domeniu neacoperit de gramatică."""


@dataclass(frozen=True)
class Domain:
    kind: str          # named | bound | interval | enum | list | tuple | record | reference | union
    raw: object
    detail: object = None

    def describe(self) -> str:
        if self.kind == "enum":
            return "valori admise: " + ", ".join(repr(v) for v in self.detail)
        return f"domeniu: {self.raw}"


def parse(descriptor) -> Domain:
    """Transformă un descriptor de registru într-un obiect Domain."""
    if isinstance(descriptor, list):
        return Domain("enum", descriptor, tuple(descriptor))

    if not isinstance(descriptor, str):
        raise UnsupportedDomain(f"descriptor de tip {type(descriptor).__name__}: {descriptor!r}")

    d = descriptor.strip()

    m = _LIST.match(d)
    if m:
        inner = parse(m.group(1))
        length = int(m.group(2)) if m.group(2) else None
        return Domain("list", d, (inner, length))

    m = _INTERVAL.match(d)
    if m:
        base, lo_b, lo, hi, hi_b = m.groups()
        return Domain("interval", d, (base, lo_b, float(lo), float(hi), hi_b))

    m = _BOUND.match(d)
    if m:
        base, op, val = m.groups()
        return Domain("bound", d, (base, op, float(val)))

    m = _TUPLE.match(d)
    if m and "," in m.group(1):
        parts = [p.strip() for p in m.group(1).split(",")]
        return Domain("tuple", d, tuple(parse(p) for p in parts))

    m = _RECORD.match(d)
    if m:
        keys = tuple(k.strip() for k in m.group(1).split(","))
        return Domain("record", d, keys)

    if "|" in d and "[" not in d and "{" not in d:
        parts = [p.strip() for p in d.split("|")]
        return Domain("union", d, tuple(parse(p) for p in parts))

    if d in NAMED_TYPES:
        return Domain("named", d, NAMED_TYPES[d])

    if d in REFERENCE_TYPES:
        return Domain("reference", d, d)

    raise UnsupportedDomain(f"descriptor de domeniu neacoperit de gramatică: {descriptor!r}")


def check(domain: Domain, value, resolver=None, path: str = "") -> str | None:
    """Verifică o valoare față de un domeniu.

    Întoarce None dacă valoarea e admisă, altfel un motiv (în română).
    `resolver` este apelat pentru tipurile de referință: resolver(kind, value) -> str|None.
    """
    k = domain.kind

    if k == "named":
        expected = domain.detail
        if expected is bool:
            if not isinstance(value, bool):
                return "valoarea trebuie să fie boolean"
            return None
        if expected is int:
            if isinstance(value, bool) or not isinstance(value, int):
                return "valoarea trebuie să fie număr întreg"
            return None
        if expected is dict:
            return None if isinstance(value, dict) else "valoarea trebuie să fie obiect"
        if expected is str:
            return None if isinstance(value, str) else "valoarea trebuie să fie șir de caractere"
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "valoarea trebuie să fie numerică"
        return None

    if k == "bound":
        base, op, limit = domain.detail
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "valoarea trebuie să fie numerică"
        if base == "integer" and not isinstance(value, int):
            return "valoarea trebuie să fie număr întreg"
        ok = {
            ">=": value >= limit,
            "<=": value <= limit,
            ">": value > limit,
            "<": value < limit,
        }[op]
        return None if ok else f"valoarea încalcă restricția {base}{op}{limit:g}"

    if k == "interval":
        base, lo_b, lo, hi, hi_b = domain.detail
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "valoarea trebuie să fie numerică"
        if base == "integer" and not isinstance(value, int):
            return "valoarea trebuie să fie număr întreg"
        lo_ok = value > lo if lo_b == "(" else value >= lo
        hi_ok = value < hi if hi_b == ")" else value <= hi
        return None if (lo_ok and hi_ok) else f"valoarea este în afara intervalului {lo_b}{lo:g},{hi:g}{hi_b}"

    if k == "enum":
        return None if value in domain.detail else "valoare în afara mulțimii admise"

    if k == "list":
        inner, length = domain.detail
        if not isinstance(value, list):
            return "valoarea trebuie să fie listă"
        if length is not None and len(value) != length:
            return f"lista trebuie să aibă exact {length} element(e)"
        for i, item in enumerate(value):
            reason = check(inner, item, resolver, f"{path}[{i}]")
            if reason:
                return f"elementul {i}: {reason}"
        return None

    if k == "tuple":
        parts = domain.detail
        if not isinstance(value, list):
            return "valoarea trebuie să fie listă"
        if len(value) != len(parts):
            return f"lista trebuie să aibă exact {len(parts)} element(e)"
        for i, (dom, item) in enumerate(zip(parts, value)):
            reason = check(dom, item, resolver, f"{path}[{i}]")
            if reason:
                return f"elementul {i}: {reason}"
        return None

    if k == "record":
        keys = set(domain.detail)
        if not isinstance(value, dict):
            return "valoarea trebuie să fie obiect"
        got = set(value)
        if got != keys:
            missing = sorted(keys - got)
            extra = sorted(got - keys)
            bits = []
            if missing:
                bits.append("chei lipsă: " + ", ".join(missing))
            if extra:
                bits.append("chei necunoscute: " + ", ".join(extra))
            return "; ".join(bits)
        return None

    if k == "union":
        reasons = [check(d, value, resolver, path) for d in domain.detail]
        if any(r is None for r in reasons):
            return None
        return "valoarea nu corespunde niciunei variante admise (" + domain.raw + ")"

    if k == "reference":
        if resolver is None:
            return None
        return resolver(domain.detail, value)

    return f"tip de domeniu neimplementat: {k}"
