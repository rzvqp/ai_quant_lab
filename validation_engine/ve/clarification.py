"""Cererea de clarificare adresată Statisticianului (VE-ARCH-v1.0 §3.3).

Exact patru câmpuri per cauză: cod, cale exactă a câmpului, motiv, ce există în
registru. **Fără valoare recomandată, fără default propus, fără reformulare a
specificației** — contractul §1.7 interzice alegerea unei valori implicite, iar o
sugestie este o alegere deghizată.
"""

from __future__ import annotations

from datetime import UTC, datetime

from .errors import TAXONOMY, ValidationResult

HEADER = "# CERERE DE CLARIFICARE"

DISCLAIMER = (
    "Acest document constată ce nu poate fi executat și ce există în registru. "
    "**Nu conține valori recomandate, valori implicite propuse sau reformulări ale "
    "specificației** — alegerea aparține exclusiv Statisticianului (contract §1.7).\n\n"
    "Specificația respinsă nu se editează în loc: se emite o versiune nouă, cu "
    "`spec_version` incrementat și hash nou."
)


def render(result: ValidationResult, spec_id: str | None = None, generated_at: str | None = None) -> str:
    ts = generated_at or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        HEADER,
        "",
        "**Emitent:** Validation Engine · **Destinatar:** Statistician",
        f"**Specificație:** {spec_id or '(neidentificată)'}",
        f"**Hash specificație:** {result.spec_sha256 or '(necalculat)'}",
        f"**Moment:** {ts}",
        f"**Etapă atinsă:** {result.stage_reached} · **Cauze:** {len(result.errors)}",
        f"**Accesări de date:** {len(result.data_accesses)}",
        "",
        DISCLAIMER,
        "",
        "---",
        "",
    ]

    for i, err in enumerate(result.errors, start=1):
        name, phase, touches, _ = TAXONOMY[err.code]
        lines += [
            f"## {i}. {err.code} — {name}",
            "",
            f"**1. Cod:** `{err.code}` ({name}; fază: {phase}; date atinse: {touches})",
            f"**2. Câmp:** `{err.field_path}`",
            f"**3. Motiv:** {err.reason}",
            f"**4. În registru:** {err.registry_info or '—'}",
            "",
        ]

    lines += [
        "---",
        "",
        "**Validation Engine s-a oprit. Nu a executat niciun test, nu a construit nicio "
        "populație și nu a atins date de piață.**",
        "",
    ]
    return "\n".join(lines)
