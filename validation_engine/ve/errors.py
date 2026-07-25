"""Taxonomia de erori a Validation Engine (arhitectură VE-ARCH-v1.0 §9).

Principiu unic: fail-closed. Orice incertitudine oprește execuția.
Nicio eroare nu conține o valoare recomandată — contractul §1.7 interzice
alegerea unei valori implicite, iar o sugestie este o alegere deghizată.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# code -> (nume, fază, atinge date, implementat în F2)
TAXONOMY: dict[str, tuple[str, str, str, bool]] = {
    "E1": ("SPEC_INCOMPLETE", "validare formă", "nu", True),
    "E2": ("SPEC_AMBIGUOUS", "validare formă / vocabular", "nu", True),
    "E3": ("SPEC_UNSUPPORTED", "validare vocabular", "nu", True),
    "E4": ("DATA_INTEGRITY", "preflight", "doar hash", False),
    "E5": ("AUTHORIZATION", "validare vocabular / preflight", "nu", True),
    "E6": ("PRECONDITION", "execuție", "da", False),
    "E7": ("RUNTIME", "execuție", "da", False),
    "E8": ("BUDGET", "execuție", "da", False),
    "E9": ("POST_INTEGRITY", "sigilare", "—", False),
}

#: Codurile pe care faza F2 le poate ridica efectiv. Restul sunt declarate,
#: dar aparțin fazelor F4+ și nu sunt încă implementate.
F2_CODES = frozenset(c for c, meta in TAXONOMY.items() if meta[3])

#: Codurile pentru care contractul cere zero atingere a datelor.
NO_DATA_ACCESS_CODES = frozenset({"E1", "E2", "E3"})


@dataclass(frozen=True)
class VEError:
    """O singură cauză de oprire.

    Câmpurile corespund exact celor patru câmpuri ale cererii de clarificare
    (VE-ARCH-v1.0 §3.3): cod, cale, motiv, ce există în registru.
    """

    code: str
    field_path: str
    reason: str
    registry_info: str = ""

    def __post_init__(self) -> None:
        if self.code not in TAXONOMY:
            raise ValueError(f"cod de eroare necunoscut: {self.code}")

    @property
    def name(self) -> str:
        return TAXONOMY[self.code][0]

    def __str__(self) -> str:
        return f"[{self.code} {self.name}] {self.field_path}: {self.reason}"


class SpecHalt(Exception):
    """Oprire fail-closed cu una sau mai multe cauze."""

    def __init__(self, errors: list[VEError]):
        self.errors = errors
        super().__init__("; ".join(str(e) for e in errors))


@dataclass
class ValidationResult:
    """Rezultatul validării unei specificații.

    `status` este PASSED sau HALTED. Nu există stare intermediară și nu există
    „trecut cu avertismente" — VE nu emite avertismente despre specificație.
    """

    status: str
    errors: list[VEError] = field(default_factory=list)
    spec_sha256: str | None = None
    stage_reached: int = 0
    files_opened: list[str] = field(default_factory=list)
    data_accesses: list[str] = field(default_factory=list)

    @property
    def halted(self) -> bool:
        return self.status == "HALTED"

    @property
    def codes(self) -> list[str]:
        return [e.code for e in self.errors]
