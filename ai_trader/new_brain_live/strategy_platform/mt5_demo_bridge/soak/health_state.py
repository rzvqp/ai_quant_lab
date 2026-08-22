"""Health/heartbeat state (mandate section 29). A single, overwritten-each-cycle JSON snapshot -- not an
append log (this is "what is true right now", not a history; the ledgers/safety-event-log already provide
history). Written frequently enough that an external observer (or a restarted process) can tell the loop
is alive without needing to parse the full execution ledger. Never a credential, secret, or token --
`account_trade_mode`/`server` are the same non-secret identifiers already printed by `run_live_demo.py`."""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class HealthSnapshot:
    loop_alive_as_of: int
    mt5_connected: bool
    account_trade_mode: str | None
    server: str | None
    equity: float | None
    last_valid_market_event_ts: int | None
    last_processed_bar_ts: int | None
    open_owned_positions: int
    pending_owned_orders: int
    last_reconciliation_as_of: int | None
    last_error: str | None
    safety_blocked: bool
    safety_block_condition: str | None
    trades_closed_so_far: int
    soak_started_at: float
    past_horizon_still_open: int = 0


def write_health_snapshot(path: Path, snapshot: HealthSnapshot) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(dataclasses.asdict(snapshot), indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic on the same filesystem -- a reader never sees a half-written file


def read_health_snapshot(path: Path) -> HealthSnapshot | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return HealthSnapshot(**data)
