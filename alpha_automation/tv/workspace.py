"""Workspace provenance -- logging + linking (no restore).

Per CEO decision 2026-07-22 the TradingView instance is Alpha's own, so the workspace is NOT
restored between investigations and useful research objects may persist. Reproducibility is
preserved instead by:

  * an append-only ACTION LOG (every gated TvClient call, linked to task_id);
  * a per-investigation PROVENANCE SNAPSHOT of the workspace state Alpha observed under
    (symbol/resolution/chart type, studies + which are present, drawings, replay cursor, mode);
  * an ARTIFACT LOG of persistent research objects (indicators/scripts/zones/layouts Alpha created
    and chose to retain), linked to the investigation that produced them.

All three live under state/tv/ as JSONL and survive restarts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from .. import schemas
from .client import TvClient


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkspaceLog:
    def __init__(self, state_dir):
        self.dir = Path(state_dir) / "tv"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.actions_path = self.dir / "actions.jsonl"
        self.snapshots_path = self.dir / "snapshots.jsonl"
        self.artifacts_path = self.dir / "artifacts.jsonl"

    def _append(self, path: Path, rec: dict) -> None:
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    def action_sink(self) -> Callable[[dict], None]:
        """The callable given to TvClient(action_log=...) so every action is logged+linked."""
        return lambda rec: self._append(self.actions_path, rec)

    def record_artifact(self, task_id: str, kind: str, ref: str, detail: Optional[dict] = None) -> None:
        """Log a persistent research object Alpha created and retained (indicator/pine/drawing/layout)."""
        self._append(self.artifacts_path, {
            "task_id": task_id, "kind": kind, "ref": ref, "detail": detail or {}, "ts": _now()})

    def record_snapshot(self, snapshot: dict) -> dict:
        errs = schemas.validate(snapshot, schemas.load_schema("workspace_snapshot"))
        if errs:
            raise ValueError(f"invalid workspace snapshot: {errs}")
        self._append(self.snapshots_path, snapshot)
        return snapshot

    def snapshot(self, client: TvClient, task_id: str, mode_info: dict) -> dict:
        """Capture and persist the workspace state Alpha is observing under, linked to task_id."""
        results = client.batch(
            [("get_state", None), ("list_drawings", None), ("replay_status", None)],
            task_id=task_id, strict=False)
        by_verb = {r.get("verb"): r for r in results}

        state = (by_verb.get("get_state") or {}).get("result", {}) or {}
        drawings = (by_verb.get("list_drawings") or {}).get("result", {}) or {}
        replay = (by_verb.get("replay_status") or {}).get("result", {}) or {}

        snap = {
            "task_id": task_id,
            "ts": _now(),
            "mode": mode_info.get("mode"),
            "data_regime": mode_info.get("data_regime"),
            "symbol": state.get("symbol"),
            "resolution": state.get("resolution"),
            "chart_type": state.get("chartType"),
            "studies": [{"id": s.get("id"), "name": s.get("name")} for s in state.get("studies", [])],
            "drawings": [{"id": s.get("id"), "name": s.get("name")} for s in drawings.get("shapes", [])],
            "replay": {
                "is_started": replay.get("is_replay_started"),
                "current_date": replay.get("current_date"),
            },
            "note": mode_info.get("note"),
        }
        return self.record_snapshot(snap)
