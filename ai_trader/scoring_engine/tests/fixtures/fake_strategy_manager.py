"""Test doubles for the Scoring Engine's Strategy Manager dependency, plus a convenience builder for
real, schema-valid ``StrategySignal`` objects (built through the REAL Signal Engine pipeline +
assembler, not hand-constructed dicts -- exercising the actual upstream contract end-to-end).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ai_trader.signal_engine import assembler as se_assembler
from ai_trader.signal_engine import pipeline as se_pipeline
from ai_trader.signal_engine.config import EngineConfig
from ai_trader.signal_engine.tests.fixtures.fake_strategy import make_context, make_fake_handle
from ai_trader.signal_engine.types import StrategySignal
from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.types import Health, Lifecycle, NotFound as SMNotFound, StrategyView


def make_signal(
    strategy_id: str = "S1",
    symbol: str = "XAUUSD",
    generate_signal_response: dict[str, Any] | None = None,
    detect_response: dict[str, Any] | None = None,
    health_response: dict[str, Any] | None = None,
    can_trade_response: dict[str, Any] | None = None,
    required_data: list[dict[str, Any]] | None = None,
    required_timeframes: frozenset[str] | None = None,
    required_fields_by_timeframe: dict[str, frozenset[str]] | None = None,
    required_lookback_by_timeframe: dict[str, int] | None = None,
    context_overrides: dict[str, Any] | None = None,
) -> StrategySignal:
    """Build a real, schema-valid ``StrategySignal`` by running the actual Signal Engine pipeline +
    assembler against a controllable :class:`FakeStrategyApi` -- the same technique
    ``ai_trader/signal_engine/tests/`` uses internally, reused here so Scoring Engine tests exercise
    genuine upstream objects, never a hand-rolled approximation of one.

    ``required_data`` only shapes the CONTRACT's declared ``semantics.required_data`` (read by
    Scoring Engine's evidence-derived components); it does NOT affect Context Validation -- that is
    driven by ``FakeStrategyApi.required_context()``, controlled separately via
    ``required_timeframes``/``required_fields_by_timeframe``/``required_lookback_by_timeframe`` (use
    these to force a ``NEED_CONTEXT`` signal, e.g. by requiring a timeframe the fixture's default
    context never populates)."""
    contract_kwargs: dict[str, Any] = {}
    if required_data is not None:
        contract_kwargs["required_data"] = required_data
    handle, api = make_fake_handle(strategy_id=strategy_id, **contract_kwargs)
    if generate_signal_response is not None:
        api.generate_signal_response = generate_signal_response
    if detect_response is not None:
        api.detect_response = detect_response
    if health_response is not None:
        api.health_response = health_response
    if can_trade_response is not None:
        api.can_trade_response = can_trade_response
    if required_timeframes is not None:
        api.timeframes = required_timeframes
    if required_fields_by_timeframe is not None:
        api.fields_by_timeframe = required_fields_by_timeframe
    if required_lookback_by_timeframe is not None:
        api.lookback_by_timeframe = required_lookback_by_timeframe

    context = make_context(symbol=symbol)
    if context_overrides:
        context.update(context_overrides)

    outcome = se_pipeline.run_pipeline(context, handle, trader_state=None)
    return se_assembler.assemble_signal(
        strategy_id=handle.id, contract=handle.contract, outcome=outcome, context=context,
        evaluation_time_ms=1.0, config=EngineConfig(), now_ts=context["meta"]["as_of"],
    )


@dataclass
class FakeStrategyManager:
    """Controllable :class:`~ai_trader.scoring_engine.evidence.StrategyManagerLike` double. Each
    strategy id's ``find_strategy``/``get_contract`` response is configured via ``views``/
    ``contracts``; an id absent from either dict resolves to :class:`SMNotFound`."""

    views: dict[str, StrategyView] = field(default_factory=dict)
    contracts: dict[str, Contract] = field(default_factory=dict)
    find_strategy_fn: Callable[[str], "StrategyView | SMNotFound"] | None = None
    get_contract_fn: Callable[[str], "Contract | SMNotFound"] | None = None
    calls: list[str] = field(default_factory=list)

    def find_strategy(self, strategy_id: str) -> StrategyView | SMNotFound:
        self.calls.append(f"find_strategy:{strategy_id}")
        if self.find_strategy_fn is not None:
            return self.find_strategy_fn(strategy_id)
        view = self.views.get(strategy_id)
        return view if view is not None else SMNotFound(strategy_id)

    def get_contract(self, strategy_id: str) -> Contract | SMNotFound:
        self.calls.append(f"get_contract:{strategy_id}")
        if self.get_contract_fn is not None:
            return self.get_contract_fn(strategy_id)
        contract = self.contracts.get(strategy_id)
        return contract if contract is not None else SMNotFound(strategy_id)

    def register(self, strategy_id: str, contract: Contract, lifecycle: Lifecycle = Lifecycle.EXPLORATORY) -> None:
        """Convenience: register both the view (for ``find_strategy``) and the contract (for
        ``get_contract``) for one strategy id in a single call."""
        self.contracts[strategy_id] = contract
        self.views[strategy_id] = StrategyView(
            id=strategy_id, name=contract.identity.name, slug=contract.identity.slug,
            lifecycle=lifecycle, health=Health.LOADED, identity_version=contract.identity.version,
            interface_version=contract.interface_version, maturity=contract.lifecycle.maturity, active=True,
        )
