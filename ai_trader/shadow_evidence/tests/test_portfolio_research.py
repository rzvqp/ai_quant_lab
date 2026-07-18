"""Unit tests for :mod:`ai_trader.shadow_evidence.portfolio_research` -- Phase 6.10 Implementation
Checkpoint 4. Pure-function tests over hand-built ``ShadowPositionRecord``/``ShadowTradeLegRecord``
fixtures.
"""

from __future__ import annotations

from ai_trader.shadow_evidence import portfolio_research as pr
from ai_trader.shadow_evidence.types import ShadowPositionRecord, ShadowTradeLegRecord
from ai_trader.signal_engine.types import Direction
from ai_trader.simulation.portfolio_simulator import TradeRecord

JAN = 1_704_067_200  # 2024-01-01 UTC
FEB = 1_706_745_600  # 2024-02-01 UTC
MAR = 1_709_251_200  # 2024-03-01 UTC


def _trade(strategy_id: str, net_pnl: float, exit_as_of: int) -> ShadowTradeLegRecord:
    record = TradeRecord(
        client_order_id=f"SHADOW-CID-{strategy_id}|XAUUSD|{exit_as_of}", strategy_id=strategy_id,
        symbol="XAUUSD", direction=Direction.LONG, entry_price=2000.0, exit_price=2000.0 + net_pnl,
        entry_as_of=exit_as_of - 900, exit_as_of=exit_as_of, qty=0.1, gross_pnl=net_pnl, fees=0.0,
        net_pnl=net_pnl, pnl_r=1.0, holding_bars=1, mfe=0.0, mae=0.0,
    )
    return ShadowTradeLegRecord(leg=record, position_id="P", exit_reason="TAKE_PROFIT")


def _position(
    strategy_id: str, entry_as_of: int, exit_as_of: int | None, position_id: str, status: str = "CLOSED",
) -> ShadowPositionRecord:
    return ShadowPositionRecord(
        position_id=position_id, strategy_id=strategy_id, symbol="XAUUSD", direction=Direction.LONG,
        entry_as_of=entry_as_of, entry_price=2000.0, entry_opportunity_id=f"{strategy_id}:opp",
        status=status, full_exit_as_of=exit_as_of, n_legs=1 if status == "CLOSED" else 0,
        aggregate_net_pnl=1.0 if status == "CLOSED" else None,
        aggregate_holding_bars_full=1 if status == "CLOSED" else None,
    )


# ------------------------------------------------------------------------------- correlation matrix

def test_monthly_pnl_by_strategy_buckets_correctly() -> None:
    trade_legs = [_trade("S10", 10.0, JAN), _trade("S10", 5.0, JAN + 3600), _trade("S10", -2.0, FEB)]
    monthly = pr.monthly_pnl_by_strategy(trade_legs)
    assert monthly["S10"] == {"2024-01": 15.0, "2024-02": -2.0}


def test_correlation_matrix_is_symmetric_and_self_correlation_is_one() -> None:
    trade_legs = [
        _trade("S10", 10.0, JAN), _trade("S10", -10.0, FEB), _trade("S10", 10.0, MAR),
        _trade("S21", 10.0, JAN), _trade("S21", -10.0, FEB), _trade("S21", 10.0, MAR),
    ]
    matrix = pr.correlation_matrix(trade_legs)
    assert matrix[("S10", "S21")] == matrix[("S21", "S10")]
    assert matrix[("S10", "S10")] == 1.0
    # Identical monthly PnL series -> perfect positive correlation.
    assert matrix[("S10", "S21")] == 1.0


def test_correlation_matrix_zero_fills_months_a_strategy_never_traded() -> None:
    # S10 trades every month; S21 only trades in January -- February/March are zero-filled for S21,
    # not treated as missing (an explicit, disclosed choice).
    trade_legs = [
        _trade("S10", 10.0, JAN), _trade("S10", -10.0, FEB), _trade("S10", 10.0, MAR),
        _trade("S21", 10.0, JAN),
    ]
    matrix = pr.correlation_matrix(trade_legs)
    assert matrix[("S10", "S21")] is not None  # computable, not None, thanks to zero-filling


def test_correlation_matrix_is_deterministic() -> None:
    trade_legs = [_trade("S10", 10.0, JAN), _trade("S21", -5.0, FEB)]
    assert pr.correlation_matrix(trade_legs) == pr.correlation_matrix(trade_legs)


def test_correlation_matrix_empty_input() -> None:
    assert pr.correlation_matrix([]) == {}


