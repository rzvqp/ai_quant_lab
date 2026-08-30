"""Durable pointer/commit-handshake persistence (mandate section 7). JSON on disk, written
atomically (write to a sibling temp file, `os.replace` into place) so a process crash mid-write can
never leave a torn/partial state file -- `os.replace` is atomic on both POSIX and Windows (the
platform this session runs on) for a rename within the same filesystem, which the sibling-temp-file
placement guarantees.

Deliberately NOT SQLite (unlike this repo's other `_state/*.db` directories, e.g.
`live_observation_state/xauusd_m15.db`) -- those hold rolling bar caches with real write-concurrency
needs; this store holds exactly one small record, is read/written by one caller at a time (the
mandate's own single-reasoning-session apprenticeship model), and a plain JSON file is trivially
human-inspectable during an incident, which mandate section 7's own restart-reconstruction
requirement benefits from directly.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_trader.csv_causal_replay.errors import RestartAmbiguityError
from ai_trader.csv_causal_replay.identity import DURABLE_STATE_SCHEMA_VERSION, SourceIdentity
from ai_trader.csv_causal_replay.types import DurableState, PendingDecision


def _source_identity_to_dict(identity: SourceIdentity) -> dict:
    return dataclasses_asdict_shallow(identity)


def dataclasses_asdict_shallow(obj) -> dict:  # type: ignore[no-untyped-def]
    import dataclasses as _dc
    return {f.name: getattr(obj, f.name) for f in _dc.fields(obj)}


def state_to_dict(state: DurableState) -> dict:
    payload = dataclasses_asdict_shallow(state)
    payload["source_identity"] = _source_identity_to_dict(state.source_identity)
    payload["pending_decision"] = (
        dataclasses_asdict_shallow(state.pending_decision) if state.pending_decision is not None else None
    )
    return payload


def state_from_dict(payload: dict) -> DurableState:
    try:
        raw_identity = payload["source_identity"]
        identity = SourceIdentity(
            source_file_name=raw_identity["source_file_name"], content_hash=raw_identity["content_hash"],
            symbol=raw_identity["symbol"], timeframe=raw_identity["timeframe"],
            bar_interval_seconds=raw_identity["bar_interval_seconds"],
            first_bar_ts_open=raw_identity["first_bar_ts_open"],
            sealed_through_bar_index=raw_identity["sealed_through_bar_index"],
            adapter_version=raw_identity["adapter_version"],
            durable_state_schema_version=raw_identity["durable_state_schema_version"],
        )
        raw_pending = payload["pending_decision"]
        pending = (
            None if raw_pending is None
            else PendingDecision(
                bar_id=raw_pending["bar_id"], bar_timestamp=raw_pending["bar_timestamp"],
                bar_index=raw_pending["bar_index"],
            )
        )
        return DurableState(
            source_identity=identity, session_id=payload["session_id"],
            last_committed_bar=payload["last_committed_bar"],
            last_committed_timestamp=payload["last_committed_timestamp"],
            next_bar=payload["next_bar"], pending_decision=pending,
            open_event_state_reference=payload["open_event_state_reference"],
            adapter_version=payload["adapter_version"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RestartAmbiguityError(
            f"durable state file is structurally invalid ({type(exc).__name__}: {exc}) -- refusing "
            "to guess at its intended meaning; inspect the raw file and this session's own "
            "ledgers before resuming"
        ) from exc


class DurablePointerStore:
    """One `DurablePointerStore` per durable-state file on disk. `load()`/`save()` are the only two
    operations -- no partial-update methods, so every write is of a complete, already-validated
    `DurableState` (constructed and validated by `engine.CSVCausalReplayEngine` before it ever
    reaches here)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> DurableState:
        try:
            raw = self._path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise RestartAmbiguityError(
                f"no durable state file at {self._path} -- this engine must be seeded "
                "(engine.seed_from_known_state) before it can resume"
            ) from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RestartAmbiguityError(
                f"durable state file at {self._path} is not valid JSON ({exc}) -- refusing to "
                "guess at its intended meaning"
            ) from exc
        if payload.get("durable_state_schema_version") != DURABLE_STATE_SCHEMA_VERSION:
            raise RestartAmbiguityError(
                f"durable state file at {self._path} carries schema version "
                f"{payload.get('durable_state_schema_version')!r}, expected "
                f"{DURABLE_STATE_SCHEMA_VERSION!r} -- refusing to interpret an unpinned schema"
            )
        return state_from_dict(payload["state"])

    def save(self, state: DurableState) -> None:
        payload = {"durable_state_schema_version": DURABLE_STATE_SCHEMA_VERSION, "state": state_to_dict(state)}
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        tmp_path.replace(self._path)
