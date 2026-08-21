"""`TradeHypothesis` -- the canonical schema a strategy plugin produces (AI Trader New Brain Architecture
mandate, section 8). A strategy never submits a broker order; it only ever produces `None` (NO_SIGNAL)
or a `TradeHypothesis`, which downstream (EV -> Risk -> Execution) may accept, size, or refuse.

Fields follow existing authoritative contracts where they already exist: `direction` reuses
`signal_engine.types.Direction` (the same vocabulary `TradeProposal`/`LiveRiskDecision` already use, so
no translation layer is needed between this schema and the existing Risk Engine)."""

from __future__ import annotations

import dataclasses

from ai_trader.signal_engine.types import Direction

TRADE_HYPOTHESIS_SCHEMA_VERSION = "trade-hypothesis-v1"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class TradeHypothesis:
    strategy_id: str
    strategy_version: str
    instrument: str
    direction: Direction
    signal_timestamp: int
    eligible_entry_timestamp: int
    entry_type: str  # e.g. "MARKET", "NEXT_BAR" -- research/live execution-model distinction, section 18
    intended_entry: float
    invalidation: float  # stop
    exit_specification: str  # e.g. "rr:3.0", "time:40", "none" -- same vocabulary canonical_specs.py already uses
    max_hold: int
    expected_edge: dict[str, float | str | None] | None  # EV metadata the strategy itself precomputed, if any
    reason_codes: tuple[str, ...]
    market_state_identity: str
    strategy_config_fingerprint: str
    research_validation_identity: str | None
    provenance: str

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise ValueError("TradeHypothesis.strategy_id must not be empty")
        if not self.strategy_version:
            raise ValueError("TradeHypothesis.strategy_version must not be empty")
        if not self.instrument:
            raise ValueError("TradeHypothesis.instrument must not be empty")
        if not isinstance(self.direction, Direction):
            raise ValueError(f"TradeHypothesis.direction must be a Direction, got {self.direction!r}")
        if not self.market_state_identity:
            raise ValueError("TradeHypothesis.market_state_identity must not be empty")
        if not self.strategy_config_fingerprint:
            raise ValueError("TradeHypothesis.strategy_config_fingerprint must not be empty")
        if not self.provenance:
            raise ValueError("TradeHypothesis.provenance must not be empty")
        if self.direction is Direction.LONG and self.invalidation >= self.intended_entry:
            raise ValueError(
                f"TradeHypothesis: LONG requires invalidation strictly below intended_entry, got "
                f"invalidation={self.invalidation!r} intended_entry={self.intended_entry!r}"
            )
        if self.direction is Direction.SHORT and self.invalidation <= self.intended_entry:
            raise ValueError(
                f"TradeHypothesis: SHORT requires invalidation strictly above intended_entry, got "
                f"invalidation={self.invalidation!r} intended_entry={self.intended_entry!r}"
            )

    @property
    def dedup_key(self) -> tuple[str, str, str]:
        """`(strategy, instrument, signal_event)` -- section 23's own required identity. `signal_event`
        is `market_state_identity` (the MarketState this hypothesis was produced from), NOT a separately
        invented episode id -- one MarketState can only ever produce one hypothesis per strategy, so
        this triple is already a complete, minimal, sufficient dedup identity."""
        return (self.strategy_id, self.instrument, self.market_state_identity)
