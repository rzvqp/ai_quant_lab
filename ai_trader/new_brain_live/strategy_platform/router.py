"""Generic Strategy Router (AI Trader New Brain Architecture mandate, section 12). Reads MarketState,
reads enabled catalog entries, checks eligibility, invokes only eligible strategies, collects
`TradeHypothesis` outputs. **Does not decide profitability** -- that is the EV/Decision Engine's job,
strictly downstream (section 12's own explicit boundary).

**Regime classification is never reinvented here.** `ve_brain.applicable_regimes(axes)` -- the SAME
function the canonical N1/Router chain already uses to build `CachedUpstreamContext.eligibility_
decisions` -- is reused verbatim to answer "what regime(s) does this MarketState satisfy," so this
Router's own eligibility check is a strict, additive VIEW over the canonical Market Intelligence output,
never a competing classifier (section 33's own prohibition)."""

from __future__ import annotations

import dataclasses

import ve_brain  # type: ignore[import-untyped]

from ai_trader.new_brain_live.market_state import MarketState, market_state_identity
from ai_trader.new_brain_live.strategy_platform.catalog import CatalogEntry, StrategyCatalog
from ai_trader.new_brain_live.strategy_platform.strategy_protocol import StrategyEvaluationInput
from ai_trader.new_brain_live.strategy_platform.trade_hypothesis import TradeHypothesis

INELIGIBLE_INSTRUMENT_MISMATCH = "INSTRUMENT_MISMATCH"
INELIGIBLE_REGIME_MISMATCH = "REGIME_MISMATCH"
ELIGIBLE_REGIME_INDEPENDENT = "REGIME_INDEPENDENT"
ELIGIBLE_REGIME_MATCH = "REGIME_MATCH"


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class EligibilityResult:
    entry: CatalogEntry
    eligible: bool
    reason_codes: tuple[str, ...]


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class RouterOutcome:
    market_state_identity: str
    eligible: tuple[EligibilityResult, ...]
    ineligible: tuple[EligibilityResult, ...]
    hypotheses: tuple[TradeHypothesis, ...]  # from eligible strategies that returned non-None
    invalid_output: tuple[tuple[str, str], ...]  # (strategy_id, error) -- an eligible strategy that raised


def _market_regimes(market_state: MarketState) -> frozenset[str]:
    regimes = ve_brain.applicable_regimes(market_state.axes)
    return frozenset(r.value for r in regimes)


def check_eligibility(entry: CatalogEntry, *, market_state: MarketState) -> EligibilityResult:
    if market_state.symbol not in entry.allowed_instruments:
        return EligibilityResult(entry=entry, eligible=False, reason_codes=(INELIGIBLE_INSTRUMENT_MISMATCH,))
    if entry.context_eligibility is None:
        return EligibilityResult(entry=entry, eligible=True, reason_codes=(ELIGIBLE_REGIME_INDEPENDENT,))
    matched = _market_regimes(market_state) & frozenset(entry.context_eligibility)
    if not matched:
        return EligibilityResult(entry=entry, eligible=False, reason_codes=(INELIGIBLE_REGIME_MISMATCH,))
    return EligibilityResult(entry=entry, eligible=True, reason_codes=(ELIGIBLE_REGIME_MATCH,))


class StrategyRouter:
    def route(
        self, *, catalog: StrategyCatalog, market_state: MarketState, tower_context: object | None = None,
    ) -> RouterOutcome:
        eligible: list[EligibilityResult] = []
        ineligible: list[EligibilityResult] = []
        hypotheses: list[TradeHypothesis] = []
        invalid_output: list[tuple[str, str]] = []

        for entry in catalog.enabled_entries():
            result = check_eligibility(entry, market_state=market_state)
            (eligible if result.eligible else ineligible).append(result)
            if not result.eligible:
                continue
            evaluation_input = StrategyEvaluationInput(
                market_state=market_state, tower_context=tower_context, config={},
            )
            # Fail-closed PER STRATEGY (section 26 + section 37 "INVALID STRATEGY OUTPUT"): one
            # strategy's bug or malformed hypothesis must never crash the whole evaluation cycle for
            # every OTHER strategy -- it is excluded from `hypotheses`, recorded, and the cycle continues.
            try:
                hypothesis = entry.strategy.evaluate(evaluation_input)
            except Exception as exc:  # noqa: BLE001 -- deliberately broad: ANY strategy failure mode
                # (raised exception, malformed TradeHypothesis construction) must fail closed the same way.
                invalid_output.append((entry.strategy_id, f"{type(exc).__name__}: {exc}"))
                continue
            if hypothesis is not None:
                hypotheses.append(hypothesis)

        return RouterOutcome(
            market_state_identity=market_state_identity(market_state), eligible=tuple(eligible),
            ineligible=tuple(ineligible), hypotheses=tuple(hypotheses), invalid_output=tuple(invalid_output),
        )
