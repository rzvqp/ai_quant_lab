from __future__ import annotations

from pathlib import Path

from ai_trader.new_brain_live.strategy_platform.mt5_demo_bridge.soak.health_state import (
    HealthSnapshot,
    read_health_snapshot,
    write_health_snapshot,
)


def _snapshot(**overrides: object) -> HealthSnapshot:
    kwargs: dict[str, object] = dict(
        loop_alive_as_of=1000, mt5_connected=True, account_trade_mode="AccountTradeMode.DEMO",
        server="FusionMarkets-Demo", equity=10_000.0, last_valid_market_event_ts=900,
        last_processed_bar_ts=900, open_owned_positions=0, pending_owned_orders=0,
        last_reconciliation_as_of=500, last_error=None, safety_blocked=False, safety_block_condition=None,
        trades_closed_so_far=0, soak_started_at=100.0,
    )
    kwargs.update(overrides)
    return HealthSnapshot(**kwargs)  # type: ignore[arg-type]


def test_missing_file_returns_none(tmp_path: Path) -> None:
    assert read_health_snapshot(tmp_path / "does_not_exist.json") is None


def test_write_then_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "sub" / "health.json"
    snap = _snapshot(equity=12_345.67, trades_closed_so_far=3)
    write_health_snapshot(path, snap)
    read_back = read_health_snapshot(path)
    assert read_back == snap


def test_write_overwrites_previous_snapshot(tmp_path: Path) -> None:
    path = tmp_path / "health.json"
    write_health_snapshot(path, _snapshot(trades_closed_so_far=1))
    write_health_snapshot(path, _snapshot(trades_closed_so_far=2))
    read_back = read_health_snapshot(path)
    assert read_back is not None
    assert read_back.trades_closed_so_far == 2


def test_no_secret_fields_exist_on_the_dataclass() -> None:
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(HealthSnapshot)}
    for forbidden in ("password", "token", "secret", "login", "credential"):
        assert not any(forbidden in name.lower() for name in field_names)
