"""`DecisionAuthority`/`current_authority`/`set_authority` -- Mandate 2, section 5 (CEO, 2026-08-14): the
single, persisted, atomic LEGACY<->NEW_BRAIN decision-authority switch. Mirrors `PolicyControl`'s own
established pattern (`SqliteStateStore.get_value`/`set_value`, re-read fresh on every call, default
baked into the read, external flip capability without touching the running process) -- the SAME
persistence mechanism this codebase already uses for this exact class of problem, not a second one.

**Default is LEGACY for any account that never explicitly set a value.** This module existing, being
imported, or being wired into an entrypoint's constructor does NOT by itself change today's live
behavior -- see `pdh_pdl_demo/orchestration.py`'s and `multi_policy_live/orchestration.py`'s own
`authority_check` parameter (optional, defaults to `None`, meaning "skip the check entirely, behave
exactly as before this mandate").

**Flipping to NEW_BRAIN is a separate, deliberate, external act** (`set_authority(store,
DecisionAuthority.NEW_BRAIN)`), requiring its own explicit confirmation before it is ever invoked
against the live processes' shared state store -- built here per CEO instruction 2026-08-14
("construieste codul, NU comuta inca"), NOT executed. `set_authority` is exported but not called
anywhere in this codebase.

**"Atomic" across two separate OS processes** (`pdh_pdl_demo`, `multi_policy_live`) cannot mean a live,
in-memory flip -- both processes would read this SAME persisted value fresh on every relevant call
(matching the circuit breaker's/`PolicyControl`'s own re-read-every-tick discipline), so the actual
atomic event is a COORDINATED RESTART after the persisted value changes -- the exact same pattern every
other cross-process invariant in this codebase already uses (the duplicate-bar fix, the stale-probe
auto-recovery fix: never a live flag flip, always a deliberate, confirmed, coordinated restart)."""

from __future__ import annotations

from enum import Enum

from ai_trader.persistent_state.store import SqliteStateStore

_KEY = "new_brain_bridge.decision_authority"


class DecisionAuthority(Enum):
    LEGACY = "LEGACY"
    NEW_BRAIN = "NEW_BRAIN"


def current_authority(state_store: SqliteStateStore) -> DecisionAuthority:
    """Re-read fresh on every call -- never cached across ticks, matching every other persisted-flag
    consumer in this codebase (`PolicyControl.is_enabled`, `load_persisted_circuit_state`). Nothing ever
    persisted -> `LEGACY`, today's real, unchanged state."""
    value = state_store.get_value(_KEY)
    if value is None or value == 0.0:
        return DecisionAuthority.LEGACY
    return DecisionAuthority.NEW_BRAIN


def set_authority(state_store: SqliteStateStore, authority: DecisionAuthority) -> None:
    """The ONLY way to flip the switch -- explicit, external, requires the account-level state store
    path (the same one `pdh_pdl_demo`'s/`multi_policy_live`'s own watermark and circuit-breaker state
    already share). NOT called anywhere else in this codebase yet."""
    state_store.set_value(_KEY, 1.0 if authority is DecisionAuthority.NEW_BRAIN else 0.0)
