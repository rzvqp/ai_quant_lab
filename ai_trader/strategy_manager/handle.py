"""``StrategyHandle`` — the runtime handle exposed to the Signal Engine (``STRATEGY_MANAGER_API.md``
§0/§2: ``active_strategies()`` "is the ONLY method that yields runtime handles").

**Scope boundary (read before extending this module).** ``StrategyHandle{ id, contract (read-only),
api }`` is documented to carry "the read-only contract + the Strategy API". This build implements
``api.required_context()`` only — the one Strategy API method (``STRATEGY_API_v1.md`` §1) that is a
pure, deterministic function of the contract with no live ``Context``/``TraderState`` dependency.
The other six methods (``detect``, ``generate_signal``, ``get_score``, ``can_trade``,
``can_open_position``, ``explain_signal``, plus ``health`` when called with live context) require
per-strategy rule-evaluation logic that does not exist anywhere in this repository: the 51 Strategy
Library entries (``knowledge/strategies/*/strategy.json``) are executable *specifications* (natural-
language ``entry``/``exit``/``stop`` rule descriptions), not executable *code*. Building an engine
that interprets those specifications against live market data is the Signal Engine's job (Phase 6.3,
NOT STARTED, CEO-gated) — the Strategy Manager's own documented boundary is "never generate signals,
score, size, or execute orders" (``STRATEGY_MANAGER_ARCHITECTURE.md`` §1). Calling any of the six
un-implemented methods raises :class:`~ai_trader.strategy_manager.exceptions.
StrategyApiNotImplementedError` with a clear explanation, rather than fabricating a response — this
is a deliberate, documented scope boundary, not an oversight or a placeholder to "fill in later" in
this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.exceptions import StrategyApiNotImplementedError
from ai_trader.strategy_manager.required_context import compute_required_context
from ai_trader.strategy_manager.types import RequiredContext


class StrategyRuntimeHandle:
    """The ``api`` object on a :class:`StrategyHandle`. See module docstring for scope."""

    __slots__ = ("_strategy_id", "_contract", "_symbols")

    def __init__(self, strategy_id: str, contract: Contract, symbols: frozenset[str]) -> None:
        self._strategy_id = strategy_id
        self._contract = contract
        self._symbols = symbols

    def required_context(self) -> RequiredContext:
        """``STRATEGY_API_v1.md`` §1: pure function of the contract; deterministic, cacheable."""
        return compute_required_context(self._contract, self._symbols)

    def detect(self, context: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "detect")

    def generate_signal(self, context: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "generate_signal")

    def get_score(self, context: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "get_score")

    def can_trade(self, context: object, trader_state: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "can_trade")

    def can_open_position(self, context: object, trader_state: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "can_open_position")

    def explain_signal(self, context: object) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "explain_signal")

    def health(self, context: object | None = None, trader_state: object | None = None) -> object:
        raise StrategyApiNotImplementedError(self._strategy_id, "health")


@dataclass(frozen=True, slots=True)
class StrategyHandle:
    """``{ id, contract (read-only), api }`` (``STRATEGY_MANAGER_API.md`` §0). Carries no research
    internals — only the contract and the (partial, see module docstring) runtime API."""

    id: str
    contract: Contract
    api: StrategyRuntimeHandle
