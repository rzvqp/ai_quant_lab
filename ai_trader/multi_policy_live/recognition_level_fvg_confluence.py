"""`LevelFvgConfluenceRecognitionRule` -- CAND-0007 `LEVEL-FVG-CONFLUENCE`, live wiring
(`POLICY_LEVEL_FVG_CONFLUENCE_v2.md`, DEMO_BASELINE, Part B completed). Same recompute-from-scratch,
single-continuous-block pattern `pdh_pdl_demo.recognition_rule.PdhPdlRecognitionRule` established for
CAND-0001 -- day boundaries from the SAME `day_boundary_start_utc`, S2's floor computed live the SAME
way, target-guard logic identical in spirit. This file adds nothing PDH-PDL's own module doesn't already
do; it applies the SAME pattern to a genuinely different Part A/B (two-structure confluence, not a
single level).

**Part A** (`POLICY_LEVEL_FVG_CONFLUENCE_v2.md`, unchanged from v1.0): same-bar direction-aligned
confluence of a PDH/PDL touch (`detect_level_touches`) and an FVG CE-50 touch (`detect_fvg_reactions`,
`ce50_touch_idx`) -- PDL support x bullish FVG -> long; PDH resistance x bearish FVG -> short.

**Part B** (v2.0, DEMO_BASELINE): stop = below BOTH structures, the deeper floor
(`min(low[touch_idx], FVG.lower)` long / `max(high[touch_idx], FVG.upper)` short); target = the
OPPOSITE prior-day level (range reversion, the confluence contains a level); time-stop = day boundary.
Sizing 1R via S2's live floor, exactly as CAND-0001."""

from __future__ import annotations

import math
from dataclasses import dataclass

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.vendor_bridge import (
    Block,
    FVGKind,
    LevelKind,
    atr14,
    compute_prior_day_levels,
    detect_fvg_reactions,
    detect_fvgs,
    detect_level_touches,
    min_executable_risk,
    sessions,
)
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.types import LiveTickReader, PdhPdlAuditEntry, PdhPdlAuditKind
from ai_trader.signal_engine.types import Direction

STRATEGY_ID = "S9002"
"""CAND-0007, next in the reserved S9xxx infra range after CAND-0001's `S9001`."""
MAGIC_NUMBER = 100_002


class LevelFvgConfluenceRecognitionRule:
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
        """The `LevelKind` (PDH/PDL) `last_trigger()` touched -- for the cross-policy exclusion check
        (`multi_policy_live.exclusion`), which needs the STRUCTURAL level, not an inferred direction
        (this policy's own direction<->level mapping matches CAND-0001's: PDL touch -> long, PDH -> short)."""
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
        fvgs = detect_fvgs(self._highs, self._lows, [block])
        fvg_reactions = detect_fvg_reactions(self._highs, self._lows, self._closes, fvgs, [block])

        fresh_touches = [t for t in level_touches if t.touch_idx == idx and t.touch_idx not in self._consumed_touch_idxs]
        fresh_ce50 = [r for r in fvg_reactions if r.ce50_touch_idx == idx]
        if not fresh_touches or not fresh_ce50:
            return None

        match = None
        for touch in fresh_touches:
            for reaction in fresh_ce50:
                if touch.level.kind is LevelKind.PDL and reaction.kind is FVGKind.BULLISH:
                    match = (touch, reaction, 1)
                    break
                if touch.level.kind is LevelKind.PDH and reaction.kind is FVGKind.BEARISH:
                    match = (touch, reaction, -1)
                    break
            if match is not None:
                break
        if match is None:
            self._consumed_touch_idxs.update(t.touch_idx for t in fresh_touches)
            self._no_trade(bar.ts_close, "NO_DIRECTION_ALIGNED_FVG_CONFLUENCE", touch_idx=idx)
            return None

        touch, reaction, direction = match
        self._consumed_touch_idxs.update(t.touch_idx for t in fresh_touches)

        fvg = next(
            (f for f in fvgs if f.formed_idx == reaction.formed_idx and f.kind is reaction.kind
             and f.block_index == reaction.block_index),
            None,
        )
        if fvg is None:
            self._no_trade(bar.ts_close, "FVG_NOT_FOUND_FOR_REACTION", touch_idx=idx)
            return None

        strategy_stop_price = min(self._lows[touch.touch_idx], fvg.lower) if direction > 0 else max(
            self._highs[touch.touch_idx], fvg.upper,
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
            session=session, magic_number=MAGIC_NUMBER, comment="CAND-0007 LEVEL-FVG-CONFLUENCE DEMO",
            as_of=bar.ts_close,
        )
