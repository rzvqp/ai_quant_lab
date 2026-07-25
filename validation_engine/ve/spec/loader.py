"""Încărcarea specificației și calculul hash-ului.

Nu injectează nimic: dicționarul întors conține exact ce era în fișier. Un loader
care ar completa valori lipsă ar încălca direct contractul §1.7.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ..errors import SpecHalt, VEError

#: Extensii recunoscute ca specificație.
JSON_SUFFIXES = {".json"}
YAML_SUFFIXES = {".yaml", ".yml"}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_spec(path: str | Path) -> tuple[dict, str]:
    """Întoarce (specificație, sha256). Ridică SpecHalt la orice problemă."""
    p = Path(path)
    suffix = p.suffix.lower()

    if suffix in YAML_SUFFIXES:
        raise SpecHalt([
            VEError(
                code="E3",
                field_path=str(p),
                reason=(
                    "Format YAML neacceptat: specificațiile se scriu exclusiv în JSON "
                    "(decizie CEO 2026-07-24, punctul A1). Fișierul nu a fost parsat."
                ),
                registry_info="Formate de specificație acceptate: .json",
            )
        ])

    if suffix not in JSON_SUFFIXES:
        shown = suffix if suffix else "(fără extensie)"
        raise SpecHalt([
            VEError(
                code="E3",
                field_path=str(p),
                reason=f"Extensie de fișier nerecunoscută ca specificație: {shown}.",
                registry_info="Formate de specificație suportate în F2: .json",
            )
        ])

    try:
        raw = p.read_bytes()
    except OSError as exc:
        raise SpecHalt([
            VEError(
                code="E1",
                field_path=str(p),
                reason=f"Specificația nu poate fi citită: {exc.__class__.__name__}.",
                registry_info="",
            )
        ]) from exc

    digest = sha256_bytes(raw)

    try:
        spec = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpecHalt([
            VEError(
                code="E2",
                field_path=str(p),
                reason=f"Specificația nu este JSON valid: {exc}",
                registry_info="",
            )
        ]) from exc

    if not isinstance(spec, dict):
        raise SpecHalt([
            VEError(
                code="E2",
                field_path=str(p),
                reason=f"Rădăcina specificației trebuie să fie un obiect, nu {type(spec).__name__}.",
                registry_info="",
            )
        ])

    return spec, digest