# ------------------------------------------------------------------------------- trade overlap

def test_trade_overlap_stats_counts_genuinely_overlapping_positions() -> None:
    positions = [
        _position("S10", JAN, JAN + 3600, "P1"),
        _position("S21", JAN + 1800, JAN + 5400, "P2"),  # overlaps P1
        _position("S39", FEB, FEB + 3600, "P3"),  # no overlap with either
    ]
    stats = pr.trade_overlap_stats(positions)
    by_pair = {(s.strategy_a, s.strategy_b): s.n_overlapping_position_pairs for s in stats}
    assert by_pair[("S10", "S21")] == 1
    assert by_pair[("S10", "S39")] == 0
    assert by_pair[("S21", "S39")] == 0


def test_trade_overlap_stats_ignores_open_positions() -> None:
    # Only ONE strategy (S21) has any CLOSED position -- S10's own open position is excluded, leaving
    # no pair to report at all (not a pair with a spurious zero-overlap count).
    positions = [_position("S10", JAN, None, "P1", status="OPEN"), _position("S21", JAN, JAN + 900, "P2")]
    stats = pr.trade_overlap_stats(positions)
    assert stats == ()


# ------------------------------------------------------------------------------- simultaneous exposure

def test_simultaneous_exposure_finds_the_busiest_moment() -> None:
    positions = [
        _position("S10", JAN, JAN + 3600, "P1"),
        _position("S21", JAN + 900, JAN + 4500, "P2"),
        _position("S39", JAN + 1800, JAN + 5400, "P3"),  # all three overlap around JAN+1800
    ]
    stats = pr.simultaneous_exposure(positions)
    assert stats.max_concurrent_positions == 3
    assert stats.n_strategies_with_any_closed_position == 3


def test_simultaneous_exposure_with_no_overlap_is_one() -> None:
    positions = [_position("S10", JAN, JAN + 900, "P1"), _position("S21", FEB, FEB + 900, "P2")]
    stats = pr.simultaneous_exposure(positions)
    assert stats.max_concurrent_positions == 1


def test_simultaneous_exposure_empty_input() -> None:
    stats = pr.simultaneous_exposure([])
    assert stats.max_concurrent_positions == 0
    assert stats.n_strategies_with_any_closed_position == 0


# ------------------------------------------------------------------------------- diversification

def test_diversification_metrics_reports_simple_aggregates() -> None:
    correlation = {("S10", "S21"): 0.9, ("S21", "S10"): 0.9, ("S10", "S39"): 0.1, ("S39", "S10"): 0.1}
    stats = pr.diversification_metrics(correlation, threshold=0.7)
    assert stats.n_strategy_pairs == 2  # (S10,S21) and (S10,S39), a<b only, no double count
    assert stats.avg_pairwise_correlation == 0.5
    assert stats.n_pairs_highly_correlated == 1  # only (S10, S21) exceeds 0.7


def test_diversification_metrics_ignores_none_correlations() -> None:
    correlation = {("S10", "S21"): None, ("S21", "S10"): None}
    stats = pr.diversification_metrics(correlation)
    assert stats.n_strategy_pairs == 0
    assert stats.avg_pairwise_correlation is None


def test_correlation_matrix_is_none_when_every_strategy_only_ever_traded_in_one_shared_month() -> None:
    # Both strategies traded only within the SAME single calendar month -- the union timeline has
    # exactly 1 month, giving _pearson fewer than 2 points to correlate against (honestly None, never
    # fabricated from a single-point "correlation").
    trade_legs = [
        _trade("S10", 10.0, JAN), _trade("S10", -3.0, JAN + 3600),
        _trade("S21", 5.0, JAN + 7200),
    ]
    matrix = pr.correlation_matrix(trade_legs)
    assert matrix[("S10", "S21")] is None


def test_correlation_matrix_is_none_when_one_strategys_monthly_pnl_never_varies() -> None:
    # S10's own monthly PnL is IDENTICAL every month (zero variance) -- Pearson correlation against
    # any other series is undefined (division by zero stdev), honestly None, never fabricated.
    trade_legs = [
        _trade("S10", 5.0, JAN), _trade("S10", 5.0, FEB), _trade("S10", 5.0, MAR),
        _trade("S21", 1.0, JAN), _trade("S21", -1.0, FEB), _trade("S21", 3.0, MAR),
    ]
    matrix = pr.correlation_matrix(trade_legs)
    assert matrix[("S10", "S21")] is None
