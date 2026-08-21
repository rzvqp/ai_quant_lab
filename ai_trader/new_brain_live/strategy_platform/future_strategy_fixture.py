"""Future-validated-strategy fixture (mandate VE-AI-TRADER-GENERIC-EV-AUTHORITY-001, section 13).

Proves MECHANICALLY -- not by assertion -- that a strategy identity NOT hardcoded into `ve_brain`'s sealed
4-strategy catalog (`trend_pullback`/`range_fade`/`trend_shadow`/`trend_experimental`) and NOT one of
`mock_strategies.py`'s 5 `MOCK_TEST_ONLY` fixtures can be: registered (via a real `CatalogEntry`,
`status=VALIDATED`), schema-validated (`TradeHypothesis.__post_init__`), fingerprint-validated
(`RealEVDecisionEngine`'s admission re-verification), routed (`StrategyRouter`), evaluated by the REAL EV
authority (`ve_brain.run_ev`, via `RealEVDecisionEngine`), and return `TRADE_DECISION` or `NO_TRADE`
according to the SAME generic contract every other strategy uses -- no `if strategy_id == "..."` branch
exists anywhere in `real_ev_engine.py` or this file.

This is explicitly NOT S5 (mandate section 5/22: do not implement or onboard S5 here) -- it is a synthetic
stand-in representing "some future validated strategy," with a `strategy_id` that could never be confused
for a real one. It has NO broker authority (inherits the same structural guarantee every strategy in this
package has: `Strategy.evaluate` returns only a `TradeHypothesis`, never touches an order; enforced by
`tests/test_strategies_never_reach_broker.py`'s AST scan, which covers this file too).

Two variants are provided, both reachable through the identical code path, differing only in the
`expected_edge` payload they carry (mirroring the calibrated positive/negative geometries independently
verified against the real `ve_brain.run_ev` before being hardcoded here -- see
`VE_GENERIC_STRATEGY_EV_AUTHORITY_IMPLEMENTATION_REPORT.md` section on EV probing):
  - `FutureValidatedStrategyPositiveEdge` -- well-formed probability inputs with genuinely positive EV_LCB
    -> proves the real `TRADE_DECISION` path end to end for a strategy `ve_brain` has never heard of.
  - `FutureValidatedStrategyNegativeEdge` -- well-formed but poor-performing probability inputs (genuinely
    negative EV_LCB) -> proves the real `NO_TRADE`/`NEGATIVE_EXPECTED_VALUE` path, not merely "unknown
    strategy" NO_TRADE, for the same non-hardcoded identity.
"""

from __future__ import annotations

import dataclasses

from ai_trader.new_brain_live.market_state import market_state_identity
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyStatus
from ai_trader.new_brain_live.strategy_platform.real_ev_engine import EXPECTED_EDGE_SCHEMA_VERSION
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis
from ai_trader.signal_engine.types import Direction

FUTURE_STRATEGY_CONFIG_FINGERPRINT = "future-fixture-config-v1"
FUTURE_STRATEGY_VALIDATION_PROVENANCE = (
    "VE-AI-TRADER-GENERIC-EV-AUTHORITY-001 fixture -- synthetic evidence, NOT a real validation record; "
    "exists solely to exercise the generic admission/EV path end to end. Never promote."
)

# Independently verified against the real ve_brain.run_ev before being hardcoded here (not guessed):
# n=200/n_target=110/n_horizon=60/sum_horizon_R=6.0, rr=2.5, cost=0.09 -> EV_LCB=+1.1065 (enters).
_POSITIVE_EDGE: dict[str, float | str | None] = {
    "edge_schema": EXPECTED_EDGE_SCHEMA_VERSION, "n": 200.0, "n_target": 110.0, "n_horizon": 60.0,
    "sum_horizon_r": 6.0, "credibility": 0.80,
}
# n=200/n_target=20/n_horizon=160/sum_horizon_R=-80.0, same rr/cost -> EV_LCB=-0.3585 (does not enter).
_NEGATIVE_EDGE: dict[str, float | str | None] = {
    "edge_schema": EXPECTED_EDGE_SCHEMA_VERSION, "n": 200.0, "n_target": 20.0, "n_horizon": 160.0,
    "sum_horizon_r": -80.0, "credibility": 0.80,
}


