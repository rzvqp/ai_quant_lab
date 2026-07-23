"""Unit tests for :class:`~ai_trader.shadow_evidence.engine.ShadowEvidenceEngine` -- Phase 6.10
Implementation Checkpoints 1B (risk-eligibility tap) + 1C (full virtual position lifecycle). Fast,
isolated tests using this project's own established fixture convention
(``scoring_engine.tests.fixtures.fake_strategy_manager.make_signal`` + the real
``score_signal_stage1``/``assembler`` pipeline, same technique ``scoring_engine/tests/test_validator.
py::_score()`` already uses) to build genuine, schema-valid ``OpportunityScore`` objects, plus
hand-constructed ``Bar`` fixtures to drive the shadow ``ExecutionSimulator`` deterministically (MARKET
orders always trigger regardless of price level, ``execution_simulator.py::_would_trigger``) --
without needing a full harness/real market data run. Complements the slower, full-harness integration
tests in ``ai_trader/simulation/tests/test_shadow_disabled_parity.py``.
"""

from __future__ import annotations

from ai_trader.execution_engine.types import BrokerCapabilities, MarketStatus, OrderType, TimeInForce
from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.risk_manager.types import RiskContext, SymbolRiskSnapshot
from ai_trader.scoring_engine import assembler
from ai_trader.scoring_engine.conflict import ConflictResult
from ai_trader.scoring_engine.config import ScoringConfig
from ai_trader.scoring_engine.pipeline import score_signal_stage1
from ai_trader.scoring_engine.tests.fixtures.fake_strategy_manager import make_signal
from ai_trader.scoring_engine.types import OpportunityScore, ScoreBatch
from ai_trader.shadow_evidence.engine import ShadowEvidenceEngine
from ai_trader.simulation.config import DateRange, FillModel, SimulationContext
from ai_trader.simulation.types import Bar, CloseAtEndPolicy, PartialFillPolicy

CONFIG = ScoringConfig()
AS_OF = 1_700_000_000
BAR_SECONDS = 900  # M15
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}
CAPABILITIES = BrokerCapabilities(
    supported_order_types=frozenset({
        OrderType.MARKET, OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT,
        OrderType.BRACKET, OrderType.OCO,
    }),
    supported_time_in_force=frozenset({TimeInForce.IOC, TimeInForce.FOK, TimeInForce.GTC, TimeInForce.DAY}),
    tick_size=0.01, lot_step=0.01, min_qty=0.01, max_qty=1_000_000.0,
    market_status={"XAUUSD": MarketStatus.OPEN},
)


def _score(strategy_id: str = "S10", **generate_kwargs: object) -> OpportunityScore:
    defaults: dict[str, object] = {
        "present": True, "direction": "LONG", "entry": 2000.0, "stop": 1990.0, "target": 2020.0,
        "strength": 0.8, "required_confirmations_met": True,
    }
    defaults.update(generate_kwargs)
    signal = make_signal(strategy_id=strategy_id, generate_signal_response=defaults)
    partial = score_signal_stage1(signal, None, {}, CONFIG)
    return assembler.assemble_score(partial, ConflictResult(0.0, ()), CONFIG)


def _batch(*scores: OpportunityScore, as_of: int = AS_OF) -> ScoreBatch:
    return ScoreBatch(
        as_of=as_of, symbol="XAUUSD", scores=tuple(scores),
        counts_by_recommendation={}, generated_at=as_of,
    )


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _risk_context(as_of: int = AS_OF) -> RiskContext:
    # A clean, filter-passing snapshot: atr/atr_rolling_median ratio 1.0 (within [0.25x, 4x]),
    # current_spread well under 3x the configured 0.10 reference_spread, liquidity_proxy well above
    # the configured 1.0 floor -- mirrors the "clean context passes filters" convention
    # risk_manager/tests/test_pipeline.py::test_clean_context_passes_filters already establishes.
    snapshot = SymbolRiskSnapshot(atr=1.0, atr_rolling_median=1.0, current_spread=0.05, liquidity_proxy=1000.0)
    return RiskContext(as_of=as_of, per_symbol={"XAUUSD": snapshot})


