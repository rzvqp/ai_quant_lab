"""Tests for the Replay Clock."""

from __future__ import annotations

import pytest

from ai_trader.simulation.clock import ReplayClock
from ai_trader.simulation.types import SimPhase


def test_tick_advances_through_all_ticks_then_exhausts() -> None:
    clock = ReplayClock(all_ticks=(100, 200, 300))
    assert clock.as_of is None
    assert clock.tick() == 100
    assert clock.tick() == 200
    assert clock.tick() == 300
    assert clock.tick() is None
    assert clock.exhausted


def test_warmup_then_running_phase() -> None:
    clock = ReplayClock(all_ticks=(100, 200, 300), warmup_ticks=2)
    clock.tick()
    assert clock.phase is SimPhase.WARMUP
    clock.tick()
    assert clock.phase is SimPhase.WARMUP
    clock.tick()
    assert clock.phase is SimPhase.RUNNING


def test_bar_index_monotonic() -> None:
    clock = ReplayClock(all_ticks=(100, 200, 300))
    assert clock.bar_index == -1
    clock.tick()
    assert clock.bar_index == 0
    clock.tick()
    assert clock.bar_index == 1


def test_rejects_unsorted_ticks() -> None:
    with pytest.raises(ValueError):
        ReplayClock(all_ticks=(200, 100))


def test_rejects_warmup_out_of_bounds() -> None:
    with pytest.raises(ValueError):
        ReplayClock(all_ticks=(100, 200), warmup_ticks=5)


def test_peek_next_does_not_advance() -> None:
    clock = ReplayClock(all_ticks=(100, 200))
    assert clock.peek_next() == 100
    assert clock.bar_index == -1
    clock.tick()
    assert clock.peek_next() == 200
