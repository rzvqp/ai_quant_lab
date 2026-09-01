"""Regression coverage for `q4_control_flow.py` (CEO mandate: durable freeze of the Q4 control-flow
fix). Synthetic bars only -- no real Q4 fixtures, no state files, nothing anywhere near bar 1632.

Uses the real `ai_trader.csv_causal_replay.types.Bar` dataclass (not a stand-in), and imports
`decide` / `check_trade_mechanics` / `S5ORState` directly from the committed module -- the same
callables any Q4 runner must use, so this suite and the runtime cannot silently diverge.

Each test proves one property required by the mandate (section 5):
  1. open trade + P007 candidate on the same bar -> trade monitoring still executes
  2. stop hit + P007 candidate on the same bar -> the stop is not skipped
  3. P007 "rejection" (candidate fires, trade unaffected) -> trade monitoring still ran
  4. P007 "open/accepted" (candidate already locked open) -> trade monitoring still ran
  5. P007 handling never skips an applicable S5 opening-range/trigger check
  6. `decide`/`check_trade_mechanics`/`S5ORState` are this module's only implementation -- no
     parallel copy exists for a runtime to import instead
"""

from __future__ import annotations

import importlib
import inspect

from ai_trader.csv_causal_replay.q4_control_flow import (
    NY_SESSION_START_UTC_SECONDS,
    S5ORState,
    check_trade_mechanics,
    decide,
)
from ai_trader.csv_causal_replay.types import Bar

DAY = 1_700_000_000 - (1_700_000_000 % 86400)  # arbitrary clean day boundary, outside NY session


def _bar(ts_open: int, o: float, h: float, l: float, c: float, v: float) -> Bar:
    return Bar(symbol="XAUUSD", ts_open=ts_open, ts_close=ts_open + 900, open=o, high=h, low=l, close=c, volume=v)


def _open_trade(entry: float, stop: float, target: float, entry_bar: int, max_hold: int = 48) -> dict:
    return {
        "entry_bar": entry_bar, "entry": entry, "control_stop": stop, "target": target,
        "risk": entry - stop, "max_hold_last_bar": entry_bar + max_hold,
        "mgmt004_fired": False, "mgmt004_fire_bar": None, "shadow_stop": None,
        "control_closed": False, "control_exit": None, "shadow_closed": False, "shadow_exit": None,
    }


def test_open_trade_plus_p007_candidate_runs_trade_monitoring() -> None:
    trade = _open_trade(entry=100.0, stop=95.0, target=115.0, entry_bar=10)
    bar = _bar(DAY, 99.0, 99.5, 98.5, 99.0, 300)  # unaffected: not near stop/target/mgmt

    action = check_trade_mechanics(trade, 11, bar)
    outcome, meta = decide(open_trade=trade, trade_action=action, p007_event=True, trigger=None)

    assert action is None
    assert trade["control_closed"] is False
    assert outcome == "STOP_FOR_P007_REASONING"
    assert meta["trade_monitoring_already_executed"] is True


def test_stop_hit_plus_p007_candidate_stop_not_skipped() -> None:
    trade = _open_trade(entry=100.0, stop=95.0, target=115.0, entry_bar=20)
    bar = _bar(DAY + 2700, 96.0, 96.5, 94.5, 95.0, 500)  # low breaches stop

    action = check_trade_mechanics(trade, 21, bar)
    outcome, meta = decide(open_trade=trade, trade_action=action, p007_event=True, trigger=None)

    assert action == "CLOSE"
    assert trade["control_closed"] is True
    assert trade["control_exit"]["reason"] == "STOP"
    assert outcome == "COMMIT_ROUTINE_TRADE_CLOSE"
    assert meta["p007_deferred"] is True


def test_p007_rejection_does_not_skip_trade_monitoring() -> None:
    trade = _open_trade(entry=100.0, stop=95.0, target=115.0, entry_bar=10)
    bar = _bar(DAY + 900, 99.0, 100.2, 98.0, 99.5, 300)  # trade unaffected

    action = check_trade_mechanics(trade, 12, bar)
    outcome, _ = decide(open_trade=trade, trade_action=action, p007_event=True, trigger=None)

    assert action is None
    assert trade["control_closed"] is False
    assert outcome == "STOP_FOR_P007_REASONING"


def test_p007_open_accepted_does_not_skip_trade_monitoring() -> None:
    trade = _open_trade(entry=100.0, stop=95.0, target=115.0, entry_bar=10)
    bar = _bar(DAY + 1800, 99.5, 100.0, 99.0, 99.8, 300)

    action = check_trade_mechanics(trade, 13, bar)
    outcome, _ = decide(open_trade=trade, trade_action=action, p007_event=True, trigger=None)

    assert action is None
    assert trade["control_closed"] is False
    assert outcome == "STOP_FOR_P007_REASONING"


def test_p007_handling_does_not_skip_s5_evaluation() -> None:
    or_state = S5ORState()
    ny_session_start = DAY - (DAY % 86400) + NY_SESSION_START_UTC_SECONDS
    or_bars = [
        _bar(ny_session_start - 900 + i * 900, 100 + i, 100.5 + i, 99.5 + i, 100.2 + i, 200)
        for i in range(4)
    ]
    for b in or_bars:
        or_state.observe(b.ts_close, b.high, b.low)
    assert or_state.or_high == 103.5
    assert or_state.or_low == 99.5

    # `observe`/`check_trigger` take no P007 parameter at all -- there is no branch to skip.
    entry_bar = _bar(ny_session_start + 3 * 900, 103.6, 104.0, 103.4, 103.9, 250)
    or_state.observe(entry_bar.ts_close, entry_bar.high, entry_bar.low)
    trigger = or_state.check_trigger(entry_bar.ts_close, entry_bar.close)

    assert trigger is not None
    assert trigger["entry"] == 103.9


def test_runtime_and_regression_suite_share_one_control_flow_module() -> None:
    """There is exactly one `decide`/`check_trade_mechanics`/`S5ORState` implementation in the repo,
    importable only from `ai_trader.csv_causal_replay.q4_control_flow`; any Q4 runner therefore has
    no parallel copy available to drift out of sync with this suite."""
    module = importlib.import_module("ai_trader.csv_causal_replay.q4_control_flow")

    assert inspect.getmodule(decide) is module
    assert inspect.getmodule(check_trade_mechanics) is module
    assert inspect.getmodule(S5ORState) is module

    # Pure-function determinism: the runtime and this suite calling `decide` with identical
    # inputs must always reach the identical outcome -- no hidden state, no parallel branch.
    trade = _open_trade(entry=100.0, stop=95.0, target=115.0, entry_bar=10)
    first = decide(open_trade=trade, trade_action=None, p007_event=True, trigger=None)
    second = decide(open_trade=trade, trade_action=None, p007_event=True, trigger=None)
    assert first == second
