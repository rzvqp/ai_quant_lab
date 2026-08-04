"""`LevelBreakDriveRecognitionRule` -- CAND-0009 `LEVEL-BREAK-DRIVE`, built so it CAN be activated (CEO
instruction, 2026-08-04: "Construieste-l ca sa poata fi activat, dar nu il porni"). Wired into the shared
entrypoint's policy registry with its persisted pause flag defaulting to DISABLED -- flipping it on later
needs no rebuild. **Not started by this change.**

**Part A** (`POLICY_LEVEL_BREAK_DRIVE_v1.md`, unchanged): same-bar confluence of a PDH/PDL touch
(`detect_level_touches`) AND a displacement bar (`expansion[i]==True`) whose OWN bar direction is
THROUGH the level -- PDH touched with a bullish bar (`close[i]>open[i]`) -> long (break up); PDL touched
with a bearish bar -> short (break down). Directionally opposite CAND-0001 on the exact same touch
primitive: a PDH/PDL touch WITHOUT a coincident displacement is CAND-0001's own reversal case, excluded
here by construction (the `expansion[i]==True` requirement).

**Part B** (`POLICY_LEVEL_BREAK_DRIVE_v3.md`, DEMO_BASELINE, live-valid horizon): stop = the broken level
itself (`touch.level.price`, not the touch-bar extreme -- a break-and-drive falsifies when price returns
through the flipped level). Exit = the first OPPOSING-direction expansion bar after entry, OR a
14-bar (`ATR_WINDOW`) time-stop from entry -- checked live, bar by bar, via this policy's OWN
`MechanicalCloseCheck` (`multi_policy_live.orchestration.opposing_expansion_or_time_stop_close`), NOT
the day-boundary check the other three policies share (CAND-0009 is a continuation trade, not bounded by
the day the level was defined for).

**Disclosed engine-interface note**: the frozen `demo_gate_engine`'s `DemoSignal` requires a
`target_price` field (its own generic stop/target/day_end_idx model), but CAND-0009 structurally has NO
price target -- only a broken-level stop and two time/event-based exits. The post-hoc audit call
(never a live decision input) passes a SENTINEL `target_price`, placed far beyond the observed high/low
range of the audited window so it can never be the leg that resolves the trade, and the audit detail is
marked `target_price_is_sentinel` so no reader mistakes it for a real level. The LIVE mechanical close
(what actually protects/closes the position) never uses this sentinel -- it is audit-record plumbing
only, disclosed rather than silently presented as a real target."""

from __future__ import annotations

import math

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.multi_policy_live.vendor_bridge import (
    ATR_WINDOW,
    Block,
    LevelKind,
    atr14,
    compute_prior_day_levels,
    detect_level_touches,
    expansion,
    min_executable_risk,
    sessions,
)
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.recognition_rule import PdhPdlTrigger
from ai_trader.pdh_pdl_demo.types import LiveTickReader, PdhPdlAuditEntry, PdhPdlAuditKind
from ai_trader.signal_engine.types import Direction

STRATEGY_ID = "S9003"
MAGIC_NUMBER = 100_003


