"""`StructuralObserver` tests -- Mandate 4 (2026-07-29). Every synthetic price series here was verified
directly against the vendored functions (via a standalone script) before being written into a test --
not hand-derived and hoped-for, matching the same discipline used throughout this mandate series."""

from __future__ import annotations

from pathlib import Path

from ai_trader.live_signal_source.types import Bar
from ai_trader.persistent_state.store import SqliteStateStore
from ai_trader.structural_observer.journal import StructuralObservationLog
from ai_trader.structural_observer.observer import StructuralObserver
from ai_trader.structural_observer.types import StructuralEventKind

SYMBOL = "XAUUSD"
BAR_SECONDS = 900
BASE_TS = 1_700_000_000


def _bar(i: int, open_: float, high: float, low: float, close: float) -> Bar:
    ts_open = BASE_TS + i * BAR_SECONDS
    return Bar(
        symbol=SYMBOL, ts_open=ts_open, ts_close=ts_open + BAR_SECONDS,
        open=open_, high=high, low=low, close=close, volume=100.0,
    )


def _feed(
    observer: StructuralObserver, opens: list[float], highs: list[float],
    lows: list[float], closes: list[float],
) -> None:
    for i, (o, h, lo, c) in enumerate(zip(opens, highs, lows, closes)):
        observer.observe(_bar(i, o, h, lo, c))


# -- market_structure: swings + BOS/CHoCH --


def test_swings_are_recorded_once_labeled() -> None:
    high = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 2.0]
    low = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    close = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 5.0]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)

    swings = [e for e in journal.entries if e.kind is StructuralEventKind.SWING]
    assert len(swings) == 2
    assert swings[0].detail["idx"] == 2
    assert swings[0].detail["swing_kind"] == "high"
    assert swings[0].detail["label"] == "unclassified"
    assert swings[1].detail["idx"] == 7
    assert swings[1].detail["label"] == "HH"
    assert swings[1].detail["price"] == 4.0


def test_structure_break_is_recorded() -> None:
    high = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 2.0]
    low = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    close = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 5.0]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)

    breaks = [e for e in journal.entries if e.kind is StructuralEventKind.STRUCTURE_BREAK]
    assert len(breaks) == 1
    assert breaks[0].detail["idx"] == 10
    assert breaks[0].detail["break_kind"] == "bos_bull"
    assert breaks[0].detail["close"] == 5.0
    assert breaks[0].detail["reference_price"] == 4.0


def test_swings_and_breaks_are_never_recorded_twice_as_the_series_grows() -> None:
    """The recompute-from-scratch design (Step 2's own disclosed property) means every `observe()`
    call re-detects the SAME earlier swings/breaks -- this proves the dedup actually suppresses them,
    not just that they appear once by accident of the specific bar count tested above."""
    high = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 2.0, 2.0, 2.0]
    low = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    close = [1.0, 2.0, 3.0, 2.0, 1.0, 2.0, 3.0, 4.0, 3.0, 2.0, 5.0, 5.0, 5.0]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)  # two extra flat bars beyond the break

    swings = [e for e in journal.entries if e.kind is StructuralEventKind.SWING]
    breaks = [e for e in journal.entries if e.kind is StructuralEventKind.STRUCTURE_BREAK]
    assert len(swings) == 2  # still exactly 2, not re-recorded on bars 11/12
    assert len(breaks) == 1  # still exactly 1


# -- imbalance_mechanics: FVG formed + CE-50/full-fill/inversion reactions --


def test_fvg_formed_and_reaction_stages_are_recorded_incrementally() -> None:
    high = [1.0, 1.5, 2.0, 2.1, 2.0, 1.8]
    low = [0.5, 1.0, 3.0, 1.9, 0.9, 0.5]
    close = [0.8, 1.2, 2.5, 1.95, 1.0, 0.5]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)

    fvg_1_formed = [
        e for e in journal.entries
        if e.kind is StructuralEventKind.FVG_FORMED and e.detail["formed_idx"] == 1
    ]
    assert len(fvg_1_formed) == 1
    assert fvg_1_formed[0].detail["fvg_kind"] == "bullish"
    assert fvg_1_formed[0].detail["lower"] == 1.0
    assert fvg_1_formed[0].detail["upper"] == 3.0
    assert fvg_1_formed[0].detail["ce_50"] == 2.0

    fvg_1_reactions = [
        e for e in journal.entries
        if e.kind is StructuralEventKind.FVG_REACTION and e.detail["formed_idx"] == 1
    ]
    stages = {r.detail["stage"]: r.detail["idx"] for r in fvg_1_reactions}
    assert stages == {"ce50_touch": 3, "full_fill": 4, "inversion": 5}


