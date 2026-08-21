"""Shared fixture builders for `strategy_platform` tests."""

from __future__ import annotations

from ai_trader.new_brain_bridge.raw_axes_builder import RawAxesBuilder
from ai_trader.new_brain_bridge.tests.conftest import trend_up_regime_bars
from ai_trader.new_brain_live.dual_clock.upstream_context import build_context
from ai_trader.new_brain_live.market_state import MarketState
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyCatalog, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import Strategy
from ai_trader.risk_manager_live.tests._fixtures import make_account, make_config, make_instrument, make_portfolio, make_risk_context

SYMBOL = "XAUUSD"


def real_trend_up_market_state() -> MarketState:
    """A real, N1/Router-produced MarketState resolving TREND_UP -- the same `trend_up_regime_bars()`
    fixture `dual_clock`'s own tests already independently verify resolves this regime. `catalog=()`
    means Router's own `eligibility_decisions` field is empty (irrelevant to `strategy_platform`, which
    re-derives regime membership itself via `ve_brain.applicable_regimes`, never reads that field)."""
    bars = trend_up_regime_bars(SYMBOL)
    builder = RawAxesBuilder(SYMBOL)
    for bar in bars[:-1]:
        builder.observe(bar)
    last_bar = bars[-1]
    return build_context(symbol=SYMBOL, timeframe="M15", bar=last_bar, axes_builder=builder, catalog=())


def catalog_entry_for(
    strategy: Strategy, *, status: StrategyStatus = StrategyStatus.MOCK_TEST_ONLY, enabled: bool = True,
    context_eligibility: tuple[str, ...] | None = None, allowed_instruments: tuple[str, ...] = (SYMBOL,),
) -> CatalogEntry:
    # Our own mock strategies expose strategy_id/strategy_version; the Protocol itself does not require them.
    sid: str = strategy.strategy_id  # type: ignore[attr-defined]
    sversion: str = strategy.strategy_version  # type: ignore[attr-defined]
    return CatalogEntry(
        strategy_id=sid, strategy_version=sversion, status=status,
        enabled=enabled, allowed_instruments=allowed_instruments, allowed_directions=("LONG", "SHORT"),
        context_eligibility=context_eligibility, implementation_fingerprint=f"{sid}-impl-v1",
        config_fingerprint=f"{sid}-cfg-v1", validation_provenance=None,
        risk_contract_reference="risk_manager_live-v1", rollback_identity=f"{sid}-rollback-v1",
        strategy=strategy,
    )


def catalog_of(*strategies: Strategy, **entry_kwargs: object) -> StrategyCatalog:
    return StrategyCatalog(entries=tuple(catalog_entry_for(s, **entry_kwargs) for s in strategies))  # type: ignore[arg-type]


def make_risk_execution_deps(symbol: str = SYMBOL) -> dict[str, object]:
    """Field-by-field kwargs (not a constructed `RiskExecutionDeps`, to avoid importing the dataclass
    here and creating an import cycle risk) -- callers do `RiskExecutionDeps(**make_risk_execution_deps())`."""
    return {
        "account": make_account(), "portfolio": make_portfolio(), "instrument": make_instrument(symbol=symbol),
        "risk_context": make_risk_context(symbol=symbol), "risk_config": make_config(symbol=symbol),
    }
