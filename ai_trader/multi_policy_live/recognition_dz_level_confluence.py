"""`DzLevelConfluenceRecognitionRule` -- CAND-0019 `DZ-LEVEL-CONFLUENCE`, live wiring
(`POLICY_DZ_LEVEL_CONFLUENCE_v2.md`, Part B completed). Same recompute-from-scratch, single-block
pattern as CAND-0001/CAND-0007.

**Part A** (`POLICY_DZ_LEVEL_CONFLUENCE_v1.md`, unchanged, Part A carried into v2.0): same-bar
direction-aligned confluence of a demand/supply zone (`detect_demand_zones`, full anchor-bar
`[Low, High]`, non-consumable) and a PDH/PDL touch (`detect_level_touches`) -- bullish (demand) zone x
PDL support -> long; bearish (supply) zone x PDH resistance -> short. Zone-bar overlap uses the SAME
explicit condition CAND-0013's own (more detailed) canonical DemandZone-reaction doc specifies --
`low[j] <= zone_upper AND high[j] >= zone_lower` -- since CAND-0019 reuses that same DemandZone reaction
semantics, not a single-price touch.

**Part B** (v2.0): stop = below BOTH -- the deeper floor (`min(DemandZone.zone_lower, low[touch_idx])`
long / `max(DemandZone.zone_upper, high[touch_idx])` short); target = the OPPOSITE prior-day level;
time-stop = day boundary. Sizing 1R via S2's live floor, exactly as CAND-0001/CAND-0007."""

from __future__ import annotations

import math

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.vendor_bridge import (
    Block,
    LevelKind,
    OrderBlockKind,
    atr14,
    compute_prior_day_levels,
    detect_demand_zones,
    detect_level_touches,
    min_executable_risk,
    sessions,
)
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.types import LiveTickReader, PdhPdlAuditEntry, PdhPdlAuditKind
from ai_trader.signal_engine.types import Direction

STRATEGY_ID = "S9004"
"""CAND-0019. `S9003` is reserved for CAND-0009 (built inactive, see recognition_level_break_drive.py)."""
MAGIC_NUMBER = 100_004


