"""Types owned by MT5 Demo Execution (Phase 10). Reuses `execution_engine.adapters.mt5_types`
(`AccountTradeMode`, `AlgoTradingStatus`, `MT5AdapterStatus`, `NormalizedMT5Error`) unmodified -- only
the genuinely missing order-send-specific pieces live here."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MT5DemoConfig:
    """Explicit, versioned-by-value (no hidden constants). `max_order_volume` defaults to the broker's
    own confirmed minimum lot size for XAUUSD (`MT5_CONNECTIVITY_PROBE_REPORT.md`: `volume_min=0.01`) --
    CEO: "test with minimal configurable volume". `deviation_points` is MT5's own max-slippage-in-points
    concept (distinct from `OrderConstraints.max_slippage`, a price-distance, not a point count)."""

    max_order_volume: float = 0.01
    deviation_points: int = 20
    market_staleness_threshold_seconds: int = 120
    expected_server: str | None = None

    def __post_init__(self) -> None:
        if self.max_order_volume <= 0:
            raise ValueError("MT5DemoConfig.max_order_volume must be > 0")
        if self.deviation_points < 0:
            raise ValueError("MT5DemoConfig.deviation_points must be >= 0")
        if self.market_staleness_threshold_seconds <= 0:
            raise ValueError("MT5DemoConfig.market_staleness_threshold_seconds must be > 0")


@dataclass(frozen=True, slots=True)
class MT5OrderCheckResult:
    """Normalized `mt5.order_check()` response (mirrors `NormalizedMT5Error`'s own normalization
    pattern). `retcode == 0` (`TRADE_RETCODE_DONE`-family "would succeed") is the only value treated as
    OK; every other retcode, including ones this module has never seen before, fails closed."""

    retcode: int
    comment: str
    balance: float | None = None
    margin: float | None = None
    margin_free: float | None = None

    @property
    def ok(self) -> bool:
        return self.retcode == 0


@dataclass(frozen=True, slots=True)
class MT5OrderSendResult:
    """Normalized `mt5.order_send()` response. `retcode == 10009` (`TRADE_RETCODE_DONE`) is MT5's own
    documented "request completed" code -- the only value treated as a successful send."""

    retcode: int
    comment: str
    order: int | None = None
    deal: int | None = None
    volume: float | None = None
    price: float | None = None

    @property
    def ok(self) -> bool:
        return self.retcode == 10009


@dataclass(frozen=True, slots=True)
class SafetyGuardReport:
    """Every guard individually inspectable -- nothing about "why" a send was refused is ever hidden
    inside one opaque boolean (same disclosure discipline as `ContextConfidence`/`ScoreComponents`)."""

    connected: bool
    account_is_demo: bool
    algo_trading_enabled: bool
    server_matches_expected: bool
    max_volume_configured: bool
    market_open: bool | None  # None = undeterminable (no symbol supplied, or no tick data) -- fail-closed by the caller

    @property
    def all_passed(self) -> bool:
        return (
            self.connected and self.account_is_demo and self.algo_trading_enabled
            and self.server_matches_expected and self.max_volume_configured and self.market_open is True
        )
