"""The Replay Clock (``SIMULATION_ARCHITECTURE.md`` §3): the deterministic historical clock, stepping
``as_of`` over the run's date range. Internal type -- no schema entry, no wire representation.

IMPLEMENTATION CHOICE: rather than arithmetically stepping by a fixed interval (which would silently
invent bars on weekends/session gaps the historical data never had), the clock is driven by the exact,
already-known sequence of base-timeframe bar-close timestamps the Replay Data Source loaded
(``SIMULATION_SEQUENCE.md`` §1: "CLK.tick(as_of) -> DS feeds SCAN"). This guarantees the clock only
ever ticks on real, existing bars -- never a fabricated timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_trader.simulation.types import SimPhase


@dataclass(slots=True)
class ReplayClock:
    """Deterministic, ordered ``as_of`` sequencer. ``warmup_ticks`` is the count of leading ticks
    (from ``all_ticks[0]``) that are WARMUP (``SIMULATION_STATE_MACHINE.md`` §A: "NO trades during
    warmup"); every tick after that is RUNNING."""

    all_ticks: tuple[int, ...]
    warmup_ticks: int = 0
    _index: int = field(default=-1, init=False)

    def __post_init__(self) -> None:
        if self.warmup_ticks < 0 or self.warmup_ticks > len(self.all_ticks):
            raise ValueError("ReplayClock.warmup_ticks must be within [0, len(all_ticks)]")
        if list(self.all_ticks) != sorted(self.all_ticks):
            raise ValueError("ReplayClock.all_ticks must be strictly non-decreasing")

    @property
    def bar_index(self) -> int:
        """Monotonic base-bar counter since run start (``SIMULATION_CONTEXT.md`` §B), -1 before the
        first ``tick()``."""
        return self._index

    @property
    def as_of(self) -> int | None:
        """The current tick's timestamp, or ``None`` before the first ``tick()``/after exhaustion."""
        if 0 <= self._index < len(self.all_ticks):
            return self.all_ticks[self._index]
        return None

    @property
    def phase(self) -> SimPhase:
        return SimPhase.WARMUP if self._index < self.warmup_ticks else SimPhase.RUNNING

    @property
    def exhausted(self) -> bool:
        return self._index >= len(self.all_ticks) - 1

    @property
    def remaining(self) -> int:
        return max(0, len(self.all_ticks) - 1 - self._index)

    @property
    def total_ticks(self) -> int:
        return len(self.all_ticks)

    def tick(self) -> int | None:
        """Advance one base bar; returns the new ``as_of``, or ``None`` if the replay is exhausted."""
        if self._index >= len(self.all_ticks) - 1:
            return None
        self._index += 1
        return self.all_ticks[self._index]

    def peek_next(self) -> int | None:
        nxt = self._index + 1
        if nxt < len(self.all_ticks):
            return self.all_ticks[nxt]
        return None
