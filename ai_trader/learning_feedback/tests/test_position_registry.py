"""Tests for RealPositionRegistry -- Architectural Decision Package Decision 1 (Option D)."""

from __future__ import annotations

from ai_trader.learning_feedback.position_registry import RealPositionRegistry, make_position_key
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import Position

RUN_ID = "run-A"


def _position(**overrides: object) -> Position:
    kwargs: dict[str, object] = {
        "symbol": "XAUUSD", "strategy_id": "S1", "direction": Direction.LONG, "size": 1.0,
        "avg_entry": 2000.0, "opened_as_of": 1_700_000_000, "opened_bar_index": 10,
    }
    kwargs.update(overrides)
    return Position(**kwargs)  # type: ignore[arg-type]


def test_make_position_key_deterministic() -> None:
    a = make_position_key(RUN_ID, "XAUUSD", 1_700_000_000, Direction.LONG)
    b = make_position_key(RUN_ID, "XAUUSD", 1_700_000_000, Direction.LONG)
    assert a == b


def test_make_position_key_sensitive_to_every_component() -> None:
    base = make_position_key(RUN_ID, "XAUUSD", 1_700_000_000, Direction.LONG)
    assert base != make_position_key("run-B", "XAUUSD", 1_700_000_000, Direction.LONG)
    assert base != make_position_key(RUN_ID, "EURUSD", 1_700_000_000, Direction.LONG)
    assert base != make_position_key(RUN_ID, "XAUUSD", 1_700_000_400, Direction.LONG)
    assert base != make_position_key(RUN_ID, "XAUUSD", 1_700_000_000, Direction.SHORT)


def test_birth_detected_on_first_observe() -> None:
    reg = RealPositionRegistry(RUN_ID)
    diff = reg.observe({"XAUUSD": _position()})
    assert len(diff.births) == 1
    assert diff.deaths == ()
    assert diff.flips == ()
    born = diff.births[0]
    assert born.symbol == "XAUUSD"
    assert born.strategy_id == "S1"
    assert reg.current_key("XAUUSD") == born


def test_scale_in_does_not_change_identity() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({"XAUUSD": _position()})
    # scale-in: same opened_as_of, size grows -- identity must be stable
    diff = reg.observe({"XAUUSD": _position(size=2.0, avg_entry=2005.0)})
    assert diff.births == ()
    assert diff.deaths == ()
    assert diff.flips == ()


def test_partial_reduce_does_not_change_identity() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({"XAUUSD": _position(size=10.0)})
    diff = reg.observe({"XAUUSD": _position(size=5.0)})  # reduced, same opened_as_of
    assert diff.births == ()
    assert diff.deaths == ()
    assert diff.flips == ()


def test_full_close_is_a_plain_death() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({"XAUUSD": _position()})
    diff = reg.observe({})  # symbol key disappeared
    assert diff.deaths[0].symbol == "XAUUSD"
    assert diff.plain_deaths == diff.deaths
    assert diff.flips == ()
    assert reg.current_key("XAUUSD") is None


def test_close_and_reopen_later_is_death_then_birth_not_a_flip() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({"XAUUSD": _position(opened_as_of=1_700_000_000)})
    reg.observe({})  # fully closed
    diff = reg.observe({"XAUUSD": _position(opened_as_of=1_700_001_000)})  # reopened, later bar
    assert len(diff.births) == 1
    assert diff.births[0].opened_as_of == 1_700_001_000
    assert diff.deaths == ()
    assert diff.flips == ()


def test_flip_detected_same_bar_as_death_and_birth() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({"XAUUSD": _position(direction=Direction.LONG, opened_as_of=1_700_000_000)})
    # SAME bar-diff call shows a NEW opened_as_of/direction at the SAME symbol key -- a flip.
    diff = reg.observe({"XAUUSD": _position(direction=Direction.SHORT, opened_as_of=1_700_000_900, strategy_id="S2")})
    assert diff.births == ()
    assert len(diff.flips) == 1
    old, new = diff.flips[0]
    assert old.direction is Direction.LONG
    assert old.strategy_id == "S1"
    assert new.direction is Direction.SHORT
    assert new.strategy_id == "S2"  # cross-strategy flip attribution preserved
    assert diff.deaths == (old,)
    assert diff.plain_deaths == ()  # the flip's own death is NOT a plain death


def test_multiple_symbols_tracked_independently() -> None:
    reg = RealPositionRegistry(RUN_ID)
    diff = reg.observe({
        "XAUUSD": _position(symbol="XAUUSD", opened_as_of=1_700_000_000),
        "EURUSD": _position(symbol="EURUSD", opened_as_of=1_700_000_000, strategy_id="S2"),
    })
    assert len(diff.births) == 2
    diff2 = reg.observe({"EURUSD": _position(symbol="EURUSD", opened_as_of=1_700_000_000, strategy_id="S2")})
    assert diff2.deaths[0].symbol == "XAUUSD"
    assert diff2.births == ()


def test_drain_returns_every_still_open_key() -> None:
    reg = RealPositionRegistry(RUN_ID)
    reg.observe({
        "XAUUSD": _position(symbol="XAUUSD"),
        "EURUSD": _position(symbol="EURUSD", strategy_id="S2"),
    })
    drained = reg.drain()
    assert {info.symbol for info in drained} == {"XAUUSD", "EURUSD"}


def test_drain_empty_when_nothing_open() -> None:
    reg = RealPositionRegistry(RUN_ID)
    assert reg.drain() == ()


def test_run_id_property() -> None:
    reg = RealPositionRegistry(RUN_ID)
    assert reg.run_id == RUN_ID