def _bar(as_of: int, price: float = 2000.0) -> dict[str, Bar]:
    return {
        "XAUUSD": Bar(
            symbol="XAUUSD", timeframe="M15", ts_open=as_of, ts_close=as_of + BAR_SECONDS,
            open=price, high=price, low=price, close=price, volume=100.0,
        )
    }


def _context(run_id: str) -> SimulationContext:
    return SimulationContext(
        run_id=run_id, date_range=DateRange(AS_OF - 10_000_000, AS_OF + 10_000_000),
        symbols=("XAUUSD",), timeframes=("M15",), starting_balance=2000.0, run_seed=1,
    )


def _engine(strategy_ids: frozenset[str], risk_config: RiskConfig | None = None, run_id: str = "T") -> ShadowEvidenceEngine:
    return ShadowEvidenceEngine(strategy_ids, risk_config or _risk_config(), _context(run_id), SYMBOL_META, CAPABILITIES)


# ------------------------------------------------------------------------------- generic tap (Checkpoint 1B)

def test_engine_ignores_scores_from_non_configured_strategies() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S39")), _risk_context())
    assert engine.opportunities == []
    assert engine.rejections == []


def test_engine_is_generic_over_multiple_configured_strategies() -> None:
    # Proves genericity directly: nothing in the engine names S10 specifically.
    engine = _engine(frozenset({"S10", "S21", "S39"}), RiskConfig())  # bare RiskConfig -> deterministic DENY
    batch = _batch(_score(strategy_id="S10"), _score(strategy_id="S21"), _score(strategy_id="S40"))
    engine.observe(AS_OF, batch, _risk_context())
    recorded_ids = {opp.strategy_id for opp in engine.opportunities}
    assert recorded_ids == {"S10", "S21"}  # S40 was never configured, correctly excluded


def test_engine_creates_a_rejection_record_only_when_denied() -> None:
    # A bare RiskConfig() (no configured reference_spread/liquidity_floor for XAUUSD) makes Risk
    # Manager's own fail-safe deny every opportunity (FILTER_SPREAD/FILTER_LIQUIDITY) -- documented
    # behavior of RiskManager itself, reused here to force a deterministic DENY.
    engine = _engine(frozenset({"S10"}), RiskConfig())
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(engine.opportunities) == 1
    assert engine.opportunities[0].shadow_risk_decision == "DENY"
    assert engine.opportunities[0].resulting_position_id is None
    assert len(engine.rejections) == 1
    assert engine.rejections[0].strategy_id == "S10"
    assert engine.rejections[0].denied_reason_code is not None


def test_account_for_reuses_the_same_shadow_account_instance_same_strategy() -> None:
    engine = _engine(frozenset({"S10"}))
    account_first = engine._account_for("S10", AS_OF)
    account_second = engine._account_for("S10", AS_OF + 900)
    assert account_first is account_second
    assert account_first.risk_manager is account_second.risk_manager
    assert account_first.execution_engine is account_second.execution_engine
    assert account_first.portfolio_simulator is account_second.portfolio_simulator


def test_account_for_uses_distinct_shadow_accounts_per_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    account_s10 = engine._account_for("S10", AS_OF)
    account_s21 = engine._account_for("S21", AS_OF)
    assert account_s10 is not account_s21
    assert account_s10.risk_manager is not account_s21.risk_manager
    assert account_s10.execution_engine is not account_s21.execution_engine
    assert account_s10.execution_simulator is not account_s21.execution_simulator
    assert account_s10.portfolio_simulator is not account_s21.portfolio_simulator


