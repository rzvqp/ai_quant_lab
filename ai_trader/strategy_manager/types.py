"""Registry-level value types for the Strategy Manager.

Mirrors ``STRATEGY_REGISTRY_SCHEMA.json`` (the internal registry object) and the result types
summarized in ``STRATEGY_MANAGER_API.md`` §0. Distinct from :mod:`ai_trader.strategy_manager.
contract`, which mirrors the Strategy Execution *Contract* itself — these are the Manager's OWN
operational classifications layered on top (``STRATEGY_MANAGER_STATE_MACHINE.md`` §4: "a derived,
operational view").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ai_trader.strategy_manager.contract import Contract, Maturity


class Lifecycle(str, Enum):
    """The nine operational lifecycle states (``STRATEGY_MANAGER_STATE_MACHINE.md`` §1)."""

    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    INVALID = "INVALID"
    EXPERIMENTAL = "EXPERIMENTAL"
    EXPLORATORY = "EXPLORATORY"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    PROMOTED = "PROMOTED"
    DISABLED = "DISABLED"
    RETIRED = "RETIRED"


#: Lifecycle states admitted to the live active set once the admission policy admits them
#: (architecture §1 "Admission policy": EXPLORATORY+ is live-admissible; EXPERIMENTAL is
#: sandbox/paper-only and never appears here).
ACTIVATABLE_LIFECYCLES: frozenset[Lifecycle] = frozenset({
    Lifecycle.EXPLORATORY, Lifecycle.CANDIDATE, Lifecycle.VALIDATED, Lifecycle.PROMOTED,
})


class Health(str, Enum):
    """Per-strategy health classification (``STRATEGY_MANAGER_ARCHITECTURE.md`` §8)."""

    LOADED = "LOADED"
    DISABLED = "DISABLED"
    INVALID = "INVALID"
    INCOMPATIBLE = "INCOMPATIBLE"
    DUPLICATE = "DUPLICATE"
    DEPRECATED = "DEPRECATED"
    STALE = "STALE"
    MISSING_DEPENDENCY = "MISSING_DEPENDENCY"
    CORRUPTED = "CORRUPTED"


class ManagerOverallHealth(str, Enum):
    """``ManagerHealth.overall`` / ``health_summary.overall``."""

    OK = "OK"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


@dataclass(slots=True)
class ContractRef:
    """``RegistryEntry.contract_ref`` — version/change-tracking, independent of ``Contract``
    itself so it survives even a ``CORRUPTED``/``INVALID`` entry that has no parsed contract."""

    identity_version: str | None = None
    interface_version: str | None = None
    content_hash: str | None = None


@dataclass(slots=True)
class CompatibilityResult:
    """``RegistryEntry.compatibility`` — the Compatibility Checker's verdict
    (``STRATEGY_MANAGER_ARCHITECTURE.md`` §5)."""

    compatible: bool
    schema_valid: bool
    interface_ok: bool
    runtime_ok: bool
    context_ok: bool
    deprecated_fields: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RequiredContext:
    """One strategy's own ``required_context()`` — a pure function of its contract's
    ``semantics.required_data`` (mirrors ``STRATEGY_REGISTRY_SCHEMA.json#/$defs/RequiredContext``
    and ``runtime_responses.v1.schema.json#/$defs/ContextRequirement``)."""

    timeframes: frozenset[str]
    fields_by_timeframe: dict[str, frozenset[str]]
    lookback_by_timeframe: dict[str, int]
    symbols: frozenset[str]
    optional_fields_by_timeframe: dict[str, frozenset[str]] = field(default_factory=dict)
    htf: frozenset[str] = field(default_factory=frozenset)
    warmup_bars: int = 0


@dataclass(slots=True)
class AggregatedContext:
    """``UNION(required_context())`` over ACTIVE strategies — the Market Scanner specification
    (``STRATEGY_REGISTRY_SCHEMA.json#/$defs/AggregatedContext``, architecture §6)."""

    timeframes: frozenset[str]
    required_fields_by_timeframe: dict[str, frozenset[str]]
    lookback_by_timeframe: dict[str, int]
    symbols: frozenset[str]
    feature_dictionary_major: int
    interface_version: str
    contributor_ids: tuple[str, ...]
    optional_fields_by_timeframe: dict[str, frozenset[str]] = field(default_factory=dict)
    warmup_bars: int | None = None


@dataclass(slots=True)
class RegistryEntry:
    """One entry per discovered strategy, including quarantined ones
    (``STRATEGY_REGISTRY_SCHEMA.json#/$defs/RegistryEntry``). Mutated only by
    :class:`~ai_trader.strategy_manager.registry.StrategyRegistry` and
    :class:`~ai_trader.strategy_manager.lifecycle.LifecycleController` — external callers only ever
    see the read-only :class:`StrategyView` projection."""

    id: str
    slug: str
    source_path: str
    lifecycle: Lifecycle
    health: Health
    loaded: bool
    active: bool = False
    contract: Contract | None = None
    contract_ref: ContractRef = field(default_factory=ContractRef)
    compatibility: CompatibilityResult = field(
        default_factory=lambda: CompatibilityResult(False, False, False, False, False)
    )
    required_context: RequiredContext | None = None
    last_review: str | None = None
    errors: list[str] = field(default_factory=list)
    # Not part of STRATEGY_REGISTRY_SCHEMA.json's persisted RegistryEntry shape -- live-only
    # bookkeeping for the Lifecycle Controller's T11 ("DISABLED -> prior state" on `enable()`).
    lifecycle_before_disable: Lifecycle | None = None


@dataclass(frozen=True, slots=True)
class StrategyView:
    """A read-only projection of a strategy's contract + registry state
    (``STRATEGY_MANAGER_API.md`` §0) — NOT a runtime handle."""

    id: str
    name: str | None
    slug: str
    lifecycle: Lifecycle
    health: Health
    identity_version: str | None
    interface_version: str | None
    maturity: Maturity | None
    active: bool


@dataclass(frozen=True, slots=True)
class NotFound:
    """Typed "not found" result (``STRATEGY_MANAGER_API.md`` §2) — never an exception."""

    id: str


@dataclass(frozen=True, slots=True)
class LoadFailure:
    """One failed/quarantined load, in ``LoadReport.failed``/``LoadReport.duplicates``."""

    source_path: str
    id: str | None
    health: Health
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LoadReport:
    """The result of ``load_library()``/``reload()`` (``STRATEGY_MANAGER_API.md`` §1).

    ``loaded`` lists the ids of entries where a valid contract was parsed AND schema-validated
    (``RegistryEntry.loaded is True``) for their canonical (non-duplicate-rejected) entry —
    including ones later found ``INCOMPATIBLE`` (a contract can load successfully yet still fail
    compatibility; those two are different questions). ``failed`` covers every entry that is not a
    usable, canonical, compatible load: ``CORRUPTED``, ``INVALID``, and ``INCOMPATIBLE``.
    ``duplicates`` is the subset of rejected-copy entries specifically classified ``DUPLICATE``,
    broken out separately per the API's own three-way split.
    """

    loaded: tuple[str, ...]
    failed: tuple[LoadFailure, ...]
    duplicates: tuple[LoadFailure, ...]
    counts_by_lifecycle: dict[str, int]
    counts_by_health: dict[str, int]
    registry_version: str
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """The result of a dry ``validate()`` call (``STRATEGY_MANAGER_API.md`` §1) — never mutates
    lifecycle/activation."""

    id: str | None
    ok: bool
    schema_valid: bool
    interface_ok: bool
    runtime_ok: bool
    context_ok: bool
    deprecated: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    """The result of an ``activate``/``deactivate``/``disable``/``enable``/``retire`` call
    (``STRATEGY_MANAGER_API.md`` §4)."""

    id: str
    from_state: Lifecycle | None
    to_state: Lifecycle | None
    ok: bool
    reason: str


@dataclass(frozen=True, slots=True)
class Statistics:
    """The result of ``statistics()`` (``STRATEGY_MANAGER_API.md`` §5)."""

    total: int
    by_lifecycle: dict[str, int]
    by_health: dict[str, int]
    active_count: int
    aggregated_context_summary: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ManagerHealth:
    """The result of ``health()`` (``STRATEGY_MANAGER_API.md`` §5)."""

    overall: ManagerOverallHealth
    counts_by_health: dict[str, int]
    active_count: int
    aggregated_context_ready: bool
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VersionInfo:
    """The result of ``versions()`` (``STRATEGY_MANAGER_API.md`` §5)."""

    manager_version: str
    registry_version: str
    supported_interface_major: int
    supported_runtime_api_major: int
    supported_feature_dictionary_major: int
