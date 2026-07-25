"""Captura mediului de execuție. NU citește date de piață.

Înregistrează versiunile exacte de Python și biblioteci, sistemul de operare și
mașina — standardul de reproductibilitate deja atins de laborator
(`REPRODUCIBILITY_AUDIT.md`).
"""

from __future__ import annotations

import platform
import sys
from importlib import metadata


def _pkg(name: str) -> str:
    try:
        return metadata.version(name)
    except Exception:
        return "absent"


def capture() -> dict:
    return {
        "python": sys.version.split()[0],
        "jsonschema": _pkg("jsonschema"),
        "os": platform.platform(),
        "machine": platform.machine(),
        "implementation": platform.python_implementation(),
    }
