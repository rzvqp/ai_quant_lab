"""S5 Opening-Range Breakout LONG (mandate `AI-TRADER-S5-CANONICAL-ONBOARDING-001`).

**Identity, recovered mechanically, never reconstructed from a prompt** (full citation trail in
`AI_TRADER_S5_ONBOARDING_REPORT.md`):

- Alpha candidate: `C_2d587447`, representative `7472f3d412f2`.
- Frozen spec string (verbatim): `S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3}`
  (`ai_quant_lab/red_team/policy_reviews/RT_S5_S20_CLEAN_INDEPENDENT_VALIDATION_REPORT.md` section 2;
  identical in `ai_quant_lab/red_team/audit/LEDGER.md` entry [97]).
- Verdict: `INDEPENDENT_VALIDATION_PASS`, all gates A-H, `RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001`
  (E97, commit `633bd5da`), on the Statistician's frozen clean 52,572-bar population. Frozen trade
  ledger hash `cd4e8d4a...` (295 trades) -- see the onboarding report for why that ledger's raw rows are
  NOT available to this repository (off-git escrow), and what that means for `expected_edge` below.
- Engine: `code/mstrat.py`'s `s5_setups`/`simulate` (`ai_quant_lab` repo) -- the ONE shared backtester
  every S-family strategy runs through. Every formula below is copied from that function, not
  reconstructed from the RT report's prose alone.

**Mechanism (verbatim from `code/mstrat.py:273-291`, M15 timeframe throughout)**:
1. Session = NY, UTC hours `[13:00, 21:00)` (`code/mtf.py:37-38`: `hh<21` boundary combined with the
   `hh<13` London cutoff -- NY is the third `np.select` branch). 32 M15 bars per session.
2. Opening range = the FIRST 4 M15 bars of the session (`bar_in_session` 0-3, i.e. `13:00-13:59` UTC) --
   `or_high`/`or_low` = max(high)/min(low) over those 4 bars (`code/mtf.py:18-20`).
3. Entry window = `bar_in_session` 4 through 20 inclusive (`14:00-16:59` UTC) -- `mstrat.py:280`'s own
   `if ... bis[t]<4 or bis[t]>20: continue`.
4. Breakout trigger: bar `t`'s CLOSE > `or_high` (the `side=up` case; frozen representative is LONG-only,
   `mstrat.py:279`'s `up=(h['side']=='up')`, representative uses `side=up`).
5. Entry: next bar's open (`mstrat.py:282`, `ei=t+1`) -- this plugin reports the intent at the signal
   bar's own close (`intended_entry`), matching `TradeHypothesis.entry_type="MARKET"`/`eligible_entry_
   timestamp` = the signal bar's own close (the pipeline's next M15 cycle IS the next-bar-open moment).
6. Stop (representative `stop=or_opp`): `stop = or_low - 2*TICK` (`mstrat.py:283`), `TICK = 0.01` -- the
   RATIFIED value (`mstrat.py`'s own module constant ships a documented `TICK=0.1` 10x defect,
   `RT-CODE-A-0007`; Red Team overrode to `0.01` for the S5/S20 validation and this plugin uses that same
   ratified value, never the buggy one).
7. Target (`exit=rr3`): `target = entry + 3 * risk`, `risk = entry - stop` (`mstrat.py:_exitmap`+`simulate`
   line 59; independently confirmed in prose by `statistician/STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md`).
8. Max hold: 48 M15 bars (`mstrat.py:58`, `to=48` for non-`time` exit kinds) -- 12 hours; force-closes at
   entry+48 bars if neither stop nor target is hit.

**Deliberately NOT reproduced -- disclosed, not a silent omission**: `mstrat.simulate`'s own stop-FLOOR
widening (`max(2*spread_ticks*TICK, 5*TICK, 0.10*ATR)`, applied AFTER the raw `or_opp` stop above) is a
BACKTEST EXECUTION-REALISM detail of that specific research engine, not part of S5's own strategy-level
stop DEFINITION -- the architecture's own separation of concerns (`AI_TRADER_NEW_BRAIN_ARCHITECTURE.md`
section 9: "a strategy may propose a stop; it may never override risk policy") places any real-world
stop-distance/execution-realism adjustment downstream, in the Risk Engine
(`risk_manager_live.evaluate_trade_proposal`'s own "stop-distance validity" guard), not inside the
strategy plugin. This is a scope boundary, not a semantic change to S5's own SL/TP/RR numbers.

**`mode` is a label with no behavioral effect**: `S5_DIMS` includes `mode=['breakout','retest']`
(`mstrat.py:274`), but `h['mode']` is never read inside `s5_setups` -- confirmed both by direct code
reading and independently by the Statistician's own pre-RT disclosure
(`statistician/STAT_S5_INDEPENDENT_VALIDATION_PROTOCOL.md:35-38`: `mode=breakout` and `mode=retest` score
identically; the choice was sort-order, not behavior). This plugin therefore implements exactly ONE
breakout mechanism, matching the engine's actual code -- there is no separate "retest" logic to add
without inventing behavior the validated engine never had."""

