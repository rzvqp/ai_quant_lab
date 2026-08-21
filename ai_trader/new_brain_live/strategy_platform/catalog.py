"""Strategy Catalog (AI Trader New Brain Architecture mandate, section 9). An AI-Trader-owned registry,
deliberately NOT `ve_brain`'s own internal catalog -- `ve_brain.n6._SEALED_CATALOG` is sealed, contains
exactly 4 hardcoded strategies, and structurally cannot accept a new entry from outside the installed
package (`INTEGRATION_BLOCKED_VE_BRAIN_STRATEGY_CATALOG.md`, `ai-trader-three-strategies` branch,
2026-08-18 -- read there for the full, adversarially-proven finding). Building THIS catalog as the
generic admission point, independent of `ve_brain`'s sealed registry, is the direct fix for that exact
hot-add blocker: a future validated strategy is admitted HERE, never by waiting for a new `ve_brain`
release to add it to its own internal set."""

from __future__ import annotations

import dataclasses
from enum import Enum

from ai_trader.new_brain_live.strategy_platform.strategy_protocol import Strategy


class StrategyStatus(str, Enum):
    MOCK_TEST_ONLY = "MOCK_TEST_ONLY"
    RESEARCH_ONLY = "RESEARCH_ONLY"
    ALPHA_CANDIDATE = "ALPHA_CANDIDATE"
    VALIDATED = "VALIDATED"
    DISABLED = "DISABLED"
    RETIRED = "RETIRED"


#: Only VALIDATED may ever be eligible for production decision authority (section 9's own explicit
#: rule). Checked by the Router, not merely documented -- see `router.py`.
PRODUCTION_ELIGIBLE_STATUSES = frozenset({StrategyStatus.VALIDATED})


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class CatalogEntry:
    strategy_id: str
    strategy_version: str
    status: StrategyStatus
    enabled: bool
    allowed_instruments: tuple[str, ...]
    allowed_directions: tuple[str, ...]  # "LONG" / "SHORT" -- section 13's own vocabulary
    #: `None` regime tuple means REGIME_INDEPENDENT (section 13: "Do NOT hard-code the assumption that
    #: every strategy requires a regime") -- a non-None, possibly-empty tuple means the strategy DOES
    #: require a regime match, checked against whatever `market_state`-derived regime label the Router
    #: resolves (empty tuple = regime-gated but currently matches nothing, i.e. permanently ineligible
    #: until reconfigured, never silently REGIME_INDEPENDENT by omission).
    context_eligibility: tuple[str, ...] | None
    implementation_fingerprint: str
    config_fingerprint: str
    validation_provenance: str | None
    risk_contract_reference: str
    rollback_identity: str
    strategy: Strategy

    def __post_init__(self) -> None:
        if not self.strategy_id:
            raise ValueError("CatalogEntry.strategy_id must not be empty")
        if not self.strategy_version:
            raise ValueError("CatalogEntry.strategy_version must not be empty")
        if not self.allowed_instruments:
            raise ValueError("CatalogEntry.allowed_instruments must not be empty")
        if not self.allowed_directions:
            raise ValueError("CatalogEntry.allowed_directions must not be empty")
        if not self.implementation_fingerprint:
            raise ValueError("CatalogEntry.implementation_fingerprint must not be empty")
        if not self.config_fingerprint:
            raise ValueError("CatalogEntry.config_fingerprint must not be empty")
        if not self.risk_contract_reference:
            raise ValueError("CatalogEntry.risk_contract_reference must not be empty")
        if not self.rollback_identity:
            raise ValueError("CatalogEntry.rollback_identity must not be empty")
        if self.status is StrategyStatus.VALIDATED and self.validation_provenance is None:
            raise ValueError(
                "CatalogEntry: status=VALIDATED requires a non-None validation_provenance -- a "
                "'validated' strategy with no disclosed evidence is exactly what this catalog must "
                "never accept"
            )


@dataclasses.dataclass(frozen=True, slots=True)
class StrategyCatalog:
    """Immutable snapshot -- a catalog is built once (from real, versioned entries) and never mutated
    in place; a new version is a NEW `StrategyCatalog`, never an in-place edit (same discipline
    `ve_brain`'s own `SealedRegistry` establishes, applied here to a registry AI Trader itself owns)."""

    entries: tuple[CatalogEntry, ...]

    def __post_init__(self) -> None:
        seen = set()
        for e in self.entries:
            key = (e.strategy_id, e.strategy_version)
            if key in seen:
                raise ValueError(f"StrategyCatalog: duplicate (strategy_id, strategy_version) {key!r}")
            seen.add(key)

    def enabled_entries(self) -> tuple[CatalogEntry, ...]:
        return tuple(e for e in self.entries if e.enabled)

    def lookup(self, strategy_id: str, strategy_version: str) -> CatalogEntry | None:
        for e in self.entries:
            if e.strategy_id == strategy_id and e.strategy_version == strategy_version:
                return e
        return None


EMPTY_CATALOG = StrategyCatalog(entries=())
"""The section 10 case -- a catalog with zero entries. Must produce NO_TRADE, never an error; every
consumer of `StrategyCatalog` is written to handle `enabled_entries() == ()` as a completely ordinary,
first-class input, not a special case requiring its own branch."""
