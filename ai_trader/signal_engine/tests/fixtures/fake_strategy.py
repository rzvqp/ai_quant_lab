"""A fully controllable, synthetic Strategy API test double.

No strategy anywhere in this repository has real executable ``detect``/``generate_signal``/etc.
logic (see ``ai_trader/signal_engine/pipeline.py``'s own module docstring), so exercising the full
range of Signal Engine pipeline states requires a test double whose responses are deterministically
controllable -- this is that double, matching ``runtime_responses.v1.schema.json``'s shapes exactly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from ai_trader.strategy_manager.contract import Contract, parse_contract
from ai_trader.strategy_manager.tests.fixtures.contracts import make_contract_dict
from ai_trader.strategy_manager.types import RequiredContext


@dataclass
class FakeStrategyApi:
    """Controllable Strategy API double. Each Strategy API method's response is set directly, or a
    ``*_fn`` override callable can replace it entirely (e.g. to sleep, raise, or return malformed
    data) for isolation/timeout/fail-safe tests.
    """

    contract: Contract
    symbols: frozenset[str] = field(default_factory=lambda: frozenset({"XAUUSD"}))
    timeframes: frozenset[str] = field(default_factory=lambda: frozenset({"M15"}))
    fields_by_timeframe: dict[str, frozenset[str]] = field(default_factory=lambda: {"M15": frozenset({"m_atr"})})
    lookback_by_timeframe: dict[str, int] = field(default_factory=lambda: {"M15": 5})

    health_response: dict[str, Any] | None = None
    can_trade_response: dict[str, Any] | None = None
    detect_response: dict[str, Any] | None = None
    generate_signal_response: dict[str, Any] | None = None
    explain_signal_response: dict[str, Any] | None = None

    health_fn: Callable[..., Any] | None = None
    can_trade_fn: Callable[..., Any] | None = None
    detect_fn: Callable[..., Any] | None = None
    generate_signal_fn: Callable[..., Any] | None = None
    explain_signal_fn: Callable[..., Any] | None = None
    required_context_fn: Callable[[], RequiredContext] | None = None

    calls: list[str] = field(default_factory=list)

    def required_context(self) -> RequiredContext:
        self.calls.append("required_context")
        if self.required_context_fn is not None:
            return self.required_context_fn()
        return RequiredContext(
            timeframes=self.timeframes, fields_by_timeframe=self.fields_by_timeframe,
            lookback_by_timeframe=self.lookback_by_timeframe, symbols=self.symbols,
        )

    def health(self, context: object | None = None, trader_state: object | None = None) -> Any:
        self.calls.append("health")
        if self.health_fn is not None:
            return self.health_fn(context, trader_state)
        if self.health_response is not None:
            return self.health_response
        return {
            "state": "OK", "checks": {"data_ok": True, "not_stale": True, "within_scope": True,
                                       "not_killed": True, "live_drift_ok": None},
            "last_review": "2026-07-01", "notes": None,
        }

    def can_trade(self, context: object, trader_state: object) -> Any:
        self.calls.append("can_trade")
        if self.can_trade_fn is not None:
            return self.can_trade_fn(context, trader_state)
        if self.can_trade_response is not None:
            return self.can_trade_response
        return {"allowed": True, "reasons": [], "slots_remaining": None}

    def detect(self, context: object) -> Any:
        self.calls.append("detect")
        if self.detect_fn is not None:
            return self.detect_fn(context)
        if self.detect_response is not None:
            return self.detect_response
        return {
            "active": True, "setup_forming": True, "insufficient_context": False, "reason": "test setup",
        }

    def generate_signal(self, context: object) -> Any:
        self.calls.append("generate_signal")
        if self.generate_signal_fn is not None:
            return self.generate_signal_fn(context)
        if self.generate_signal_response is not None:
            return self.generate_signal_response
        return {
            "present": True, "direction": "LONG", "entry": 100.0, "stop": 99.0, "target": 102.0,
            "risk_R": 1.0, "confidence": "MEDIUM", "strength": 0.75, "reason": "test signal",
            "regime": "TREND_UP", "required_confirmations_met": True, "valid_until": None, "invalidations": [],
        }

    def explain_signal(self, context: object) -> Any:
        self.calls.append("explain_signal")
        if self.explain_signal_fn is not None:
            return self.explain_signal_fn(context)
        if self.explain_signal_response is not None:
            return self.explain_signal_response
        return {
            "headline": "test headline", "mechanism": self.contract.semantics.mechanism,
            "triggered_conditions": ["SWEEP_TAKEN", "CLOSE_BACK_INSIDE"], "confirmations": [],
            "regime": "TREND_UP", "counterfactual": None,
            "contract_ref": {"id": self.contract.identity.id, "version": self.contract.identity.version},
        }


@dataclass(frozen=True, slots=True)
class FakeHandle:
    """Structurally satisfies :class:`~ai_trader.signal_engine.pipeline.StrategyHandleLike` without
    depending on the concrete (and concretely-typed-to-``StrategyRuntimeHandle``)
    :class:`~ai_trader.strategy_manager.handle.StrategyHandle` -- letting ``api`` be a
    :class:`FakeStrategyApi` rather than a real ``StrategyRuntimeHandle``, which is the whole point
    of this test double."""

    id: str
    contract: Contract
    api: FakeStrategyApi


def make_fake_handle(
    strategy_id: str = "S1", symbols: frozenset[str] = frozenset({"XAUUSD"}), **contract_kwargs: Any,
) -> tuple[FakeHandle, FakeStrategyApi]:
    """Build a :class:`FakeHandle` wrapping a :class:`FakeStrategyApi` -- returns both so tests can
    further configure the API double after construction."""
    contract = parse_contract(make_contract_dict(id=strategy_id, **contract_kwargs))
    api = FakeStrategyApi(contract=contract, symbols=symbols)
    handle = FakeHandle(id=strategy_id, contract=contract, api=api)
    return handle, api


def make_context(
    symbol: str = "XAUUSD", as_of: int = 1_700_000_000, features: dict[str, dict[str, Any]] | None = None,
    session_name: str = "ny", data_quality: str = "OK", bars_per_timeframe: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Build a minimal, schema-shaped ``MarketContext`` dict for tests."""
    features = features or {"M15": {"m_atr": 1.23}}
    bars_per_timeframe = bars_per_timeframe or {tf: 10 for tf in features}
    return {
        "meta": {
            "context_schema_version": "1.0.0", "feature_dictionary_version": "1.0.0",
            "interface_version": "1.0.0", "symbol": symbol, "base_timeframe": "M15",
            "as_of": as_of, "generated_at": as_of, "mode": "REPLAY", "source": "test",
        },
        "clock": {"as_of": as_of, "base_bar_index": 100, "is_new_session": False, "is_new_day": False, "is_new_week": False},
        "symbol_meta": {"symbol": symbol, "tick_size": 0.01, "point_value": 1.0, "price_precision": 2, "session_anchor": "NY_17:00"},
        "session": {"name": session_name, "block_id": 1, "bar_in_session": 5, "session_open_ts": as_of - 3600},
        "calendar": {"date": "2026-07-01", "dow": 2, "dom": 1, "is_holiday": False, "is_weekend_gap": False, "dst_offset_seconds": 0},
        "timeframes": {
            tf: {"timeframe": tf, "bars": [{}] * bars_per_timeframe.get(tf, 10), "features": feats}
            for tf, feats in features.items()
        },
        "data_quality": {"overall": data_quality, "by_timeframe": {}},
        "sufficiency": {"overall": "SUFFICIENT", "missing_fields": None, "missing_timeframes": None, "note": None},
    }
