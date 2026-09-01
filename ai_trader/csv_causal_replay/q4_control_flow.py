"""Q4 resume-runtime control flow (CEO mandate: durable freeze of the Q4 control-flow fix).

**The bug this remediates**: a session-local Q4 runner evaluated P007 gate signals BEFORE its
open-trade monitoring block, so a bar carrying both an open position and a fresh P007 candidate had
its SL/TP/MAX_HOLD/MGMT-004 check skipped by the `break` the P007 branch took. A read-only audit of
the one real occurrence (TRADE #7, bar 1624) found the trade's actual stop/target were untouched on
that bar (manually re-verified against the sealed fixture) -- the real Q4 record was undamaged -- but
the control-flow defect itself needed removing before further replay, not merely working around it
bar-by-bar. This module is that removal, persisted durably so the runtime and its regression tests
share one implementation rather than a scratchpad copy neither is provably identical to.

**Ordering invariant (mandate section 3), the whole point of this module**: for every revealed Q4
bar, unconditionally:
  A. session/opening-range bookkeeping (`S5ORState.observe`)
  B. IF a position was open at the start of the bar: `check_trade_mechanics` -- SL, TP, MAX_HOLD,
     MGMT-004, position close/persistence. Runs regardless of whether a P007 candidate also fired on
     this same bar; this is pure bookkeeping on the caller-owned `open_trade` dict, entirely
     independent of what the caller ultimately commits to the causal engine for this bar.
  C. P007 reasoning requirement (surfaced via `decide()`'s return value, never silently resolved here)
  D. S5 eligibility/signal check (`S5ORState.check_trigger`) where applicable

`decide()` is the single decision function -- both the real runtime (a session-local orchestration
script, not committed, since it is specific to this Q4 replay task and carries session-local file
paths) and this module's own test suite (`tests/test_q4_control_flow.py`) call it, so there is no
parallel reimplementation of the ordering invariant to drift out of sync.

**Explicitly NOT changed by this module**: S5's frozen entry/stop/target formulas, P007's frozen
definition, MGMT-004's frozen trigger/action, `engine.py`, `p007_detector.py`, `p007_gate.py`,
`q4_replay_step.py`, or the canonical `reveal_next_bar_with_p007_gate()` reveal path -- this module
sits entirely downstream of that reveal, deciding only what a caller who already has a
`WiredRevealResult` should do next.
"""

from __future__ import annotations

from typing import Any, Literal

from ai_trader.csv_causal_replay.types import Bar

TICK = 0.01
NY_SESSION_START_UTC_SECONDS = 13 * 3600
NY_SESSION_END_UTC_SECONDS = 21 * 3600
BAR_SECONDS_M15 = 900
OR_BAR_COUNT = 4
ENTRY_WINDOW_FIRST_BIS = 4
ENTRY_WINDOW_LAST_BIS = 20
RR_TARGET = 3.0
"""Redeclared verbatim from `ai_trader/new_brain_live/strategy_platform/s5_opening_range_breakout.py`
(mandate section 6: no strategy-semantics changes) -- this module never imports that one directly
(it transitively pulls in `live_signal_source` -> `fastjsonschema`, not installed here; see that
module's own docstring), matching the "redeclare, don't import" precedent `types.py` already sets
in this same package."""


