"""`LiveSignalLoop` -- Mandate 4 (2026-07-28): item #7, the last infrastructure piece before shadow
mode. Everything this loop orchestrates was already independently built and proven: `LiveBarFeed`'s
restart-correct watermark and gap detection (Mandates 2/3), `CandidateSignalProducer`'s journaling
(Step 5), the circuit breaker's persisted state (Mandate 3). This module adds exactly what none of those
already provide: interval-based unattended scheduling, and consulting the circuit breaker BEFORE every
cycle's action.

**Circuit breaker consultation, exact semantics**: `tick()` reads `load_persisted_circuit_state` FRESH
from the store on every single call -- never cached, never read once at construction -- so a suspension
that happens between ticks (from whatever process eventually calls `evaluate_circuit_state`/
`reset_emergency_stop`) takes effect on the very next tick, not after some delay. If the state is not
`READY`, the cycle's action (`producer.run_once()`) is skipped entirely -- no bars processed, no
candidates evaluated, no journal entries for that cycle. This loop does NOT itself run
`evaluate_circuit_state` (that requires a live `PortfolioStateSource`, out of this mandate's scope --
"Fara sursa de P&L virtual" carries over from Mandate 2); it only CONSULTS whatever is already persisted.

**Clean stop**: `stop()` sets a plain flag, safe to call from a signal handler, another thread, or a
test. `run_forever()` checks it between ticks and, in a `finally` block, closes the state store --
`SqliteStateStore` commits every write immediately (its own autocommit design), so nothing is ever lost
by stopping between cycles; `close()` here is about releasing the file handle cleanly, not flushing
unsaved state. `install_default_signal_handlers()` wires `SIGINT`/`SIGTERM` to `stop()` for a real
deployment; tests call `_handle_stop_signal` directly rather than sending OS signals, and `run_forever`
accepts `install_signal_handlers=False` to skip registration entirely during tests.

**Disclosed, not built**: a single tick raising (e.g. `BarFeedError` from a transient MT5 disconnect)
propagates out of `run_forever()` uncaught -- there is no retry/backoff here. A months-long unattended
run needs SOME answer to this, but retry policy (immediate vs. backoff, how many attempts, what counts
as escalation) is a real design decision this mandate did not specify; building one unrequested would be
inventing a policy, not implementing a specification.
"""

from __future__ import annotations

import signal
import time
from typing import Callable

from ai_trader.live_signal_source.producer import CandidateSignalProducer
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.risk_manager.types import EngineState
from ai_trader.risk_manager_live.circuit_breaker import load_persisted_circuit_state


def _default_sleep(seconds: float) -> None:
    time.sleep(seconds)


class LiveSignalLoop:
    def __init__(
        self, producer: CandidateSignalProducer, state_store: SqliteStateStore, poll_interval_seconds: float,
    ) -> None:
        if poll_interval_seconds <= 0:
            raise ValueError(
                f"LiveSignalLoop: poll_interval_seconds must be > 0, got {poll_interval_seconds!r}"
            )
        self._producer = producer
        self._state_store = state_store
        self._poll_interval_seconds = poll_interval_seconds
        self._stop_requested = False

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    def stop(self) -> None:
        """Safe to call from a signal handler, another thread, or a test -- sets a plain flag, no I/O."""
        self._stop_requested = True

    def _handle_stop_signal(self, signum: int, frame: object) -> None:
        self.stop()

    def install_default_signal_handlers(self) -> None:
        """Wires SIGINT/SIGTERM to `stop()` for a real deployment. Not called automatically by
        `__init__` or `run_forever` unless requested -- registering OS signal handlers is a deployment
        decision, not something a constructor should do as a side effect."""
        signal.signal(signal.SIGINT, self._handle_stop_signal)
        signal.signal(signal.SIGTERM, self._handle_stop_signal)

    def tick(self) -> bool:
        """Runs exactly one cycle. Returns `True` if the producer actually ran, `False` if the cycle
        was skipped because the persisted circuit breaker state was not `READY`."""
        circuit_state = load_persisted_circuit_state(self._state_store)
        if circuit_state.state is not EngineState.READY:
            return False
        self._producer.run_once()
        return True

    def run_forever(
        self, sleep: Callable[[float], None] = _default_sleep, install_signal_handlers: bool = True,
    ) -> None:
        """Blocks, running `tick()` at `poll_interval_seconds` intervals, until `stop()` is called.
        Closes the state store on the way out regardless of how the loop exits."""
        if install_signal_handlers:
            self.install_default_signal_handlers()
        try:
            while not self._stop_requested:
                self.tick()
                sleep(self._poll_interval_seconds)
        finally:
            self._state_store.close()