class LevelBreakDriveRecognitionRule:
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
        """The `LevelKind` this policy's own trigger broke -- exposed for the cross-policy exclusion
        check against CAND-0001 (`multi_policy_live.exclusion`)."""
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
        expansion_mask = expansion(self._opens, self._highs, self._lows, self._closes)

        fresh_touches = [t for t in level_touches if t.touch_idx == idx and t.touch_idx not in self._consumed_touch_idxs]
        if not fresh_touches:
            return None
        self._consumed_touch_idxs.update(t.touch_idx for t in fresh_touches)

        if not expansion_mask[idx]:
            self._no_trade(bar.ts_close, "NO_COINCIDENT_DISPLACEMENT", touch_idx=idx)
            return None
        bar_is_bullish = self._closes[idx] > self._opens[idx]

        touch = fresh_touches[0]
        if len(fresh_touches) > 1:
            for skipped in fresh_touches[1:]:
                self._no_trade(
                    bar.ts_close, "SAME_BAR_MULTIPLE_TOUCHES_ONLY_FIRST_PROCESSED",
                    touch_idx=int(skipped.touch_idx), level_kind=skipped.level.kind.value,
                )

        if touch.level.kind is LevelKind.PDH and bar_is_bullish:
            direction = 1
        elif touch.level.kind is LevelKind.PDL and not bar_is_bullish:
            direction = -1
        else:
            # PDH+bearish or PDL+bullish = a REJECTION, not a break -- CAND-0001's own thesis, excluded.
            self._no_trade(
                bar.ts_close, "DISPLACEMENT_DIRECTION_NOT_THROUGH_LEVEL", touch_idx=idx,
                level_kind=touch.level.kind.value,
            )
            return None

        strategy_stop_price = touch.level.price

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

        # Validity guard (Part A): no trade if entry is already back through the broken level.
        if (direction > 0 and reference_price <= strategy_stop_price) or (
            direction < 0 and reference_price >= strategy_stop_price
        ):
            self._no_trade(bar.ts_close, "NO_TRADE_ENTRY_BACK_THROUGH_LEVEL", touch_idx=idx)
            return None

        self._last_level_kind = touch.level.kind
        self._last_trigger = PdhPdlTrigger(
            touch_idx=idx, entry_idx=idx + 1, direction=direction,
            strategy_stop_price=float(strategy_stop_price),
            target_price=float(strategy_stop_price),  # placeholder -- this policy has no real target;
            # PolicyOrchestrator's own post-hoc audit call overwrites this with a disclosed sentinel
            # before calling the frozen engine (see module docstring). Never used live.
            atr_at_touch=float(atr_at_touch), day_boundary_label=self._day_index[idx],
            effective_spread=float(effective_spread), executable_stop_price=float(executable_stop_price),
            tick_size=self._tick_size,
        )
        session = str(sessions([bar.ts_open])[0])
        return LiveCandidate(
            strategy_id=STRATEGY_ID, symbol=self._symbol,
            direction=Direction.LONG if direction > 0 else Direction.SHORT,
            entry=float(reference_price), stop=float(executable_stop_price), target=float(strategy_stop_price),
            session=session, magic_number=MAGIC_NUMBER, comment="CAND-0009 LEVEL-BREAK-DRIVE DEMO",
            as_of=bar.ts_close,
        )


def sentinel_target_price(pending: object, arrays: tuple[list[float], list[float], list[float], list[float]]) -> float:
    """`PolicyOrchestrator`'s own `target_price_for_audit` hook for CAND-0009 (see module docstring's
    "Disclosed engine-interface note") -- a target far beyond the audited window's own observed
    high/low range, in the position's own direction, so the frozen engine's target leg can never be
    the one that resolves the trade. Computed from REAL data (the day's own range), not an arbitrary
    constant, so it scales sanely with volatility; still never a real price level."""
    from ai_trader.pdh_pdl_demo.types import PendingPdhPdlTrade

    assert isinstance(pending, PendingPdhPdlTrade)
    _, high, low, _ = arrays
    window_high = max(high[pending.entry_idx:]) if high[pending.entry_idx:] else high[-1]
    window_low = min(low[pending.entry_idx:]) if low[pending.entry_idx:] else low[-1]
    span = max(window_high - window_low, pending.atr_at_touch, 1.0)
    return window_high + span * 1000.0 if pending.direction > 0 else window_low - span * 1000.0


def opposing_expansion_or_time_stop_close(
    pending: object, bar_idx: int, day_boundary_label: int, arrays: tuple[list[float], list[float], list[float], list[float]] | None,
) -> str | None:
    """CAND-0009's own `MechanicalCloseCheck` (`multi_policy_live.orchestration.MechanicalCloseCheck`):
    close on the first OPPOSING-direction expansion bar after entry, or a 14-bar (`ATR_WINDOW`)
    time-stop from entry -- whichever comes first. `pending` is typed `object` here only to avoid an
    import cycle with `orchestration.py`; callers always pass a `PendingPdhPdlTrade`."""
    from ai_trader.pdh_pdl_demo.types import PendingPdhPdlTrade

    assert isinstance(pending, PendingPdhPdlTrade)
    if arrays is None:
        return None
    open_, high, low, close = arrays
    if bar_idx < pending.entry_idx:
        return None

    if bar_idx - pending.entry_idx >= ATR_WINDOW:
        return "TIME_STOP"

    expansion_mask = expansion(open_, high, low, close)
    if bar_idx < len(expansion_mask) and expansion_mask[bar_idx]:
        bar_is_bullish = close[bar_idx] > open_[bar_idx]
        # Opposing = the OPPOSITE bar direction from this position's own entry direction.
        if pending.direction > 0 and not bar_is_bullish:
            return "OPPOSING_EXPANSION"
        if pending.direction < 0 and bar_is_bullish:
            return "OPPOSING_EXPANSION"
    return None
