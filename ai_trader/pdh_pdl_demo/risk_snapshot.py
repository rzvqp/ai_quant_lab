"""`LiveRiskSnapshotBuilder` -- constructs a REAL `SymbolRiskSnapshot` for the generic
`risk_manager`/`risk_manager_live` gate (a SEPARATE, pre-existing safety layer from PDH-PDL's own
S1/S2/S3 -- both must pass; this module does not touch S1/S2/S3).

**Precedent and honest disclosure**: Phase 10's own BTCUSD pilot (`btcusd_phase10_operational_test.py`)
hand-built its `SymbolRiskSnapshot` with several HARDCODED placeholder values (`atr=spread*20`,
`bars_since_gap=100`, `is_weekend_gap=False`, `minutes_to_high_impact_event=999.0`) -- no live ATR,
liquidity, or gap computation was wired for that pilot. This module improves on that precedent for the
fields this project genuinely has live infrastructure for (ATR from real accumulated bars via the
already-built `StreamingIndicatorEngine`; gap detection reusing `LiveBarFeed`'s own `GapRecord`/
`GapClassification`; a real, disclosed volume-ratio liquidity proxy) -- but does NOT invent a
computation for the two fields nothing in this codebase can currently compute live:
`is_past_friday_cutoff`/`is_near_session_close` have no established threshold definition anywhere in
this codebase (confirmed by inspection -- `filters.py`/`limits.py` only ever CONSUME these booleans,
never define how to compute them), and `minutes_to_high_impact_event` needs an economic-calendar feed
this project does not have live access to. Both are left at the SAME values Phase 10's own precedent
used (`False`/`False`, `999.0`) -- matching, not exceeding, the one existing precedent, and disclosed
here rather than silently presented as fully live-computed.
"""

from __future__ import annotations

from collections import deque

from ai_trader.live_signal_source.types import Bar, GapClassification, GapRecord
from ai_trader.market_scanner.indicators import StreamingIndicatorEngine
from ai_trader.market_scanner.types import DataQualityLevel
from ai_trader.risk_manager.types import SymbolRiskSnapshot

_VOLUME_WINDOW = 20
_MINUTES_TO_HIGH_IMPACT_EVENT_UNKNOWN = 999.0
"""Matches Phase 10 BTCUSD's own precedent exactly -- no live economic-calendar feed exists; this is a
disclosed "none known" placeholder, never presented as a real computed value."""


class LiveRiskSnapshotBuilder:
    def __init__(self) -> None:
        self._indicators = StreamingIndicatorEngine()
        self._volume_window: deque[float] = deque(maxlen=_VOLUME_WINDOW)
        self._bars_since_gap: int | None = None
        self._last_gap_classification: GapClassification | None = None

    def update(self, bar: Bar, gaps_this_poll: tuple[GapRecord, ...]) -> None:
        self._indicators.update(bar.high, bar.low, bar.close)
        if bar.volume is not None:
            self._volume_window.append(bar.volume)
        if gaps_this_poll:
            self._bars_since_gap = 0
            self._last_gap_classification = gaps_this_poll[-1].classification
        elif self._bars_since_gap is not None:
            self._bars_since_gap += 1

    def snapshot(self, current_spread: float) -> SymbolRiskSnapshot:
        indicator_snapshot = self._indicators.snapshot()
        liquidity_proxy = None
        if self._volume_window and len(self._volume_window) >= 2:
            latest = self._volume_window[-1]
            average = sum(self._volume_window) / len(self._volume_window)
            liquidity_proxy = latest / average if average > 0 else None
        return SymbolRiskSnapshot(
            atr=indicator_snapshot.atr if indicator_snapshot is not None else None,
            atr_rolling_median=indicator_snapshot.atr_ma if indicator_snapshot is not None else None,
            current_spread=current_spread,
            liquidity_proxy=liquidity_proxy,
            is_weekend_gap=(self._bars_since_gap == 0 and self._last_gap_classification is GapClassification.WEEKEND),
            bars_since_gap=self._bars_since_gap,
            is_past_friday_cutoff=False,  # Phase 10 precedent -- no established live definition exists
            is_near_session_close=False,  # Phase 10 precedent -- no established live definition exists
            minutes_to_high_impact_event=_MINUTES_TO_HIGH_IMPACT_EVENT_UNKNOWN,
            data_quality=DataQualityLevel.OK,
        )
