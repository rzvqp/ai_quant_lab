"""Garda de acces la date — dovadă mecanică, nu declarativă.

Mecanism: `sys.addaudithook` (PEP 578), evenimentul "open". Hook-ul prinde
deschiderile de fișiere indiferent dacă vin din `builtins.open`, `io.open`,
`os.open` sau din cod C (ex. cititoarele native pandas/pyarrow), deci nu poate fi
ocolit prin alegerea bibliotecii.

Două regimuri:
  - ÎNREGISTRARE  — toate căile deschise sunt colectate;
  - INTERDICȚIE   — orice deschidere sub o rădăcină de date ridică excepție și
                    operațiunea este abandonată de interpretor.

Un audit hook nu poate fi dezinstalat (proprietate a PEP 578, intenționată).
De aceea hook-ul este instalat o singură dată, la import, și este INACTIV
implicit; se activează exclusiv în interiorul contextului `recording(...)`.
"""

from __future__ import annotations

import os
import sys
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field

from .. import paths


class DataAccessViolation(RuntimeError):
    """Ridicată când se încearcă deschiderea unui fișier de date sub interdicție."""


@dataclass
class AccessRecord:
    """Rezultatul unei ferestre de înregistrare."""

    opened: list[str] = field(default_factory=list)
    data_accesses: list[str] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"fișiere deschise={len(self.opened)} · accesări de date={len(self.data_accesses)}"
        )


_state = threading.local()
_installed = False


def _current() -> AccessRecord | None:
    return getattr(_state, "record", None)


def _forbidding() -> bool:
    return bool(getattr(_state, "forbid", False))


def _data_roots_str() -> tuple[str, ...]:
    return tuple(str(p) for p in paths.data_roots())


def _is_data_path(path: str) -> bool:
    norm = os.path.normcase(path)
    for root in _data_roots_str():
        r = os.path.normcase(root)
        if norm == r or norm.startswith(r + os.sep):
            return True
    return False


def _hook(event: str, args: tuple) -> None:
    if event != "open":
        return
    record = _current()
    if record is None:
        return
    if not args:
        return
    raw = args[0]
    if isinstance(raw, int):  # deschidere după descriptor, fără cale
        return
    try:
        path = os.path.abspath(os.fspath(raw))
    except (TypeError, ValueError):
        return
    record.opened.append(path)
    if _is_data_path(path):
        record.data_accesses.append(path)
        if _forbidding():
            raise DataAccessViolation(
                f"Acces la date interzis în această fază: {path}"
            )


def install() -> None:
    global _installed
    if not _installed:
        sys.addaudithook(_hook)
        _installed = True


@contextmanager
def recording(forbid_data: bool = True):
    """Înregistrează deschiderile de fișiere; opțional interzice accesul la date."""
    install()
    prev_record = getattr(_state, "record", None)
    prev_forbid = getattr(_state, "forbid", False)
    record = AccessRecord()
    _state.record = record
    _state.forbid = forbid_data
    try:
        yield record
    finally:
        _state.record = prev_record
        _state.forbid = prev_forbid


install()