class DzLevelConfluenceRecognitionRule:
    def __init__(
        self, symbol: str, tick_size: float, tick_reader: LiveTickReader, audit_journal: PdhPdlAuditJournal,
    ) -> None:
        self._symbol = symbol
        self._tick_size = tick_size
        self._tick_reader = tick_reader
        self._audit = audit_journal
        self._opens: list[float] = []
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []
        self._day_index: list[int] = []
        self._consumed_touch_idxs: set[int] = set()
        self._last_trigger: PdhPdlTrigger | None = None
        self._last_level_kind: LevelKind | None = None

    def last_trigger(self) -> PdhPdlTrigger | None:
        return self._last_trigger

    def last_touch_level_kind(self) -> LevelKind | None:
        return self._last_level_kind

    @property
    def current_bar_count(self) -> int:
        return len(self._closes)

    @property
    def current_arrays(self) -> tuple[list[float], list[float], list[float], list[float]]:
        return self._opens, self._highs, self._lows, self._closes

    def _no_trade(self, as_of: int, reason_code: str, **extra: object) -> None:
        self._audit.record(PdhPdlAuditEntry(
            symbol=self._symbol, as_of=as_of, kind=PdhPdlAuditKind.NO_TRADE,
            detail={"reason_code": reason_code, **extra},
        ))

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self._last_trigger = None
        self._last_level_kind = None
        idx = len(self._closes)
        self._opens.append(bar.open)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)
        self._day_index.append(day_boundary_start_utc(bar.ts_open))

        block = Block(0, len(self._closes))
        levels = compute_prior_day_levels(self._highs, self._lows, self._day_index, [block])
        level_touches = detect_level_touches(self._highs, self._lows, levels, self._day_index, [block])
        zones = detect_demand_zones(self._opens, self._highs, self._lows, self._closes, len(self._closes))

        fresh_touches = [t for t in level_touches if t.touch_idx == idx and t.touch_idx not in self._consumed_touch_idxs]
        overlapping_zones = [
            z for z in zones
            if z.formation_idx < idx and self._lows[idx] <= z.zone_upper and self._highs[idx] >= z.zone_lower
        ]
        if not fresh_touches or not overlapping_zones:
            return None

        match = None
        for touch in fresh_touches:
            for zone in overlapping_zones:
                if touch.level.kind is LevelKind.PDL and zone.kind is OrderBlockKind.BULLISH:
                    match = (touch, zone, 1)
                    break
                if touch.level.kind is LevelKind.PDH and zone.kind is OrderBlockKind.BEARISH:
                    match = (touch, zone, -1)
                    break
            if match is not None:
                break
        if match is None:
            self._consumed_touch_idxs.update(t.touch_idx for t in fresh_touches)
            self._no_trade(bar.ts_close, "NO_DIRECTION_ALIGNED_ZONE_CONFLUENCE", touch_idx=idx)
            return None

        touch, zone, direction = match
        self._consumed_touch_idxs.update(t.touch_idx for t in fresh_touches)

        strategy_stop_price = min(zone.zone_lower, self._lows[touch.touch_idx]) if direction > 0 else max(
            zone.zone_upper, self._highs[touch.touch_idx],
        )
        opposite_kind = LevelKind.PDL if touch.level.kind is LevelKind.PDH else LevelKind.PDH
        target_level = next(
            (lv for lv in levels if lv.kind is opposite_kind and lv.available_idx == touch.level.available_idx
             and lv.block_index == touch.level.block_index),
            None,
        )
        if target_level is None:
            self._no_trade(bar.ts_close, "OPPOSITE_LEVEL_NOT_FOUND", touch_idx=idx)
            return None
        target_price = target_level.price

        atr_array = atr14(self._highs, self._lows, self._closes)
        atr_at_touch = atr_array[touch.touch_idx]
        if atr_at_touch is None or math.isnan(float(atr_at_touch)):
            self._no_trade(bar.ts_close, "ATR_NOT_AVAILABLE_AT_TOUCH", touch_idx=idx)
            return None

        tick = self._tick_reader.read(self._symbol)
        if tick is None:
            self._no_trade(bar.ts_close, "LIVE_TICK_UNAVAILABLE", touch_idx=idx)
            return None
        effective_spread = tick.ask - tick.bid
        reference_price = tick.bid if direction < 0 else tick.ask

        min_exec = min_executable_risk(effective_spread, self._tick_size, float(atr_at_touch))
        strategy_stop_distance = abs(reference_price - strategy_stop_price)
        executable_stop_distance = max(strategy_stop_distance, min_exec)
        if executable_stop_distance <= 0:
            self._no_trade(bar.ts_close, "ZERO_OR_NEGATIVE_RISK_AT_LIVE_QUOTE", touch_idx=idx)
            return None
        executable_stop_price = reference_price - direction * executable_stop_distance

        if (direction > 0 and reference_price <= strategy_stop_price) or (
            direction < 0 and reference_price >= strategy_stop_price
        ):
            self._no_trade(bar.ts_close, "NO_TRADE_ENTRY_BEYOND_STRUCTURAL_STOP", touch_idx=idx)
            return None
        if (direction > 0 and reference_price >= target_price) or (direction < 0 and reference_price <= target_price):
            self._no_trade(bar.ts_close, "NO_TRADE_ENTRY_BEYOND_TARGET", touch_idx=idx)
            return None

        self._last_level_kind = touch.level.kind
        self._last_trigger = PdhPdlTrigger(
            touch_idx=idx, entry_idx=idx + 1, direction=direction,
            strategy_stop_price=float(strategy_stop_price), target_price=float(target_price),
            atr_at_touch=float(atr_at_touch), day_boundary_label=self._day_index[idx],
            effective_spread=float(effective_spread), executable_stop_price=float(executable_stop_price),
            tick_size=self._tick_size,
        )
        session = str(sessions([bar.ts_open])[0])
        return LiveCandidate(
            strategy_id=STRATEGY_ID, symbol=self._symbol,
            direction=Direction.LONG if direction > 0 else Direction.SHORT,
            entry=float(reference_price), stop=float(executable_stop_price), target=float(target_price),
            session=session, magic_number=MAGIC_NUMBER, comment="CAND-0019 DZ-LEVEL-CONFLUENCE DEMO",
            as_of=bar.ts_close,
        )
