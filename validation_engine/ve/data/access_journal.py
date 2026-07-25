"""Jurnalul de acces la date (F4) — fiecare accesare, verificabilă.

Distinge două tipuri de citire:
  - `hash_read`  — octeții întregului fișier, pentru verificarea integrității;
  - `data_read`  — rânduri parsate ca date (DOAR fereastra deschisă), cu `max_ts_read`.

`max_ts_read` din citirile de tip `data_read` este dovada că holdout-ul nu a fost
folosit ca dată: trebuie să fie strict înaintea graniței sigilate.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .sealing import SEALED_BOUNDARY_EPOCH


@dataclass
class AccessEntry:
    source_id: str
    path: str
    kind: str            # hash_read | data_read
    rows_read: int = 0
    max_ts_read: int | None = None
    stopped_at_boundary: bool = False


@dataclass
class AccessJournal:
    entries: list[AccessEntry] = field(default_factory=list)

    def record(self, entry: AccessEntry) -> None:
        self.entries.append(entry)

    def max_ts_by_source(self) -> dict:
        out: dict[str, int] = {}
        for e in self.entries:
            if e.kind == "data_read" and e.max_ts_read is not None:
                out[e.source_id] = max(out.get(e.source_id, -1), e.max_ts_read)
        return out

    def sealed_window_touched(self) -> bool:
        """True dacă vreo dată parsată are ts la sau peste granița sigilată."""
        return any(ts >= SEALED_BOUNDARY_EPOCH for ts in self.max_ts_by_source().values())

    def to_dict(self) -> dict:
        return {
            "boundary_epoch": SEALED_BOUNDARY_EPOCH,
            "entries": [vars(e) for e in self.entries],
            "max_ts_by_source": self.max_ts_by_source(),
            "sealed_window_touched": self.sealed_window_touched(),
        }