def test_engine_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))

    def _boom(self: ShadowEvidenceEngine, as_of: int, score: OpportunityScore, risk_context: RiskContext) -> None:
        raise RuntimeError("forced failure")

    original = ShadowEvidenceEngine._observe_one
    ShadowEvidenceEngine._observe_one = _boom  # type: ignore[method-assign]
    try:
        engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    finally:
        ShadowEvidenceEngine._observe_one = original  # type: ignore[method-assign]

    assert engine.opportunities == []
    assert len(engine.failures) == 2
    failed_ids = {sid for _as_of, sid, _err in engine.failures}
    assert failed_ids == {"S10", "S21"}

    # A strategy already marked degraded is skipped on a later bar without re-raising or re-recording.
    engine.observe(AS_OF + 900, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(engine.failures) == 2  # unchanged -- S10 was already degraded, silently skipped


# ------------------------------------------------------------------------------- virtual execution (Checkpoint 1C)

def test_allow_defers_the_opportunity_record_until_the_entry_fills() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    # entry_price (ShadowPositionRecord's own required field) is not known yet -- nothing published.
    assert engine.opportunities == []
    assert engine.positions == ()

    fill_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(fill_as_of, bar_index=1, bars=_bar(fill_as_of), phase_running=True)

    assert len(engine.opportunities) == 1
    opp = engine.opportunities[0]
    assert opp.strategy_id == "S10"
    assert opp.shadow_risk_decision == "ALLOW"
    assert opp.resulting_position_id is not None

    assert len(engine.positions) == 1
    position = engine.positions[0]
    assert position.position_id == opp.resulting_position_id
    assert position.status == "OPEN"
    assert position.entry_price == 2000.0
    assert position.strategy_id == "S10"
    assert position.n_legs == 0


def test_virtual_entry_client_order_id_carries_the_shadow_prefix() -> None:
    # Design §10 invariant 4 / §17.1 finding H3's required defense-in-depth.
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    account = engine._account_for("S10", AS_OF)
    pending = account.pending_entries["XAUUSD"]
    assert pending.client_order_id.startswith("SHADOW-CID-")
    assert "SHADOW-CID-" not in pending.client_order_id[len("SHADOW-CID-"):]


def test_virtual_position_closes_on_stop_loss_and_records_a_trade_leg() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())  # LONG, stop=1990, target=2020

    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert len(engine.positions) == 1
    position_id = engine.positions[0].position_id

    stop_as_of = entry_as_of + BAR_SECONDS
    engine.settle_bar(stop_as_of, bar_index=2, bars=_bar(stop_as_of, 1985.0), phase_running=True)  # breaches stop

    assert len(engine.trade_legs) == 1
    leg = engine.trade_legs[0]
    assert leg.position_id == position_id
    assert leg.exit_reason == "STOP_LOSS"
    assert leg.leg.strategy_id == "S10"
    assert leg.leg.net_pnl < 0

    closed = [p for p in engine.positions if p.position_id == position_id][0]
    assert closed.status == "CLOSED"
    assert closed.n_legs == 1
    assert closed.aggregate_net_pnl == leg.leg.net_pnl
    assert closed.full_exit_as_of == leg.leg.exit_as_of


def test_virtual_position_closes_on_take_profit() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())  # LONG, target=2020

    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)

    tp_as_of = entry_as_of + BAR_SECONDS
    engine.settle_bar(tp_as_of, bar_index=2, bars=_bar(tp_as_of, 2025.0), phase_running=True)  # breaches target

    assert len(engine.trade_legs) == 1
    leg = engine.trade_legs[0]
    assert leg.exit_reason == "TAKE_PROFIT"
    assert leg.leg.net_pnl > 0
    assert engine.positions[0].status == "CLOSED"


def test_a_strategy_cannot_hold_two_concurrent_shadow_positions_same_symbol() -> None:
    # Design §8: the same frozen LIMIT_MAX_PER_SYMBOL check, reused unmodified, structurally limits a
    # shadow account to one open position at a time -- a second entry attempt while one is open denies.
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert len(engine.positions) == 1

    reentry_as_of = entry_as_of + BAR_SECONDS
    engine.observe(reentry_as_of, _batch(_score(strategy_id="S10", entry=2001.0)), _risk_context(reentry_as_of))
    latest = engine.opportunities[-1]
    assert latest.shadow_risk_decision == "DENY"
    assert latest.shadow_denied_reason == "LIMIT_MAX_PER_SYMBOL"