def session_start_of(ts_close: int) -> int | None:
    """Verbatim port of `s5_opening_range_breakout.py::_session_start_of` -- session membership is
    judged by a bar's own CLOSE, not its open."""
    day_start = (ts_close // 86400) * 86400
    seconds_into_day = ts_close - day_start
    if NY_SESSION_START_UTC_SECONDS <= seconds_into_day < NY_SESSION_END_UTC_SECONDS:
        return day_start + NY_SESSION_START_UTC_SECONDS
    return None


def bar_in_session(ts_close: int, session_start: int) -> int:
    """Verbatim port of `s5_opening_range_breakout.py::_bar_in_session`."""
    return (ts_close - session_start) // BAR_SECONDS_M15


class S5ORState:
    """Session-local opening-range tracker, faithful to `S5OpeningRangeBreakoutLong`'s own
    `observe_bar`/`evaluate` logic (mandate section 6: exact existing strategy semantics unchanged).
    `observe()` has no P007 parameter and no P007-conditional branch at all -- this is what makes it
    structurally impossible for P007 handling to suppress OR bookkeeping, not merely a call-site
    discipline the caller has to remember."""

    def __init__(self) -> None:
        self.session_start: int | None = None
        self.or_high: float | None = None
        self.or_low: float | None = None

    def observe(self, ts_close: int, high: float, low: float) -> None:
        session_start = session_start_of(ts_close)
        if session_start is None:
            return
        if session_start != self.session_start:
            self.session_start = session_start
            self.or_high = None
            self.or_low = None
        bis = bar_in_session(ts_close, session_start)
        if bis < OR_BAR_COUNT:
            self.or_high = high if self.or_high is None else max(self.or_high, high)
            self.or_low = low if self.or_low is None else min(self.or_low, low)

    def check_trigger(self, ts_close: int, close: float) -> dict[str, Any] | None:
        session_start = session_start_of(ts_close)
        if session_start is None or session_start != self.session_start:
            return None
        if self.or_high is None or self.or_low is None:
            return None
        bis = bar_in_session(ts_close, session_start)
        if bis < ENTRY_WINDOW_FIRST_BIS or bis > ENTRY_WINDOW_LAST_BIS:
            return None
        if not (close > self.or_high):
            return None
        entry = close
        stop = self.or_low - 2 * TICK
        if not (stop < entry):
            return None
        risk = entry - stop
        target = entry + RR_TARGET * risk
        return {"entry": entry, "stop": stop, "target": target, "or_high": self.or_high, "or_low": self.or_low, "bis": bis}


def check_trade_mechanics(open_trade: dict[str, Any], bar_index: int, bar: Bar) -> str | None:
    """Mandate section 3.B -- ALWAYS called by the runtime when a position is open, regardless of
    P007 state. Pure bookkeeping: mutates `open_trade` in place (control/shadow stop-touch, target-
    touch, max-hold, MGMT-004 trigger), never touches the causal engine or any durable replay state.
    Returns 'CLOSE', 'MGMT004_TRIGGER', or None (nothing new resolved on this bar)."""
    action: str | None = None
    risk = open_trade["risk"]
    mgmt_trigger_price = open_trade["entry"] + 1.0 * risk
    if not open_trade["mgmt004_fired"] and bar.close >= mgmt_trigger_price:
        open_trade["mgmt004_fired"] = True
        open_trade["mgmt004_fire_bar"] = bar_index
        open_trade["shadow_stop"] = open_trade["entry"]
        action = "MGMT004_TRIGGER"

    if not open_trade["control_closed"]:
        if bar.low <= open_trade["control_stop"]:
            open_trade["control_closed"] = True
            open_trade["control_exit"] = {"bar_index": bar_index, "reason": "STOP", "price": open_trade["control_stop"]}
            action = "CLOSE"
        elif bar.high >= open_trade["target"]:
            open_trade["control_closed"] = True
            open_trade["control_exit"] = {"bar_index": bar_index, "reason": "TARGET", "price": open_trade["target"]}
            action = "CLOSE"
        elif bar_index >= open_trade["max_hold_last_bar"]:
            open_trade["control_closed"] = True
            open_trade["control_exit"] = {"bar_index": bar_index, "reason": "MAX_HOLD", "price": bar.close}
            action = "CLOSE"

    if open_trade["mgmt004_fired"] and not open_trade.get("shadow_closed"):
        if bar.low <= open_trade["shadow_stop"]:
            open_trade["shadow_closed"] = True
            open_trade["shadow_exit"] = {"bar_index": bar_index, "reason": "STOP", "price": open_trade["shadow_stop"]}
        elif bar.high >= open_trade["target"]:
            open_trade["shadow_closed"] = True
            open_trade["shadow_exit"] = {"bar_index": bar_index, "reason": "TARGET", "price": open_trade["target"]}
        elif bar_index >= open_trade["max_hold_last_bar"]:
            open_trade["shadow_closed"] = True
            open_trade["shadow_exit"] = {"bar_index": bar_index, "reason": "MAX_HOLD", "price": bar.close}

    return action


DecisionOutcome = Literal[
    "COMMIT_ROUTINE_TRADE_CLOSE", "COMMIT_MGMT004_TRIGGER", "STOP_FOR_P007_REASONING",
    "COMMIT_ROUTINE_TRADE_CONTINUES", "STOP_FOR_S5_TRADE_FREEZE", "COMMIT_ROUTINE_NO_EVENT",
]


def decide(
    *, open_trade: dict[str, Any] | None, trade_action: str | None, p007_event: bool,
    trigger: dict[str, Any] | None,
) -> tuple[DecisionOutcome, dict[str, Any]]:
    """THE single decision function (mandate section 2: "no parallel duplicate implementation") --
    both the Q4 runtime and `tests/test_q4_control_flow.py` call this exact function. Priority order
    matches mandate section 3/4 exactly: a trade needing to close this bar always wins the commit
    (a coincident P007 event is deferred, not dropped -- the gate re-detects it on the next reveal,
    same as any other re-flagged episode); MGMT-004 firing is next; only once trade mechanics have
    had first claim on this bar does P007 get to request a reasoning stop; S5 is checked only when no
    position is open (an open position's own bar-by-bar fate is already handled above it)."""
    if trade_action == "CLOSE":
        return "COMMIT_ROUTINE_TRADE_CLOSE", {"p007_deferred": p007_event}
    if trade_action == "MGMT004_TRIGGER":
        return "COMMIT_MGMT004_TRIGGER", {"p007_deferred": p007_event}
    if p007_event:
        return "STOP_FOR_P007_REASONING", {"trade_monitoring_already_executed": open_trade is not None}
    if open_trade is not None:
        return "COMMIT_ROUTINE_TRADE_CONTINUES", {}
    if trigger is not None:
        return "STOP_FOR_S5_TRADE_FREEZE", {}
    return "COMMIT_ROUTINE_NO_EVENT", {}
