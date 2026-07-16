"""Phase 6.9 CEO-approved fix proof: Health-gating (``strategy_id_filter``) must restrict NEW-signal
eligibility only -- it must never strip time-stop/trailing-stop protection from an already-open
position (CEO methodological rule, 2026-07-16). These tests drive the REAL composed pipeline +
Simulation Framework with a strategy EXCLUDED from ``strategy_id_filter`` from the very start (the
strongest case: fully demoted, never "currently active" at all -- a superset of "demoted mid-run")
and prove its synthetically-injected open position still receives its own declared overlay exit,
while ``strategy_id_filter`` itself continues to block every new signal throughout
(``only_ids=frozenset()`` admits nothing). Positions are injected directly (mirroring
``test_time_stop.py``'s own ``make_position`` pattern) rather than waited-for organically, so these
tests are deterministic and fast, never dependent on real market data happening to produce a signal
at a particular moment."""

from __future__ import annotations

from pathlib import Path

from ai_trader.market_scanner.types import SymbolMeta
from ai_trader.risk_manager.config import RiskConfig
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.config import DateRange, SimulationContext
from ai_trader.simulation.harness import SimulationHarness
from ai_trader.simulation.portfolio_simulator import Position
from ai_trader.simulation.types import RunState, SimPhase
from ai_trader.strategy_manager.config import ManagerConfig
from ai_trader.strategy_runtime.registry import build_runtime_handles

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "market"
SYMBOL_META = {"XAUUSD": SymbolMeta(symbol="XAUUSD", tick_size=0.01, point_value=1.0, price_precision=2)}
TIME_STOP_ID = "S13"   # TIME_STOP_BARS = 24 (families/s13_imbalance_fill.py)
TRAILING_ID = "S10"    # trailing_stop_atr_mult = 1.5 (families/s10_displacement_continuation.py)


def _risk_config() -> RiskConfig:
    cfg = RiskConfig()
    cfg.filters.reference_spread["XAUUSD"] = 0.10
    cfg.filters.liquidity_floor["XAUUSD"] = 1.0
    return cfg


def _make_harness(run_id: str) -> SimulationHarness:
    """``strategy_id_filter=frozenset()`` (empty, NOT ``None``) admits ZERO strategies for new
    signals -- ``TIME_STOP_ID``/``TRAILING_ID`` are excluded from bar 0 onward, yet both remain
    registered runtime evaluators (``build_runtime_handles(only_ids=None)`` still finds them),
    exactly the "demoted, holding an open position" case Phase 6.9 introduces."""
    context = SimulationContext(
        run_id=run_id, date_range=DateRange(1_672_617_600, 1_672_761_600), symbols=("XAUUSD",),
        timeframes=("M15", "H1", "H4", "D1"), starting_balance=2000.0, run_seed=1, warmup_bars=200,
    )
    harness = SimulationHarness(
        context, SYMBOL_META, DATA_DIR,
        manager_config=ManagerConfig(auto_admit_min_maturity="EXPLORATORY"),
        use_strategy_runtime=True, risk_config=_risk_config(),
        enable_time_stops=True, enable_trailing_stops=True,
        strategy_id_filter=frozenset(),
    )
    harness.configure()
    harness.load()
    assert harness.state is RunState.WARMUP, harness.fail_reason
    return harness


def _advance_to_running(harness: SimulationHarness) -> None:
    while harness.phase is not SimPhase.RUNNING:
        assert harness.step(), harness.fail_reason


def test_demoted_strategy_is_absent_from_new_signal_handles_but_present_in_the_unfiltered_set() -> None:
    """Registry-level proof of the mechanism the harness fix relies on."""
    harness = _make_harness("OVERLAY-HANDLES")
    new_signal_handles = build_runtime_handles(
        harness._strategy_manager, frozenset({"XAUUSD"}), only_ids=frozenset(),
    )
    new_signal_ids = {h.id for h in new_signal_handles}
    assert TIME_STOP_ID not in new_signal_ids
    assert TRAILING_ID not in new_signal_ids

    overlay_handles = build_runtime_handles(harness._strategy_manager, frozenset({"XAUUSD"}), only_ids=None)
    overlay_ids = {h.id for h in overlay_handles}
    assert TIME_STOP_ID in overlay_ids
    assert TRAILING_ID in overlay_ids


def test_time_stop_still_closes_a_demoted_strategys_open_position() -> None:
    harness = _make_harness("OVERLAY-TIMESTOP")
    _advance_to_running(harness)
    assert harness.portfolio_simulator is not None

    opened_bar_index = harness.bar_index
    opened_as_of = harness.as_of
    assert opened_as_of is not None
    harness.portfolio_simulator.account.positions["XAUUSD"] = Position(
        symbol="XAUUSD", strategy_id=TIME_STOP_ID, direction=Direction.LONG, size=0.01,
        avg_entry=2000.0, opened_as_of=opened_as_of, opened_bar_index=opened_bar_index,
    )

    for _ in range(26):
        if not harness.step():
            break

    account = harness.portfolio_simulator.account
    time_stop_trades = [t for t in account.trade_ledger if t.strategy_id == TIME_STOP_ID]
    assert len(time_stop_trades) == 1, (
        "the demoted strategy's own open position must still close via its declared time-stop"
    )
    assert time_stop_trades[0].symbol == "XAUUSD"
    assert time_stop_trades[0].holding_bars == 24
    # No other trade of any kind: `strategy_id_filter=frozenset()` admits nothing, so the single
    # trade above -- the synthetically-injected position closing -- is the only possible ledger entry.
    # In particular the demoted strategy itself never opens a SECOND (new) position.
    assert len(account.trade_ledger) == 1


def test_trailing_stop_still_closes_a_demoted_strategys_open_position() -> None:
    harness = _make_harness("OVERLAY-TRAILING")
    _advance_to_running(harness)
    assert harness.portfolio_simulator is not None

    opened_bar_index = harness.bar_index
    opened_as_of = harness.as_of
    assert opened_as_of is not None
    harness.portfolio_simulator.account.positions["XAUUSD"] = Position(
        symbol="XAUUSD", strategy_id=TRAILING_ID, direction=Direction.LONG, size=0.01,
        avg_entry=2000.0, opened_as_of=opened_as_of, opened_bar_index=opened_bar_index,
    )
    # A near-zero entry ATR collapses the trailing distance to ~0, so the very next bar's own
    # high-low range breaches it deterministically -- proving the mechanism fires without depending
    # on which direction real market data happens to move that particular historical day.
    harness._trailing_entry_atr["XAUUSD"] = 1e-6

    for _ in range(3):
        if not harness.step():
            break

    account = harness.portfolio_simulator.account
    trailing_trades = [t for t in account.trade_ledger if t.strategy_id == TRAILING_ID]
    assert len(trailing_trades) == 1, (
        "the demoted strategy's own open position must still close via its declared trailing-stop"
    )
    assert trailing_trades[0].symbol == "XAUUSD"
    assert len(account.trade_ledger) == 1
