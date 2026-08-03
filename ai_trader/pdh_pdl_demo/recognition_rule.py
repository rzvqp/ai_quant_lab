"""`PdhPdlRecognitionRule` -- replaces `ObservingNullRecognitionRule` for XAUUSD PDH-PDL DEMO ONLY
(CEO instruction, 2026-08-03: "care inlocuieste ObservingNullRecognitionRule doar pentru aceasta
politica, nu global"). Part A (CAND-0001, `POLICY_PDH_PDL_v2.md`, UNCHANGED from v1.2): PDH/PDL from
`institutional_levels.compute_prior_day_levels`, first-touch trigger from `detect_level_touches` --
both ratified primitives, reused verbatim, never reimplemented.

**Recompute-from-scratch, single continuous block** -- same pattern `structural_observer` already
established: day boundaries come from `day_index.day_boundary_start_utc`, numerically verified against
`resample_ny.py` (0 mismatches / 83,279 real bars, 7+ DST transitions).

**S2's floor computed HERE, live** (CEO: "S2, podeaua de risc, se aplica INAINTE de trimitere, din
spread-ul real citit atunci. Aceea e singura parte care trebuie live.") -- via the FROZEN engine's own
`min_executable_risk`, called early rather than re-derived; never S1 or S3, which are audit-only,
computed post-hoc by the engine itself (`orchestration.py`).

**Dual entry-price concept, disclosed**: the live `executable_stop_price` sent to the broker uses the
CURRENT live tick as the entry-price proxy (the actual next-open isn't known yet at trigger time -- the
touch bar has JUST closed). The frozen engine's own POST-HOC audit independently recomputes
`strategy_stop_distance`/`executable_stop_distance` from `open_[entry_idx]` (the bar's own recorded
open, once available) -- the two may differ slightly (live tick vs. recorded bar open, ~0-900s apart).
Both are journaled; this is an intrinsic, disclosed consequence of "enter live, audit from bars after
the fact," not a bug.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ai_trader.live_signal_source.types import Bar, LiveCandidate
from ai_trader.pdh_pdl_demo.day_index import day_boundary_start_utc
from ai_trader.pdh_pdl_demo.journal import PdhPdlAuditJournal
from ai_trader.pdh_pdl_demo.types import LiveTickReader, PdhPdlAuditEntry, PdhPdlAuditKind
from ai_trader.pdh_pdl_demo.vendor_bridge import (
    Block,
    LevelKind,
    atr14,
    compute_prior_day_levels,
    detect_level_touches,
    min_executable_risk,
    sessions,
)
from ai_trader.signal_engine.types import Direction

STRATEGY_ID = "S9001"
"""`ORDER_SCHEMA.json` requires `^S\\d+$` (confirmed empirically -- a plain "CAND0001" is REJECTED by
the order manager's own schema validation, `data.strategy_id must match pattern ^S\\d+$`). `S9001` is a
disclosed, reserved-looking infra id for THIS policy specifically -- distinct from the research S1-S43
family strategies and from Phase 10 BTCUSD's own `S999` infra-test id, never a real registered
research strategy."""
MAGIC_NUMBER = 100_001
"""Distinct from Phase 10 BTCUSD's own `900010` and the execution_orchestrator test fixtures' default
`900001` -- a fixed, disclosed, policy-level identifier (not derived per-order)."""


@dataclass(frozen=True, slots=True)
class PdhPdlTrigger:
    """Everything the orchestration layer needs beyond the bare `LiveCandidate` -- read via
    `PdhPdlRecognitionRule.last_trigger()` immediately after an `evaluate()` call that returned
    non-`None` (the `RecognitionRule` Protocol itself only returns `LiveCandidate`)."""

    touch_idx: int
    entry_idx: int
    direction: int  # +1 long (PDL), -1 short (PDH) -- DemoSignal's own convention
    strategy_stop_price: float
    target_price: float
    atr_at_touch: float
    day_boundary_label: int
    effective_spread: float
    executable_stop_price: float
    tick_size: float


class PdhPdlRecognitionRule:
    def __init__(
        self, symbol: str, tick_size: float, tick_reader: LiveTickReader, audit_journal: PdhPdlAuditJournal,
    ) -> None:
        self._symbol = symbol
        self._tick_size = tick_size
        self._tick_reader = tick_reader
        self._audit = audit_journal
        self._times: list[int] = []
        self._opens: list[float] = []
        self._highs: list[float] = []
        self._lows: list[float] = []
        self._closes: list[float] = []
        self._day_index: list[int] = []
        self._consumed_touch_idxs: set[int] = set()
        self._last_trigger: PdhPdlTrigger | None = None

    def last_trigger(self) -> PdhPdlTrigger | None:
        return self._last_trigger

    @property
    def current_bar_count(self) -> int:
        """The number of bars processed so far -- the SAME index space `PdhPdlTrigger.touch_idx`/
        `.entry_idx` and `PendingPdhPdlTrade.entry_idx`/`.day_end_idx` refer to. The orchestration
        layer's own per-bar bookkeeping (`PdhPdlOrchestrator.observe_bar`) must stay synchronized to
        this exact count -- both this rule and the orchestrator index into the SAME conceptual bar
        sequence, one bar behind (this count) or in front (an index already recorded)."""
        return len(self._closes)

    @property
    def current_arrays(self) -> tuple[list[float], list[float], list[float], list[float]]:
        """`(open, high, low, close)` -- the full accumulated arrays, for `PdhPdlOrchestrator.run_post_hoc_audit`,
        which needs the complete day's bars to call the frozen engine. Returns the LIVE lists
        themselves (not copies) -- read-only usage expected; the caller must not mutate them."""
        return self._opens, self._highs, self._lows, self._closes

    def _no_trade(self, as_of: int, reason_code: str, **extra: object) -> None:
        self._audit.record(PdhPdlAuditEntry(
            symbol=self._symbol, as_of=as_of, kind=PdhPdlAuditKind.NO_TRADE,
            detail={"reason_code": reason_code, **extra},
        ))

    def evaluate(self, bar: Bar) -> LiveCandidate | None:
        self._last_trigger = None
        idx = len(self._closes)
        self._times.append(bar.ts_open)
        self._opens.append(bar.open)
        self._highs.append(bar.high)
        self._lows.append(bar.low)
        self._closes.append(bar.close)
        self._day_index.append(day_boundary_start_utc(bar.ts_open))

        block = Block(0, len(self._closes))
        levels = compute_prior_day_levels(self._highs, self._lows, self._day_index, [block])
        touches = detect_level_touches(self._highs, self._lows, levels, self._day_index, [block])

        fresh = [t for t in touches if t.touch_idx == idx and t.touch_idx not in self._consumed_touch_idxs]
        if not fresh:
            return None
        if len(fresh) > 1:
            # Both PDH and PDL touched on the SAME bar -- a genuine, disclosed limitation:
            # RecognitionRule.evaluate() returns at most one candidate per call (Protocol shape, not
            # this rule's own choice). Process the first (compute_prior_day_levels' own PDH-then-PDL
            # emission order), journal the rest as explicitly skipped rather than silently dropping them.
            for skipped in fresh[1:]:
                self._consumed_touch_idxs.add(skipped.touch_idx)
                self._no_trade(
                    bar.ts_close, "SAME_BAR_MULTIPLE_TOUCHES_ONLY_FIRST_PROCESSED",
                    touch_idx=int(skipped.touch_idx), level_kind=skipped.level.kind.value,
                )
        touch = fresh[0]
        self._consumed_touch_idxs.add(touch.touch_idx)

        direction = -1 if touch.level.kind is LevelKind.PDH else 1
        strategy_stop_price = self._highs[touch.touch_idx] if direction < 0 else self._lows[touch.touch_idx]
        opposite_kind = LevelKind.PDL if touch.level.kind is LevelKind.PDH else LevelKind.PDH
        target_level = next(
            (lv for lv in levels if lv.kind is opposite_kind and lv.available_idx == touch.level.available_idx
             and lv.block_index == touch.level.block_index),
            None,
        )
        if target_level is None:
            # Structurally impossible -- compute_prior_day_levels always emits PDH+PDL together for
            # every day pair. Defensive, fail-closed, journaled rather than silently assumed away.
            self._no_trade(bar.ts_close, "OPPOSITE_LEVEL_NOT_FOUND", touch_idx=int(touch.touch_idx))
            return None
        target_price = target_level.price

        atr_array = atr14(self._highs, self._lows, self._closes)
        atr_at_touch = atr_array[touch.touch_idx]
        if atr_at_touch is None or math.isnan(float(atr_at_touch)):
            self._no_trade(bar.ts_close, "ATR_NOT_AVAILABLE_AT_TOUCH", touch_idx=int(touch.touch_idx))
            return None

        tick = self._tick_reader.read(self._symbol)
        if tick is None:
            self._no_trade(bar.ts_close, "LIVE_TICK_UNAVAILABLE", touch_idx=int(touch.touch_idx))
            return None
        effective_spread = tick.ask - tick.bid
        reference_price = tick.bid if direction < 0 else tick.ask

        min_exec = min_executable_risk(effective_spread, self._tick_size, float(atr_at_touch))
        strategy_stop_distance = abs(reference_price - strategy_stop_price)
        executable_stop_distance = max(strategy_stop_distance, min_exec)
        if executable_stop_distance <= 0:
            self._no_trade(
                bar.ts_close, "ZERO_OR_NEGATIVE_RISK_AT_LIVE_QUOTE", touch_idx=int(touch.touch_idx),
                executable_stop_distance=executable_stop_distance,
            )
            return None
        executable_stop_price = reference_price - direction * executable_stop_distance

        # Part B's own validity guards (POLICY_PDH_PDL_v2.md) -- structural, no lookahead, applied here
        # against the LIVE reference price exactly as the frozen engine applies them against open_[ei]:
        # entry already beyond the structural stop, or already beyond the target -> NO_TRADE.
        if (direction > 0 and reference_price <= strategy_stop_price) or (
            direction < 0 and reference_price >= strategy_stop_price
        ):
            self._no_trade(bar.ts_close, "NO_TRADE_ENTRY_BEYOND_STRUCTURAL_STOP", touch_idx=int(touch.touch_idx))
            return None
        if (direction > 0 and reference_price >= target_price) or (direction < 0 and reference_price <= target_price):
            self._no_trade(bar.ts_close, "NO_TRADE_ENTRY_BEYOND_TARGET", touch_idx=int(touch.touch_idx))
            return None

        self._last_trigger = PdhPdlTrigger(
            touch_idx=int(touch.touch_idx), entry_idx=int(touch.touch_idx) + 1, direction=direction,
            strategy_stop_price=float(strategy_stop_price), target_price=float(target_price),
            atr_at_touch=float(atr_at_touch), day_boundary_label=self._day_index[touch.touch_idx],
            effective_spread=float(effective_spread), executable_stop_price=float(executable_stop_price),
            tick_size=self._tick_size,
        )
        session = str(sessions([bar.ts_open])[0])
        return LiveCandidate(
            strategy_id=STRATEGY_ID, symbol=self._symbol,
            direction=Direction.LONG if direction > 0 else Direction.SHORT,
            entry=float(reference_price), stop=float(executable_stop_price), target=float(target_price),
            session=session, magic_number=MAGIC_NUMBER, comment="CAND-0001 PDH-PDL DEMO",
            as_of=bar.ts_close,
        )