from __future__ import annotations

import dataclasses

from ai_trader.live_signal_source.types import Bar
from ai_trader.new_brain_live.market_state import market_state_identity
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.signal_engine.types import Direction

STRATEGY_ID = "s5_c_2d587447_opening_range_breakout_long"
STRATEGY_VERSION = "rep_7472f3d412f2"

TICK = 0.01  # the RATIFIED value (RT-CODE-A-0007 override), never mstrat.py's own buggy module TICK=0.1
NY_SESSION_START_UTC_SECONDS = 13 * 3600
NY_SESSION_END_UTC_SECONDS = 21 * 3600
BAR_SECONDS_M15 = 900
OR_BAR_COUNT = 4  # bar_in_session 0..3
ENTRY_WINDOW_FIRST_BIS = 4
ENTRY_WINDOW_LAST_BIS = 20  # inclusive -- mstrat.py's own "bis[t]<4 or bis[t]>20: continue"
MAX_HOLD_BARS = 48
RR_TARGET = 3.0

VALIDATION_PROVENANCE = (
    "Alpha candidate C_2d587447, representative 7472f3d412f2, frozen spec "
    "S5{session=ny, mode=breakout, side=up, stop=or_opp, exit=rr3} -- "
    "RT-ALPHA-S5-S20-CLEAN-INDEPENDENT-VALIDATION-001 (E97, ai_quant_lab commit 633bd5da), "
    "verdict INDEPENDENT_VALIDATION_PASS (gates A-H all PASS), frozen ledger sha256 "
    "cd4e8d4aae0104cd1041898cf136917b9ec3194c343ba6840fab0bdb7831e1d7 (295 trades), "
    "engine code/mstrat.py (s5_setups/simulate), TICK=0.01 ratified override (RT-CODE-A-0007). "
    "Statistician prep: statistician/STAT_S5_INDEPENDENT_VALIDATION_PROTOCOL.md + "
    "STAT_S5_S20_CLEAN_VALIDATION_FREEZE.md (freeze ed49c2c). "
    "CEO promotion authorization: AI-TRADER-S5-CANONICAL-ONBOARDING-001."
)
CONFIG_FINGERPRINT = (
    "S5-frozen-spec:session=ny,mode=breakout,side=up,stop=or_opp,exit=rr3;"
    "tick=0.01;or_bars=4;entry_window_bis=4-20;hold_bars=48;rr=3.0"
)
IMPLEMENTATION_FINGERPRINT = "s5_opening_range_breakout.py-impl-v1"
ROLLBACK_IDENTITY = "s5_opening_range_breakout-rollback-v1"