def test_fvg_reaction_stages_are_never_recorded_twice() -> None:
    high = [1.0, 1.5, 2.0, 2.1, 2.0, 1.8, 1.8, 1.8]
    low = [0.5, 1.0, 3.0, 1.9, 0.9, 0.5, 0.5, 0.5]
    close = [0.8, 1.2, 2.5, 1.95, 1.0, 0.5, 0.5, 0.5]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)  # two extra flat bars after inversion already happened

    fvg_1_reactions = [
        e for e in journal.entries
        if e.kind is StructuralEventKind.FVG_REACTION and e.detail["formed_idx"] == 1
    ]
    assert len(fvg_1_reactions) == 3  # one per stage, never repeated on the extra flat bars


# -- market_state: regime (expansion/compression/session) recorded every bar --


def test_regime_is_recorded_for_every_bar() -> None:
    high = [102.1, 102.1, 102.1]
    low = [101.9, 101.9, 101.9]
    close = [102.0, 102.0, 102.0]
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, close, high, low, close)

    regimes = [e for e in journal.entries if e.kind is StructuralEventKind.REGIME]
    assert len(regimes) == 3  # one per bar, always -- not deduped, not gated
    assert regimes[0].detail["expansion"] is False  # flat range, no ATR warmup yet either
    assert regimes[0].detail["compression"] is None  # fewer than 460 bars -- not yet valid
    assert regimes[0].detail["session"] == "late"  # BASE_TS is 22:13 UTC


# -- order_flow: OB formation + mitigation + rejection + breaker --


def _order_block_series() -> tuple[list[float], list[float], list[float], list[float]]:
    n_warmup = 14
    open_ = [102.0] * n_warmup
    high = [102.1] * n_warmup
    low = [101.9] * n_warmup
    close = [102.0] * n_warmup
    open_.append(102.05); high.append(102.15); low.append(101.85); close.append(101.95)  # bar14: OB anchor
    open_.append(101.5); high.append(110.0); low.append(101.4); close.append(109.0)      # bar15: impulse
    open_.append(103.0); high.append(103.0); low.append(102.0); close.append(103.0)      # bar16: mitigation
    open_.append(102.5); high.append(103.0); low.append(101.8); close.append(102.0)      # bar17: rejection
    open_.append(101.9); high.append(101.9); low.append(100.5); close.append(101.0)      # bar18: breaker
    return open_, high, low, close


def test_order_block_lifecycle_is_recorded() -> None:
    open_, high, low, close = _order_block_series()
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, open_, high, low, close)

    formed = [e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_FORMED]
    assert len(formed) == 1
    assert formed[0].detail["formation_idx"] == 14
    assert formed[0].detail["ob_kind"] == "bullish"
    assert formed[0].detail["zone_lower"] == 101.95
    assert formed[0].detail["zone_upper"] == 102.05

    mitigations = [e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_MITIGATION]
    assert len(mitigations) == 1
    assert mitigations[0].detail["event_idx"] == 16

    rejections = [e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_REJECTION]
    assert len(rejections) == 1
    assert rejections[0].detail["event_idx"] == 17

    breakers = [e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_BREAKER]
    assert len(breakers) == 1
    assert breakers[0].detail["breaker_idx"] == 18
    assert breakers[0].detail["new_kind"] == "bearish"


def test_order_block_events_are_never_recorded_twice() -> None:
    open_, high, low, close = _order_block_series()
    open_.append(101.0); high.append(101.1); low.append(100.9); close.append(101.0)  # bar19: flat, post-breaker
    journal = StructuralObservationLog()
    observer = StructuralObserver(SYMBOL, journal)
    _feed(observer, open_, high, low, close)

    assert len([e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_FORMED]) == 1
    assert len([e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_MITIGATION]) == 1
    assert len([e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_REJECTION]) == 1
    assert len([e for e in journal.entries if e.kind is StructuralEventKind.ORDER_BLOCK_BREAKER]) == 1


# -- persistence: same SqliteStateStore engine, same convention as every other Mandate 2/3 journal --


def test_observations_survive_a_simulated_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "state.db"
    store_before_restart = SqliteStateStore(db_path)
    journal_before_restart = StructuralObservationLog(state_store=store_before_restart)
    observer_before_restart = StructuralObserver(SYMBOL, journal_before_restart)

    high = [1.0, 2.0, 3.0, 2.0, 1.0]
    low = [0.0, 0.0, 0.0, 0.0, 0.0]
    close = [1.0, 2.0, 3.0, 2.0, 1.0]
    _feed(observer_before_restart, close, high, low, close)
    store_before_restart.close()

    store_after_restart = SqliteStateStore(db_path)
    journal_after_restart = StructuralObservationLog(state_store=store_after_restart)

    assert len(journal_after_restart.entries) == len(journal_before_restart.entries)
    assert journal_after_restart.entries[0].kind is journal_before_restart.entries[0].kind
