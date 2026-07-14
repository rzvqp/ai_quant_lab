"""Exception hierarchy for the Strategy Manager.

Per ``STRATEGY_MANAGER_ARCHITECTURE.md`` §9 ("Error handling & fail-safe policy") and
``STRATEGY_MANAGER_API.md`` ("Failure model"), every *expected* failure — a bad contract, an
unknown id, an incompatible strategy — is a classified, typed result on the registry/report, never
an exception thrown across the public API boundary. The exceptions below exist only for genuinely
exceptional conditions: programmer errors (calling the API before :meth:`StrategyManager.configure`)
and environment failures (the schema file itself is missing/corrupt). All derive from
:class:`StrategyManagerError` so callers can catch the whole family with one ``except`` clause.
"""

from __future__ import annotations


class StrategyManagerError(Exception):
    """Base class for every Strategy Manager exception."""


class ManagerNotConfiguredError(StrategyManagerError):
    """Raised when an operation requires :meth:`StrategyManager.configure` to have run first."""


class SchemaLoadError(StrategyManagerError):
    """Raised when ``strategy_contract.v1.schema.json`` cannot be located, read, or compiled."""


class UnknownStrategyError(StrategyManagerError):
    """Raised only by internal helpers that intentionally do not follow the typed-result
    convention. The public API (:meth:`StrategyManager.find_strategy`,
    :meth:`StrategyManager.get_contract`) returns a typed ``NotFound`` result instead of raising
    this — see ``STRATEGY_MANAGER_API.md`` §2."""

    def __init__(self, strategy_id: str) -> None:
        self.strategy_id = strategy_id
        super().__init__(f"unknown strategy id: {strategy_id!r}")


class IllegalTransitionError(StrategyManagerError):
    """Raised when code attempts a lifecycle transition that is not in the transition table
    (``STRATEGY_MANAGER_STATE_MACHINE.md`` §3) — a programmer error, since the public lifecycle
    methods (:meth:`StrategyManager.activate` etc.) always guard first and return a typed
    ``LifecycleResult{ok=False}`` rather than raising."""

    def __init__(self, from_state: str, to_state: str, trigger: str) -> None:
        self.from_state = from_state
        self.to_state = to_state
        self.trigger = trigger
        super().__init__(f"illegal lifecycle transition {from_state} -> {to_state} via {trigger!r}")


class StrategyApiNotImplementedError(StrategyManagerError, NotImplementedError):
    """Raised by a :class:`~ai_trader.strategy_manager.handle.StrategyRuntimeHandle`'s behavioural
    methods (``detect``, ``generate_signal``, ``get_score``, ``can_trade``, ``can_open_position``,
    ``explain_signal``, ``health``). These require live ``MarketContext``/``TraderState`` and
    strategy-specific rule-evaluation logic that does not exist anywhere in this repository (the 51
    Strategy Library entries are executable *specifications*, not executable *code* — see
    ``knowledge/strategies/*/strategy.json``). Building that evaluation logic is the Signal Engine's
    job (Phase 6.3, not started, CEO-gated), not the Strategy Manager's, whose documented boundary is
    "never generate signals, score, size, or execute orders"
    (``STRATEGY_MANAGER_ARCHITECTURE.md`` §1). Raising this — rather than returning a fabricated
    response — keeps that boundary honest instead of silently inventing trading logic."""

    def __init__(self, strategy_id: str, method: str) -> None:
        self.strategy_id = strategy_id
        self.method = method
        super().__init__(
            f"{strategy_id}: Strategy API method {method}() is not implemented by the Strategy "
            "Manager — it requires live market context and strategy-specific execution logic that "
            "belongs to the (not yet built) Signal Engine, not the Strategy Manager."
        )
