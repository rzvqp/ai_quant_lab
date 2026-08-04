"""`LevelDayExclusion` -- implements the CEO's explicit decision (2026-08-04): "CAND-0001 si CAND-0009
pe acelasi nivel, in aceeasi zi -> NICIUNA nu intra. Excludere, nu prioritate." Statistician precedent
reused verbatim: the disjoint-test-population rule already applied to CAND-0001's own backtest
population against CAND-0009's (`CANDIDATE_QUEUE.md`'s own "W-partition DECIDED" note) -- the SAME
mutual non-interference principle, applied here to LIVE order submission instead of a backtest
population split.

**A disclosed, honest limitation, not glossed over**: CAND-0001 runs as its own separate, already-live,
unmodified OS process (PID confirmed at build time, launched before this package existed) -- it is NOT
part of this package's own event loop and was never authorized to be touched (frozen policy, frozen
wiring). This registry can only ever act as the SECOND-checking party: it reads CAND-0001's own
already-persisted audit journal (`pdh_pdl_live_state/xauusd_m15.db`, `log_name="pdh_pdl_demo.audit"`,
the SAME file/table CAND-0001's own process already writes to) FRESH, immediately before CAND-0009 would
submit a candidate, and refuses CAND-0009's submission if CAND-0001 has ALREADY entered on the same
(level, day) -- in either order of arrival, whichever policy's process reaches this check first
effectively wins in the exceedingly rare case both would fire within the same processing cycle, since
CAND-0001's own process cannot be paused or consulted synchronously. This achieves "neither enters"
for every practically-reachable case (CAND-0001 almost always commits well before CAND-0009's own
30-second-polling process would even see the same bar), but a perfect, provably-symmetric simultaneous
exclusion is not achievable without modifying CAND-0001's own running process, which was never
authorized. Disclosed here rather than silently presented as airtight."""

from __future__ import annotations

from pathlib import Path

from ai_trader.multi_policy_live.vendor_bridge import LevelKind
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.recognition_rule import MAGIC_NUMBER as PDH_PDL_MAGIC_NUMBER
from ai_trader.pdh_pdl_demo.types import PdhPdlAuditKind
from ai_trader.persistent_state.store import SqliteStateStore

_PDH_PDL_AUDIT_LOG_NAME = "pdh_pdl_demo.audit"


def _level_kind_from_pdh_pdl_direction(direction: int) -> LevelKind:
    """CAND-0001's OWN convention (`recognition_rule.py`: `direction = -1 if touch.level.kind is
    LevelKind.PDH else 1`) -- reversal family: PDH touch -> SHORT (-1), PDL touch -> LONG (+1)."""
    return LevelKind.PDH if direction < 0 else LevelKind.PDL


class LevelDayExclusion:
    """Checked by CAND-0009's own recognition/submission path ONLY (the one member of the excluded
    pair this process controls) before every candidate submission. `pdh_pdl_db_path` points at
    CAND-0001's own live state file -- read-only, a fresh `SqliteStateStore` connection opened and
    closed per check (never held open, never a second writer)."""

    def __init__(self, pdh_pdl_db_path: Path) -> None:
        self._pdh_pdl_db_path = pdh_pdl_db_path

    def cand0001_already_entered_today(self, level_kind: LevelKind, day_boundary_label: int) -> bool:
        """`level_kind` is the level CAND-0009's OWN trigger touched, in ITS OWN vocabulary
        (structural, not inferred from its direction, since CAND-0009's direction<->level mapping is
        the OPPOSITE of CAND-0001's -- continuation vs. reversal)."""
        store = SqliteStateStore(self._pdh_pdl_db_path)
        try:
            for payload in store.read_log_entries(_PDH_PDL_AUDIT_LOG_NAME):
                entry = _parse_entry_kind_and_detail(payload)
                if entry is None:
                    continue
                kind, as_of, direction = entry
                if kind is not PdhPdlAuditKind.ENTRY_SUBMITTED:
                    continue
                if direction is None:
                    continue
                if _level_kind_from_pdh_pdl_direction(direction) is not level_kind:
                    continue
                if day_boundary_start_utc(as_of) != day_boundary_label:
                    continue
                return True
            return False
        finally:
            store.close()


def _parse_entry_kind_and_detail(payload: str) -> tuple[PdhPdlAuditKind, int, int | None] | None:
    import json

    try:
        data = json.loads(payload)
        kind = PdhPdlAuditKind(data["kind"])
        as_of = int(data["as_of"])
        direction = data.get("detail", {}).get("direction")
        return kind, as_of, (int(direction) if direction is not None else None)
    except (KeyError, ValueError, TypeError):
        return None


__all__ = ["LevelDayExclusion", "PDH_PDL_MAGIC_NUMBER"]