def _session_start_of(ts_close: int) -> int | None:
    """Returns the NY session's own start timestamp (the epoch second of that calendar day's 13:00 UTC)
    if `ts_close` falls within an NY session block, else `None`. `ts_close` is a bar's own CLOSE
    timestamp; the bar's session membership is judged by its close, matching `mtf.py`'s own convention
    (session assigned per-row from that row's own timestamp)."""
    day_start = (ts_close // 86400) * 86400
    seconds_into_day = ts_close - day_start
    if NY_SESSION_START_UTC_SECONDS <= seconds_into_day < NY_SESSION_END_UTC_SECONDS:
        return day_start + NY_SESSION_START_UTC_SECONDS
    return None


def _bar_in_session(ts_close: int, session_start: int) -> int:
    """0-indexed M15 bar position within the session block this bar's OWN close belongs to -- bar 0 is
    the first bar whose close falls in [session_start, session_start+900)."""
    return (ts_close - session_start) // BAR_SECONDS_M15


@dataclasses.dataclass
class S5OpeningRangeBreakoutLong:
    """Stateful by necessity: the opening range (bars 0-3's high/low) must be remembered across the
    entry-window bars (4-20) that follow it -- `MarketState` deliberately does not carry raw OHLC or
    session-relative bar position (see `market_state.py`'s own 'deliberately absent' section), so this
    strategy tracks its own OR state via `observe_bar`, fed the same real, closed M15 bars the M15
    context-refresh loop already processes (mirrors `RawAxesBuilder.observe(bar)`'s own established
    calling convention -- a future live-wiring step would call both on the same bar, in the same order,
    a decision explicitly deferred to a future, separate mandate per this mandate's own section 19).

    `evaluate()` itself only reads `MarketState` (for identity/timestamp/entry_price) plus this
    instance's own already-updated OR state -- never any other global/broker state."""

    strategy_id: str = STRATEGY_ID
    strategy_version: str = STRATEGY_VERSION
    _session_start: int | None = dataclasses.field(default=None, init=False, repr=False)
    _or_high: float | None = dataclasses.field(default=None, init=False, repr=False)
    _or_low: float | None = dataclasses.field(default=None, init=False, repr=False)

    def observe_bar(self, bar: Bar) -> None:
        """Called once per real, closed M15 bar, in bar-close order -- accumulates the opening range's
        high/low from bars 0-3 of each NY session. A bar outside any NY session, or outside the
        OR-forming window (`bar_in_session` 0-3), is observed (for session-boundary bookkeeping) but
        never changes `_or_high`/`_or_low`."""
        session_start = _session_start_of(bar.ts_close)
        if session_start is None:
            return
        if session_start != self._session_start:
            self._session_start = session_start
            self._or_high = None
            self._or_low = None
        bis = _bar_in_session(bar.ts_close, session_start)
        if bis < OR_BAR_COUNT:
            self._or_high = bar.high if self._or_high is None else max(self._or_high, bar.high)
            self._or_low = bar.low if self._or_low is None else min(self._or_low, bar.low)

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        if state.entry_price is None:
            return None  # MARKET_STATE_INVALID is the pipeline's own, earlier fail-closed gate

        session_start = _session_start_of(state.market_timestamp)
        if session_start is None or session_start != self._session_start:
            return None  # not in an NY session this strategy has observed the opening range for
        if self._or_high is None or self._or_low is None:
            return None  # opening range not yet formed (still bars 0-3, or never observed)
        bis = _bar_in_session(state.market_timestamp, session_start)
        if bis < ENTRY_WINDOW_FIRST_BIS or bis > ENTRY_WINDOW_LAST_BIS:
            return None  # outside the entry window -- faithful to mstrat.py's own bis<4 or bis>20 guard

        close = state.entry_price
        if not (close > self._or_high):  # side=up breakout trigger, mstrat.py's own cl[t]>orh[t]
            return None

        entry = close
        stop = self._or_low - 2 * TICK
        if not (stop < entry):
            return None  # geometrically invalid (OR collapsed to near-zero width) -- fail closed, no signal

        return TradeHypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            direction=Direction.LONG, signal_timestamp=state.market_timestamp,
            eligible_entry_timestamp=state.market_timestamp, entry_type="MARKET", intended_entry=entry,
            invalidation=stop, exit_specification=f"rr:{RR_TARGET}", max_hold=MAX_HOLD_BARS,
            expected_edge=None,  # see AI_TRADER_S5_ONBOARDING_REPORT.md -- the real n/n_target/n_horizon
            # breakdown is not accessible (frozen ledger is off-git escrow, hash-only); never invented.
            reason_codes=("S5_OPENING_RANGE_BREAKOUT",), market_state_identity=market_state_identity(state),
            strategy_config_fingerprint=CONFIG_FINGERPRINT, research_validation_identity=VALIDATION_PROVENANCE,
            provenance="s5_opening_range_breakout.py",
        )


def catalog_entry_for_s5(strategy: S5OpeningRangeBreakoutLong, *, enabled: bool = True) -> CatalogEntry:
    return CatalogEntry(
        strategy_id=strategy.strategy_id, strategy_version=strategy.strategy_version,
        status=StrategyStatus.VALIDATED, enabled=enabled, allowed_instruments=("XAUUSD",),
        allowed_directions=("LONG",), context_eligibility=None,  # session-gated internally, not regime-gated
        implementation_fingerprint=IMPLEMENTATION_FINGERPRINT, config_fingerprint=CONFIG_FINGERPRINT,
        validation_provenance=VALIDATION_PROVENANCE, risk_contract_reference="risk_manager_live-v1",
        rollback_identity=ROLLBACK_IDENTITY, strategy=strategy,
    )
