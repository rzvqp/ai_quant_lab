"""Evidence Binder (``SCORING_ENGINE_ARCHITECTURE.md`` §5): read-only fetch + per-cycle cache of a
strategy's contract evidence from the Strategy Manager.

**Design decision — two calls, two different Strategy Manager views.** ``SCORING_MODEL.md`` §3's
``maturity_prior`` table is keyed by ``EXPERIMENTAL``/``EXPLORATORY``/``CANDIDATE``/``VALIDATED``/
``PROMOTED``/``INVALID``/``NOT_IMPLEMENTED`` — this is the Strategy MANAGER's own **operational**
``Lifecycle`` classification (:class:`ai_trader.strategy_manager.types.Lifecycle`, 9 values, from
``find_strategy() -> StrategyView``), NOT the raw contract's ``lifecycle.maturity`` field
(:class:`ai_trader.strategy_manager.contract.Maturity`, only 5 values: EXPLORATORY/CANDIDATE/
VALIDATED/PROMOTED/RETIRED — it has no EXPERIMENTAL/INVALID/NOT_IMPLEMENTED member at all). The
vocabulary match is exact and deliberate, so this binder fetches BOTH: ``find_strategy()`` for the
``Lifecycle`` (maturity_prior lookup) and ``get_contract()`` for the rest of the evidence (OOS/
historical metrics, validation-ladder gates, ``market_regime``) -- read-only, per
``SCORING_ENGINE_ARCHITECTURE.md`` §2 "read a strategy's contract evidence (via Strategy Manager,
read-only)".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ai_trader.strategy_manager.contract import Contract
from ai_trader.strategy_manager.types import Lifecycle, NotFound as SMNotFound, StrategyView


class StrategyManagerLike(Protocol):
    """Structural shape of the Strategy Manager this binder calls. A ``Protocol`` so it works with
    ANY object satisfying this shape -- the real ``StrategyManager``, a test double, or a future
    fuller implementation -- without requiring inheritance."""

    def find_strategy(self, strategy_id: str) -> StrategyView | SMNotFound: ...
    def get_contract(self, strategy_id: str) -> Contract | SMNotFound: ...


@dataclass(frozen=True, slots=True)
class BoundEvidence:
    """The per-strategy evidence snapshot this cycle. Both fields are ``None`` when the strategy is
    unknown to the Strategy Manager (or no manager was supplied at all) -- the fail-safe
    ``EVIDENCE_MISSING`` path (``SCORING_ENGINE_ARCHITECTURE.md`` §7), never fabricated."""

    lifecycle: Lifecycle | None
    contract: Contract | None

    @property
    def found(self) -> bool:
        return self.lifecycle is not None and self.contract is not None


#: Per-call cache: ``strategy_id -> BoundEvidence``. Callers create a fresh dict per
#: ``score_batch()``/``score_signal()`` invocation (never reused across calls) -- "content-addressed"
#: per-cycle caching that cannot itself change results (architecture §6).
EvidenceCache = dict[str, BoundEvidence]


def bind_evidence(
    strategy_id: str, manager: StrategyManagerLike | None, cache: EvidenceCache,
) -> BoundEvidence:
    """Fetch (or return the cached) evidence for ``strategy_id``. Never raises: a broken/missing
    Strategy Manager call is classified as evidence-missing (``BoundEvidence(None, None)``), exactly
    like every other strategy-side failure elsewhere in the AI Trader -- isolated, disclosed, never
    aborting the batch (architecture §7: "contract evidence missing -> historical_confidence=0;
    reason EVIDENCE_MISSING; score capped").
    """
    cached = cache.get(strategy_id)
    if cached is not None:
        return cached

    if manager is None:
        result = BoundEvidence(lifecycle=None, contract=None)
        cache[strategy_id] = result
        return result

    try:
        view = manager.find_strategy(strategy_id)
        contract_result = manager.get_contract(strategy_id)
    except Exception:  # noqa: BLE001 -- any Strategy Manager failure means "evidence unavailable"
        result = BoundEvidence(lifecycle=None, contract=None)
        cache[strategy_id] = result
        return result

    lifecycle = None if isinstance(view, SMNotFound) else view.lifecycle
    contract = None if isinstance(contract_result, SMNotFound) else contract_result
    result = BoundEvidence(lifecycle=lifecycle, contract=contract)
    cache[strategy_id] = result
    return result
