"""`PolicyControl` -- a persisted, per-policy pause flag (design doc question 6, `MULTI_POLICY_LIVE_DESIGN.md`
9f6f08d: "un flag persistat, per politica... citit din nou la INCEPUTUL fiecarui tick"). Reuses the SAME
`SqliteStateStore.get_value`/`set_value` machinery already used for the bar-feed watermark -- no new
persistence mechanism, matching Mandate 2's "one persistence solution" rule.

Setting a flag needs no access to the running process: any separate script pointed at the SAME shared
account-level `SqliteStateStore` file can flip it (`PolicyControl(store).set_enabled("CAND-0009", True)`)
-- the running loop re-reads it fresh every tick, the same discipline already established for the circuit
breaker (`load_persisted_circuit_state` is never cached across ticks either).

**Default is DISABLED for any policy never explicitly enabled** -- CAND-0009 is wired into the loop's
policy registry but was never given an enabled row, so it starts paused without any extra code at the
call site (CEO: "Construieste-l ca sa poata fi activat, dar nu il porni")."""

from __future__ import annotations

from ai_trader.persistent_state.store import SqliteStateStore

_KEY_PREFIX = "multi_policy_live.policy_enabled:"


class PolicyControl:
    def __init__(self, state_store: SqliteStateStore) -> None:
        self._state_store = state_store

    def is_enabled(self, policy_id: str, default: bool = False) -> bool:
        value = self._state_store.get_value(_KEY_PREFIX + policy_id)
        if value is None:
            return default
        return value != 0.0

    def set_enabled(self, policy_id: str, enabled: bool) -> None:
        self._state_store.set_value(_KEY_PREFIX + policy_id, 1.0 if enabled else 0.0)
