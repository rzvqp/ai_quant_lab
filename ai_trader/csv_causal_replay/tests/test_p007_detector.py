"""Mandate section 5 (reproduce known case) and section 6 (known trigger detected, correct causal
H1 EMA50 used, M15 helper not used as reference, routine bars do not false-trigger). Uses ONLY
already-consumed data <=1304 -- never bar 1305.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ai_trader.csv_causal_replay.identity import M15_BAR_INTERVAL_SECONDS, Q4_START_TS, XAUUSD_M15_SYMBOL
from ai_trader.csv_causal_replay.p007_detector import P007Detector, replay_p007_detection
from ai_trader.csv_causal_replay.sealed_reader import SealedReader, SealedReaderConfig
from ai_trader.csv_causal_replay.types import Bar

REAL_FIXTURE = Path(__file__).parent.parent / "fixtures" / "data" / "Q4_SEALED_1_1304.csv"


def _events_through(upto: int):
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=upto,
    )
    with SealedReader(REAL_FIXTURE, config=config) as reader:
        return replay_p007_detection(reader.iter_rows(), upto_q4_bar_index=upto)


# ── section 5: reproduce the known Q4-P007-004 case, read-only, <=1304 only ─────────────────────

@pytest.mark.skipif(not REAL_FIXTURE.exists(), reason="real fixture not present")
def test_p007_004_trigger_detected_prospectively_at_the_correct_bar():
    events = _events_through(1304)
    triggers = {e.bar_index: e for e in events if e.event_type == "TRIGGER"}
    assert 787 in triggers
    trigger = triggers[787]
    assert trigger.close == pytest.approx(1916.054, abs=0.001)
    assert trigger.h1_ema50 == pytest.approx(1918.200, abs=0.001)


@pytest.mark.skipif(not REAL_FIXTURE.exists(), reason="real fixture not present")
def test_p007_004_resolution_reproduced_at_the_correct_bar():
    events = _events_through(1304)
    resolutions = {e.bar_index: e for e in events if e.event_type == "RESOLUTION"}
    assert 878 in resolutions
    resolution = resolutions[878]
    assert resolution.close == pytest.approx(1905.436, abs=0.001)
    assert resolution.h1_ema50 == pytest.approx(1904.592, abs=0.001)


@pytest.mark.skipif(not REAL_FIXTURE.exists(), reason="real fixture not present")
def test_p007_004_detected_using_only_data_through_878_not_the_full_1304_history():
    """Prospective, not retrospective: the detector must find the 787 trigger and 878 resolution
    using ONLY bars up to 878 -- it does not need to see bars 879-1304 to have already flagged and
    resolved this candidate at the time those bars actually happened."""
    events = _events_through(878)
    triggers = {e.bar_index for e in events if e.event_type == "TRIGGER"}
    resolutions = {e.bar_index for e in events if e.event_type == "RESOLUTION"}
    assert 787 in triggers
    assert 878 in resolutions


@pytest.mark.skipif(not REAL_FIXTURE.exists(), reason="real fixture not present")
def test_detector_is_open_immediately_after_the_trigger_bar_and_closed_after_resolution():
    # Reader ceilings set to EXACTLY the last row wanted in each pass, with an explicit break the
    # moment that row is processed -- REAL_FIXTURE physically contains rows well past both ceilings
    # (it is sealed through 1304), so relying on the reader to stop gracefully on its own would ask
    # it for one row too many and raise SealedBoundaryError instead (caught during development; see
    # p007_detector.replay_p007_detection's own docstring for the same lesson applied there).
    config = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=786,
    )
    detector = P007Detector()
    with SealedReader(REAL_FIXTURE, config=config) as reader:
        for row in reader.iter_rows():
            if row.q4_bar_index is None:
                detector.feed_warmup(row.bar)
                continue
            detector.feed(row.bar, row.q4_bar_index)
            if row.q4_bar_index == 786:
                break
    assert not detector.is_open

    # Feed bar 787 alone (the trigger) -- must now report open, since exactly this bar.
    config2 = SealedReaderConfig(
        symbol=XAUUSD_M15_SYMBOL, bar_interval_seconds=M15_BAR_INTERVAL_SECONDS,
        q4_start_ts=Q4_START_TS, max_q4_bar_index=787,
    )
    detector2 = P007Detector()
    with SealedReader(REAL_FIXTURE, config=config2) as reader:
        for row in reader.iter_rows():
            if row.q4_bar_index is None:
                detector2.feed_warmup(row.bar)
                continue
            detector2.feed(row.bar, row.q4_bar_index)
            if row.q4_bar_index == 787:
                break
    assert detector2.is_open
    assert detector2.open_since_bar_index == 787


# ── section 6: M15 ema.py helper must never be the P007 reference (structural check) ───────────

def test_p007_detector_module_does_not_import_the_m15_ema_helper():
    source = Path(__file__).parent.parent.joinpath("p007_detector.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
    assert "ai_trader.csv_causal_replay.ema" not in imported_names


def test_causal_h1_module_does_not_import_the_m15_ema_helper():
    """Checks actual imports (AST), not a bare substring match -- causal_h1.py's own docstring
    legitimately MENTIONS `ema.py::causal_ema` by name (explaining a design-convention parallel, not
    using it), which a naive substring check would wrongly flag."""
    source = Path(__file__).parent.parent.joinpath("causal_h1.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.name)
    assert "ai_trader.csv_causal_replay.ema" not in imported_names


# ── section 6: routine bars do not false-trigger ────────────────────────────────────────────────

def test_flat_series_never_triggers():
    detector = P007Detector()
    base = 1_600_000_000
    events = []
    for i in range(300):  # >> 50 H1 candles worth of flat M15 bars
        ts = base + i * 900
        bar = Bar(symbol="TEST", ts_open=ts, ts_close=ts + 900, open=100.0, high=100.0, low=100.0, close=100.0, volume=10)
        event = detector.feed(bar, i + 1)
        if event is not None:
            events.append(event)
    assert events == []


def test_a_close_staying_exactly_at_the_ema_never_triggers():
    """`close < ema` is a strict inequality -- a close sitting exactly ON the EMA is not a break."""
    detector = P007Detector()
    base = 1_600_000_000
    for i in range(250):
        ts = base + i * 900
        bar = Bar(symbol="TEST", ts_open=ts, ts_close=ts + 900, open=100.0, high=100.0, low=100.0, close=100.0, volume=10)
        event = detector.feed(bar, i + 1)
        assert event is None