def test_a_second_allow_while_the_first_entry_is_still_pending_does_not_corrupt_bookkeeping() -> None:
    # Checkpoint 3's own real finding, at 43-strategy validation scale: a strategy's entry is a
    # LIMIT-priced BRACKET order (entry/stop/target all set) that can sit WORKING for many bars before
    # it fills -- LIMIT_MAX_PER_SYMBOL only sees OPEN positions, never pending orders, so RiskManager
    # legitimately ALLOWs a second entry for the same symbol while the first is still unresolved. This
    # must never silently overwrite account.pending_entries[symbol] and orphan the first order's own
    # eventual fill.
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())  # entry=2000, first order

    # Price stays away from 2000 (never touches the LONG limit: bar.low <= 2000) -- the first entry
    # order stays genuinely WORKING, unresolved, for several bars.
    away_as_of_1 = AS_OF + BAR_SECONDS
    engine.settle_bar(away_as_of_1, bar_index=1, bars=_bar(away_as_of_1, 2010.0), phase_running=True)
    assert engine.positions == ()  # first order has not filled yet

    # A second ALLOW arrives for the SAME strategy+symbol before the first resolves.
    away_as_of_2 = away_as_of_1 + BAR_SECONDS
    engine.observe(away_as_of_2, _batch(_score(strategy_id="S10", entry=2005.0)), _risk_context(away_as_of_2))
    second_opp = engine.opportunities[-1]
    assert second_opp.shadow_risk_decision == "DENY"
    assert second_opp.shadow_denied_reason == "SHADOW_ENTRY_ALREADY_PENDING"
    assert second_opp.resulting_position_id is None
    assert len(engine.rejections) == 1
    assert engine.rejections[0].denied_reason_code == "SHADOW_ENTRY_ALREADY_PENDING"

    # The FIRST order (still tracked, never overwritten) eventually fills correctly.
    fill_as_of = away_as_of_2 + BAR_SECONDS
    engine.settle_bar(fill_as_of, bar_index=3, bars=_bar(fill_as_of, 2000.0), phase_running=True)
    assert len(engine.positions) == 1
    assert engine.positions[0].entry_price == 2000.0  # the FIRST order's own price, not the second's

    # And it closes cleanly, with correct bookkeeping (the exact scenario that previously raised the
    # defensive "no tracked open position_id" RuntimeError once the bug was hit).
    stop_as_of = fill_as_of + BAR_SECONDS
    engine.settle_bar(stop_as_of, bar_index=4, bars=_bar(stop_as_of, 1985.0), phase_running=True)
    assert len(engine.trade_legs) == 1
    assert engine.positions[0].status == "CLOSED"
    assert len(engine.failures) == 0  # no internal-consistency error was ever raised


def _fractional_fill_context(run_id: str) -> SimulationContext:
    # A hand-constructed 2-leg scaled-exit scenario (Design §13 test 4): FRACTIONAL partial fills mean
    # the SAME closing (TP) order fills 50% on one bar and the remaining 50% on the next -- the exact
    # mechanism that produces multi-leg positions in production (Design §4's "Partial exits" row).
    return SimulationContext(
        run_id=run_id, date_range=DateRange(AS_OF - 10_000_000, AS_OF + 10_000_000),
        symbols=("XAUUSD",), timeframes=("M15",), starting_balance=2000.0, run_seed=1,
        fill_model=FillModel(partial_fill_policy=PartialFillPolicy.FIXED_FRACTION, partial_fill_fraction=0.5),
    )


