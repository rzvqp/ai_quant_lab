"""Research Memory -- append-only JSONL ledgers (source of truth) + in-memory indexes.

Matches the lab's append-only audit-trail convention and is git-diffable. Indexes are rebuilt
from the ledgers on construction, so this IS the restart-recovery path for research state.

It strictly distinguishes the record types the CEO directive requires be kept separate:
  * internal investigation records   -> investigations.jsonl   (every pass, positive or negative)
  * negative findings                -> negatives.jsonl         (internal; never surfaced routinely)
  * tentative observations           -> tentative.jsonl         (unfrozen; promote/discard later)
  * candidate proposals              -> candidates_proposed.jsonl(awaiting the Phase-3 gate)
Frozen Discovery Candidates are NOT stored here -- Phase 3 writes them to the existing
discovery_candidates/ tree. A NEGATIVE result is never a Discovery Candidate.

Derived ledgers (questions_asked, windows_reviewed, perspectives) power duplicate-avoidance and
resumable "what have we already looked at" queries.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from . import schemas

_LEDGERS = {
    "investigations": "investigations.jsonl",
    "negatives": "negatives.jsonl",
    "tentative": "tentative.jsonl",
    "candidates_proposed": "candidates_proposed.jsonl",
    "questions_asked": "questions_asked.jsonl",
    "windows_reviewed": "windows_reviewed.jsonl",
    "perspectives": "perspectives.jsonl",
}


class ResearchMemory:
    def __init__(self, memory_dir):
        self.dir = Path(memory_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._paths = {k: self.dir / v for k, v in _LEDGERS.items()}
        # in-memory indexes
        self._asked: set = set()
        self._task_ids: set = set()
        self._windows: List[dict] = []
        self._perspectives: List[dict] = []
        self._counts: Dict[str, int] = {k: 0 for k in _LEDGERS}
        self._rebuild()

    # ---------- index rebuild (restart recovery) ----------
    def _rebuild(self) -> None:
        for rec in self._iter("questions_asked"):
            if "question_norm" in rec:
                self._asked.add(rec["question_norm"])
        for rec in self._iter("windows_reviewed"):
            self._windows.append(rec)
        for rec in self._iter("perspectives"):
            self._perspectives.append(rec)
        for rec in self._iter("investigations"):
            tid = rec.get("task_id")
            if tid:
                self._task_ids.add(tid)
        for k in _LEDGERS:
            self._counts[k] = sum(1 for _ in self._iter(k))

    def _iter(self, ledger: str):
        p = self._paths[ledger]
        if not p.exists():
            return
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    # A corrupt trailing line (e.g. crash mid-write) is skipped, not fatal.
                    continue

    def _append(self, ledger: str, rec: dict) -> None:
        with self._paths[ledger].open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self._counts[ledger] = self._counts.get(ledger, 0) + 1

    # ---------- queries ----------
    def asked_question_norms(self) -> set:
        return set(self._asked)

    def has_task(self, task_id: str) -> bool:
        return task_id in self._task_ids

    def recent_stances(self, k: int) -> List[Tuple[str, str, str]]:
        out = [tuple(r["stance"]) for r in self._perspectives if "stance" in r]
        return out[-k:] if k > 0 else out

    def reviewed_windows(self, timeframe: Optional[str] = None) -> List[dict]:
        if timeframe is None:
            return list(self._windows)
        return [w for w in self._windows if w.get("timeframe") == timeframe]

    def stats(self) -> Dict[str, int]:
        return dict(self._counts)

    # ---------- writes ----------
    def record_investigation(self, record: dict) -> None:
        """Persist one investigation and fan it out to the derived + typed ledgers.

        `record` must conform to investigation_record.schema.json.
        """
        errs = schemas.validate(record, schemas.load_schema("investigation_record"))
        if errs:
            raise ValueError(f"invalid investigation record: {errs}")

        self._append("investigations", record)
        tid = record["task_id"]
        self._task_ids.add(tid)
        ts = record.get("ts")

        # derived: asked question
        task = record.get("task") or {}
        qn = task.get("question_norm")
        if qn:
            self._asked.add(qn)
            self._append("questions_asked", {"question_norm": qn, "task_id": tid, "ts": ts})

        # derived: reviewed window
        win = record.get("window")
        if win:
            wrec = {
                "timeframe": win.get("timeframe"),
                "start": win.get("start"),
                "end": win.get("end"),
                "edge_ref": task.get("edge_ref"),
                "task_id": tid,
                "ts": ts,
            }
            self._windows.append(wrec)
            self._append("windows_reviewed", wrec)

        # derived: perspective stance
        persp = record.get("perspective") or {}
        if {"lens", "analytical_style", "framing"} <= set(persp):
            prec = {
                "stance": [persp["lens"], persp["analytical_style"], persp["framing"]],
                "perspective_id": persp.get("perspective_id"),
                "task_id": tid,
                "pass": record.get("pass"),
                "ts": ts,
            }
            self._perspectives.append(prec)
            self._append("perspectives", prec)

        # typed routing by outcome
        outcome = record.get("outcome")
        if outcome == "NEGATIVE":
            self._append("negatives", {"task_id": tid, "response": record.get("response"), "ts": ts})
        elif outcome == "TENTATIVE":
            self._append("tentative", {"task_id": tid, "response": record.get("response"), "ts": ts})
        elif outcome == "CANDIDATE_PROPOSED":
            # Held for the Phase-3 gate. A proposal is NOT a frozen candidate.
            self._append("candidates_proposed",
                         {"task_id": tid, "response": record.get("response"), "ts": ts})