def _hypothesis(
    *, strategy_id: str, strategy_version: str, instrument: str, as_of: int, market_state_id: str,
    edge: dict[str, float | str | None],
) -> TradeHypothesis:
    return TradeHypothesis(
        strategy_id=strategy_id, strategy_version=strategy_version, instrument=instrument,
        direction=Direction.LONG, signal_timestamp=as_of, eligible_entry_timestamp=as_of,
        entry_type="MARKET", intended_entry=100.0, invalidation=98.0, exit_specification="rr:2.5",
        max_hold=20, expected_edge=edge, reason_codes=("FUTURE_STRATEGY_FIXTURE_SIGNAL",),
        market_state_identity=market_state_id, strategy_config_fingerprint=FUTURE_STRATEGY_CONFIG_FINGERPRINT,
        research_validation_identity="fixture-not-a-real-validation", provenance="future_strategy_fixture.py",
    )


@dataclasses.dataclass(frozen=True, slots=True)
class FutureValidatedStrategyPositiveEdge:
    """A strategy identity `ve_brain` has never heard of, carrying genuinely positive EV inputs."""

    strategy_id: str = "FIXTURE_FUTURE_VALIDATED_STRATEGY_POSITIVE"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        return _hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            as_of=state.market_timestamp, market_state_id=market_state_identity(state), edge=_POSITIVE_EDGE,
        )


@dataclasses.dataclass(frozen=True, slots=True)
class FutureValidatedStrategyNegativeEdge:
    """The same kind of never-hardcoded identity, carrying genuinely negative EV inputs -- proves the real
    engine reaches NO_TRADE via actual EV math, not merely because the strategy is unrecognized."""

    strategy_id: str = "FIXTURE_FUTURE_VALIDATED_STRATEGY_NEGATIVE"
    strategy_version: str = "v1"

    def evaluate(self, evaluation_input: StrategyEvaluationInput) -> TradeHypothesis | None:
        state = evaluation_input.market_state
        return _hypothesis(
            strategy_id=self.strategy_id, strategy_version=self.strategy_version, instrument=state.symbol,
            as_of=state.market_timestamp, market_state_id=market_state_identity(state), edge=_NEGATIVE_EDGE,
        )


def catalog_entry_for_future_strategy(
    strategy: FutureValidatedStrategyPositiveEdge | FutureValidatedStrategyNegativeEdge, *,
    allowed_instruments: tuple[str, ...] = ("XAUUSD",),
) -> CatalogEntry:
    """A REAL `CatalogEntry`, `status=VALIDATED`, with real (if synthetic) provenance -- constructed by
    whoever assembles a run's catalog, never by the strategy or engine itself. This is the ONLY way this
    fixture's hypotheses can ever reach `TRADE_DECISION`; without this entry existing in the `StrategyCatalog`
    passed to `RealEVDecisionEngine`, `UNKNOWN_STRATEGY` is the only possible outcome -- proving admission is
    catalog-governed, not identity-governed."""
    return CatalogEntry(
        strategy_id=strategy.strategy_id, strategy_version=strategy.strategy_version,
        status=StrategyStatus.VALIDATED, enabled=True, allowed_instruments=allowed_instruments,
        allowed_directions=("LONG", "SHORT"), context_eligibility=None,
        implementation_fingerprint=f"{strategy.strategy_id}-impl-v1",
        config_fingerprint=FUTURE_STRATEGY_CONFIG_FINGERPRINT,
        validation_provenance=FUTURE_STRATEGY_VALIDATION_PROVENANCE,
        risk_contract_reference="risk_manager_live-v1", rollback_identity=f"{strategy.strategy_id}-rollback-v1",
        strategy=strategy,
    )