def test_multi_leg_partial_exit_shares_one_position_id_across_legs() -> None:
    # Design §13 test 4: a hand-constructed multi-leg scenario -- exactly 1 ShadowPositionRecord, N
    # ShadowTradeLegRecords sharing its position_id, aggregation fields derived incrementally from the
    # legs, never the reverse (Design §17.1 Q4's own formal position-identity invariant).
    #
    # FIXED_FRACTION throttles EVERY working order at 50% of its first fill -- including the entry
    # itself (a real ExecutionSimulator property, not special-cased here) -- so the entry needs two
    # settle_bar() calls to fully fill and activate its OCO bracket children (the second fill is a
    # same-direction scale-in, producing no TradeRecord), then the closing TAKE_PROFIT leg itself needs
    # two more calls to fully exit -- four settle_bar() calls total for one hand-traced scenario.
    engine = ShadowEvidenceEngine(
        frozenset({"S10"}), _risk_config(), _fractional_fill_context("T-MULTI-LEG"), SYMBOL_META, CAPABILITIES,
    )
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())

    entry_as_of_1 = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of_1, bar_index=1, bars=_bar(entry_as_of_1, 2000.0), phase_running=True)
    assert len(engine.positions) == 1  # position created on the FIRST (50%) opening fill
    position_id = engine.positions[0].position_id
    assert engine.trade_legs == []  # opening fills never produce a TradeRecord

    entry_as_of_2 = entry_as_of_1 + BAR_SECONDS
    engine.settle_bar(entry_as_of_2, bar_index=2, bars=_bar(entry_as_of_2, 2000.0), phase_running=True)
    assert engine.trade_legs == []  # the scale-in completion still isn't a closing fill
    assert engine.positions[0].position_id == position_id  # same position throughout

    tp_as_of_1 = entry_as_of_2 + BAR_SECONDS
    engine.settle_bar(tp_as_of_1, bar_index=3, bars=_bar(tp_as_of_1, 2025.0), phase_running=True)  # breaches target
    assert len(engine.trade_legs) == 1  # first 50% closing leg
    assert engine.positions[0].status == "OPEN"  # position remains open after a partial exit
    assert engine.positions[0].n_legs == 1

    tp_as_of_2 = tp_as_of_1 + BAR_SECONDS
    engine.settle_bar(tp_as_of_2, bar_index=4, bars=_bar(tp_as_of_2, 2025.0), phase_running=True)  # second 50%

    assert len(engine.trade_legs) == 2
    assert {leg.position_id for leg in engine.trade_legs} == {position_id}  # both legs share one id
    assert [leg.exit_reason for leg in engine.trade_legs] == ["TAKE_PROFIT", "TAKE_PROFIT"]
    assert len(engine.positions) == 1  # exactly one ShadowPositionRecord, never duplicated

    closed = engine.positions[0]
    assert closed.status == "CLOSED"
    assert closed.n_legs == 2
    assert closed.aggregate_net_pnl == sum(leg.leg.net_pnl for leg in engine.trade_legs)
    assert closed.full_exit_as_of == engine.trade_legs[-1].leg.exit_as_of

    # Test 5 (§13): partial exits do not inflate opportunity counts -- exactly 1 virtual entry, no
    # matter how many legs the resulting position produces.
    assert len(engine.opportunities) == 1

    closed = engine.positions[0]
    assert closed.status == "CLOSED"
    assert closed.n_legs == 2
    assert closed.aggregate_net_pnl == sum(leg.leg.net_pnl for leg in engine.trade_legs)
    assert closed.full_exit_as_of == engine.trade_legs[-1].leg.exit_as_of

    # Test 5 (§13): partial exits do not inflate opportunity counts -- exactly 1 virtual entry, no
    # matter how many legs the resulting position produces.
    assert len(engine.opportunities) == 1


def test_time_stop_closes_a_virtual_position() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)

    due_as_of = entry_as_of + BAR_SECONDS
    engine.apply_time_stops(due_as_of, bar_index=2, time_stop_bars_by_strategy={"S10": 1})
    settle_as_of = due_as_of + BAR_SECONDS
    engine.settle_bar(settle_as_of, bar_index=3, bars=_bar(settle_as_of, 2000.0), phase_running=True)

    assert len(engine.trade_legs) == 1
    assert engine.trade_legs[0].exit_reason == "TIME_STOP"
    assert engine.positions[0].status == "CLOSED"


def test_finalize_at_end_force_closes_a_still_open_shadow_position() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert engine.positions[0].status == "OPEN"

    end_as_of = entry_as_of + BAR_SECONDS
    engine.finalize_at_end(end_as_of, bar_index=2, bars=_bar(end_as_of, 2005.0))

    assert len(engine.trade_legs) == 1
    assert engine.trade_legs[0].exit_reason == "FORCED_CLOSE_AT_WINDOW_END"
    assert engine.positions[0].status == "CLOSED"


def test_finalize_at_end_flushes_a_still_pending_unresolved_entry() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    # No settle_bar() call at all -- the entry never got a chance to resolve.
    assert engine.opportunities == []

    engine.finalize_at_end(AS_OF + BAR_SECONDS, bar_index=1, bars=_bar(AS_OF + BAR_SECONDS))

    assert len(engine.opportunities) == 1
    assert engine.opportunities[0].shadow_risk_decision == "ALLOW"
    assert engine.opportunities[0].resulting_position_id is None
    assert engine.positions == ()


def test_settle_bar_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())

    def _boom(self: ShadowEvidenceEngine, *args: object, **kwargs: object) -> None:
        raise RuntimeError("forced settlement failure")

    original = ShadowEvidenceEngine._settle_one
    ShadowEvidenceEngine._settle_one = _boom  # type: ignore[method-assign]
    try:
        engine.settle_bar(AS_OF + BAR_SECONDS, bar_index=1, bars=_bar(AS_OF + BAR_SECONDS), phase_running=True)
    finally:
        ShadowEvidenceEngine._settle_one = original  # type: ignore[method-assign]

    assert len(engine.failures) == 2
    failed_ids = {sid for _as_of, sid, _err in engine.failures}
    assert failed_ids == {"S10", "S21"}
    assert engine.opportunities == []  # neither entry ever resolved


def test_apply_time_stops_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert len(engine._accounts) == 2

    def _boom(self: ShadowEvidenceEngine, *args: object, **kwargs: object) -> None:
        raise RuntimeError("forced time-stop failure")

    original = ShadowEvidenceEngine._apply_time_stop_one
    ShadowEvidenceEngine._apply_time_stop_one = _boom  # type: ignore[method-assign]
    try:
        due_as_of = entry_as_of + BAR_SECONDS
        engine.apply_time_stops(due_as_of, bar_index=2, time_stop_bars_by_strategy={"S10": 1, "S21": 1})
    finally:
        ShadowEvidenceEngine._apply_time_stop_one = original  # type: ignore[method-assign]

    assert len(engine.failures) == 2
    assert {sid for _as_of, sid, _err in engine.failures} == {"S10", "S21"}
    # Positions remain OPEN (the overlay never got to close them) -- competitive execution is
    # untouched, but this call site's own failure isolation is what's under test here.
    assert all(p.status == "OPEN" for p in engine.positions)


def test_apply_trailing_stops_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert len(engine._accounts) == 2

    def _boom(self: ShadowEvidenceEngine, *args: object, **kwargs: object) -> None:
        raise RuntimeError("forced trailing-stop failure")

    original = ShadowEvidenceEngine._apply_trailing_stop_one
    ShadowEvidenceEngine._apply_trailing_stop_one = _boom  # type: ignore[method-assign]
    try:
        due_as_of = entry_as_of + BAR_SECONDS
        engine.apply_trailing_stops(
            due_as_of, bars=_bar(due_as_of, 2005.0), context_batch={},
            atr_mult_by_strategy={"S10": 1.5, "S21": 1.5},
        )
    finally:
        ShadowEvidenceEngine._apply_trailing_stop_one = original  # type: ignore[method-assign]

    assert len(engine.failures) == 2
    assert {sid for _as_of, sid, _err in engine.failures} == {"S10", "S21"}


def test_apply_time_stops_is_a_no_op_when_nothing_is_due_yet() -> None:
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert engine.positions[0].status == "OPEN"

    # A time_stop_bars horizon far in the future -- nothing is due yet.
    engine.apply_time_stops(entry_as_of + BAR_SECONDS, bar_index=2, time_stop_bars_by_strategy={"S10": 10_000})

    assert engine.positions[0].status == "OPEN"  # untouched
    assert engine.trade_legs == []


def test_finalize_at_end_is_a_no_op_under_hold_and_mark_policy() -> None:
    context = SimulationContext(
        run_id="T-HOLD-AND-MARK", date_range=DateRange(AS_OF - 10_000_000, AS_OF + 10_000_000),
        symbols=("XAUUSD",), timeframes=("M15",), starting_balance=2000.0, run_seed=1,
        close_at_end_policy=CloseAtEndPolicy.HOLD_AND_MARK,
    )
    engine = ShadowEvidenceEngine(frozenset({"S10"}), _risk_config(), context, SYMBOL_META, CAPABILITIES)
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert engine.positions[0].status == "OPEN"

    engine.finalize_at_end(entry_as_of + BAR_SECONDS, bar_index=2, bars=_bar(entry_as_of + BAR_SECONDS, 2005.0))

    assert engine.positions[0].status == "OPEN"  # HOLD_AND_MARK leaves it open, untouched
    assert engine.trade_legs == []


def test_finalize_at_end_failure_isolation_degrades_only_the_failing_strategy() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    assert len(engine._accounts) == 2

    def _boom(self: ShadowEvidenceEngine, *args: object, **kwargs: object) -> None:
        raise RuntimeError("forced finalize failure")

    original = ShadowEvidenceEngine._finalize_one
    ShadowEvidenceEngine._finalize_one = _boom  # type: ignore[method-assign]
    try:
        end_as_of = entry_as_of + BAR_SECONDS
        engine.finalize_at_end(end_as_of, bar_index=2, bars=_bar(end_as_of, 2005.0))
    finally:
        ShadowEvidenceEngine._finalize_one = original  # type: ignore[method-assign]

    assert len(engine.failures) == 2
    assert {sid for _as_of, sid, _err in engine.failures} == {"S10", "S21"}


# ------------------------------------------------------------------------------- lifecycle introspection + aggregation (Checkpoint 2)

def test_configured_strategy_ids_reflects_construction() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    assert engine.configured_strategy_ids == frozenset({"S10", "S21"})
    assert engine.degraded_strategy_ids == frozenset()
    assert engine.active_strategy_ids == frozenset({"S10", "S21"})


def test_degraded_and_active_strategy_ids_reflect_a_failure() -> None:
    engine = _engine(frozenset({"S10", "S21"}))

    def _boom(self: ShadowEvidenceEngine, as_of: int, score: OpportunityScore, risk_context: RiskContext) -> None:
        raise RuntimeError("forced failure")

    original = ShadowEvidenceEngine._observe_one
    ShadowEvidenceEngine._observe_one = _boom  # type: ignore[method-assign]
    try:
        engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    finally:
        ShadowEvidenceEngine._observe_one = original  # type: ignore[method-assign]

    assert engine.degraded_strategy_ids == frozenset({"S10"})
    assert engine.active_strategy_ids == frozenset({"S21"})
    assert engine.configured_strategy_ids == frozenset({"S10", "S21"})  # unchanged -- still configured


def test_summaries_aggregates_across_multiple_strategies_end_to_end() -> None:
    engine = _engine(frozenset({"S10", "S21"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)
    stop_as_of = entry_as_of + BAR_SECONDS
    engine.settle_bar(stop_as_of, bar_index=2, bars=_bar(stop_as_of, 1985.0), phase_running=True)  # both stop out

    summaries = engine.summaries("12m", stop_as_of)
    assert set(summaries) == {"S10", "S21"}
    for strategy_id, summary in summaries.items():
        assert summary.strategy_id == strategy_id
        assert summary.source == "shadow"
        assert summary.window_metrics.n_trades == 1
        assert summary.window_metrics.net_pnl < 0  # both closed at a loss (stop hit)


def test_summaries_is_read_only_and_never_affects_further_engine_behavior() -> None:
    # Calling summaries() mid-run must change nothing about subsequent observe()/settle_bar() results.
    engine = _engine(frozenset({"S10"}))
    engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    entry_as_of = AS_OF + BAR_SECONDS
    engine.settle_bar(entry_as_of, bar_index=1, bars=_bar(entry_as_of, 2000.0), phase_running=True)

    _ = engine.summaries("3m", entry_as_of)
    _ = engine.summaries("12m", entry_as_of)  # called twice, different windows -- still read-only

    assert engine.positions[0].status == "OPEN"  # untouched by either summaries() call
    assert len(engine._accounts) == 1  # no new account spuriously created by summaries()


# ------------------------------------------------------------------------------- ShadowObservationResult
# (Sprint 2, Blocker 1 -- Learning/Research Feedback connection, CEO-ratified Option A)


def test_observe_returns_a_result_for_an_allow_decision() -> None:
    engine = _engine(frozenset({"S10"}))
    results = engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(results) == 1
    result = results[0]
    assert result.strategy_id == "S10"
    assert result.symbol == "XAUUSD"
    assert result.decision.decision.value == "ALLOW"
    assert result.position_id is not None
    assert result.position_id == f"T:S10:XAUUSD:{AS_OF}:{result.decision.decision_id}"


def test_observe_returns_a_result_for_a_deny_decision_with_no_position_id() -> None:
    engine = _engine(frozenset({"S10"}), RiskConfig())  # bare RiskConfig -> deterministic DENY
    results = engine.observe(AS_OF, _batch(_score(strategy_id="S10")), _risk_context())
    assert len(results) == 1
    result = results[0]
    assert result.decision.decision.value == "DENY"
    assert result.position_id is None


def test_observe_returns_no_result_for_non_configured_or_degraded_strategies() -> None:
    engine = _engine(frozenset({"S10"}))
    results = engine.observe(AS_OF, _batch(_score(strategy_id="S39")), _risk_context())
    assert results == ()


def test_observe_returns_one_result_per_strategy_in_the_batch() -> None:
    engine = _engine(frozenset({"S10", "S21"}), RiskConfig())
    batch = _batch(_score(strategy_id="S10"), _score(strategy_id="S21"))
    results = engine.observe(AS_OF, batch, _risk_context())
    assert {r.strategy_id for r in results} == {"S10", "S21"}


def test_observe_returns_no_result_for_shadow_entry_already_pending_veto() -> None:
    # A LIMIT-priced bracket order stays WORKING (never triggers a MARKET-style immediate fill), so a
    # second ALLOW for the same symbol on a later bar hits the SHADOW_ENTRY_ALREADY_PENDING veto -- a
    # shadow-internal bookkeeping decision, not a genuine Risk Manager decision boundary, and must
    # produce NO ShadowObservationResult (already fully recorded via ShadowOpportunityRecord/
    # ShadowRejectionRecord, per the existing, unchanged test coverage of that path).
    engine = _engine(frozenset({"S10"}))
    first = engine.observe(AS_OF, _batch(_score(strategy_id="S10", entry=2000.0)), _risk_context())
    assert len(first) == 1
    assert first[0].position_id is not None
    later_as_of = AS_OF + BAR_SECONDS
    second = engine.observe(
        later_as_of, _batch(_score(strategy_id="S10", entry=2000.0)), _risk_context(later_as_of),
    )
    assert second == ()
    assert engine.opportunities[-1].shadow_denied_reason == "SHADOW_ENTRY_ALREADY_PENDING"


def test_observe_failure_isolation_still_returns_results_for_healthy_strategies() -> None:
    # A strategy that raises inside _observe_one is degraded and contributes no result, but every
    # OTHER strategy in the same batch still gets its own ShadowObservationResult -- mirrors the
    # existing failure-isolation guarantee, extended to the new return value.
    engine = _engine(frozenset({"S10", "S21"}))
    original = ShadowEvidenceEngine._observe_one

    def _boom_for_s10(self: ShadowEvidenceEngine, as_of: int, score: OpportunityScore, risk_context: RiskContext):
        if score.strategy_id == "S10":
            raise RuntimeError("forced failure")
        return original(self, as_of, score, risk_context)

    ShadowEvidenceEngine._observe_one = _boom_for_s10  # type: ignore[method-assign]
    try:
        results = engine.observe(AS_OF, _batch(_score(strategy_id="S10"), _score(strategy_id="S21")), _risk_context())
    finally:
        ShadowEvidenceEngine._observe_one = original  # type: ignore[method-assign]
    assert {r.strategy_id for r in results} == {"S21"}
    assert "S10" in engine.degraded_strategy_ids
