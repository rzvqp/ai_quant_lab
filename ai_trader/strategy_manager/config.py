"""Configuration objects for the Strategy Manager.

A single :class:`ManagerConfig` instance is supplied to the :class:`~ai_trader.strategy_manager.
manager.StrategyManager` constructor and never mutated afterwards — mirrors the Market Scanner's
``ScannerConfig`` convention (immutable-by-convention configuration, pure query methods given it).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

#: The versions this build of the Manager emits/targets (architecture §11). Bump deliberately.
MANAGER_VERSION = "1.0.0"
REGISTRY_VERSION = "1.0.0"

#: The Strategy Interface / runtime API / feature-dictionary MAJOR versions this build supports
#: (architecture §11 "Versioning" / registry schema ``supported``). A contract or scanner reporting
#: a higher MAJOR is INCOMPATIBLE; a lower or equal MINOR within the same MAJOR is accepted.
DEFAULT_SUPPORTED_INTERFACE_MAJOR = 1
DEFAULT_SUPPORTED_RUNTIME_API_MAJOR = 1
DEFAULT_SUPPORTED_FEATURE_DICTIONARY_MAJOR = 1

#: Default location of the Strategy Library relative to the repo root
#: (``ai_trader/strategy_manager/config.py`` -> parents[2] = repo root).
DEFAULT_LIBRARY_PATH = Path(__file__).resolve().parents[2] / "knowledge" / "strategies"

#: Default staleness threshold for the ``STALE`` health classification (architecture §8):
#: ``lifecycle.last_review`` older than this many days.
DEFAULT_STALE_AFTER_DAYS = 180


@dataclass(slots=True)
class SupportedVersions:
    """The Manager's version-support window (registry schema ``supported`` object)."""

    interface_major: int = DEFAULT_SUPPORTED_INTERFACE_MAJOR
    runtime_api_major: int = DEFAULT_SUPPORTED_RUNTIME_API_MAJOR
    feature_dictionary_major: int = DEFAULT_SUPPORTED_FEATURE_DICTIONARY_MAJOR

    def __post_init__(self) -> None:
        for name, value in (
            ("interface_major", self.interface_major),
            ("runtime_api_major", self.runtime_api_major),
            ("feature_dictionary_major", self.feature_dictionary_major),
        ):
            if value < 1:
                raise ValueError(f"SupportedVersions.{name} must be >= 1, got {value!r}")


@dataclass(slots=True)
class ManagerConfig:
    """Immutable-by-convention configuration for one :class:`StrategyManager` instance.

    Attributes:
        library_path: filesystem path to the Strategy Library root (a directory of
            ``S<NN>_<slug>/strategy.json`` folders). Read-only — the Manager never writes here.
        symbols: the symbol universe every strategy is evaluated against. The frozen Strategy
            Execution Contract schema (``strategy_contract.v1.schema.json``) has no per-strategy
            symbol field at all — the whole Strategy Library is implicitly single-instrument
            (XAUUSD, mirroring the Research Lab's XAUUSD-only campaign, ``PROJECT_STATE_v1.0.md``).
            ``required_context()``/``AggregatedContext.symbols`` (``STRATEGY_REGISTRY_SCHEMA.json``)
            still need a symbol set, so it is supplied here, externally, exactly as the Market
            Scanner receives its own symbol universe via ``configure(symbols=...)`` rather than
            from any single indicator/strategy.
        supported: the interface/runtime-API/feature-dictionary MAJOR versions this build accepts
            (architecture §11).
        auto_admit_min_maturity: if set, any strategy whose contract ``lifecycle.maturity`` is at
            or above this tier is automatically admitted to the live active set (T4) during
            :meth:`~ai_trader.strategy_manager.manager.StrategyManager.load_library`/``reload``.
            ``None`` (the default) means no auto-admission — every strategy rests at
            ``EXPERIMENTAL`` (sandbox-eligible) until an operator/Learning-Engine explicitly calls
            ``activate()``. This is the conservative default: the architecture describes admission
            as a configurable *policy* decision (§"admission policy"), and given no strategy in the
            current Library has been validated beyond exploratory research-segment evidence
            (holdout SEALED, global-FDR NOT run), auto-admitting into the live active set by default
            is not warranted.
        stale_after_days: a strategy's ``lifecycle.last_review`` older than this many days (as of
            the caller-supplied ``as_of`` timestamp — never wall-clock, architecture §4.6/§"Everything
            deterministic") is classified health ``STALE``.
        deprecated_field_paths: dotted JSON paths (e.g. ``"execution.target"``) that the current
            interface MINOR marks deprecated (§5 "Deprecated fields"). Empty by default: nothing is
            deprecated in interface v1.0.0, the first version. Present so the deprecation policy is
            implemented and tested, not a stub, ready for the next interface MINOR that deprecates a
            field.
        registry_version: the shape version of the internal registry object
            (``STRATEGY_REGISTRY_SCHEMA.json``); recorded, not independently configurable (pinned by
            the schema's own ``const``).
        manager_version: this module's implementation/spec version.
    """

    library_path: Path = field(default_factory=lambda: DEFAULT_LIBRARY_PATH)
    symbols: frozenset[str] = frozenset({"XAUUSD"})
    supported: SupportedVersions = field(default_factory=SupportedVersions)
    auto_admit_min_maturity: str | None = None
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS
    deprecated_field_paths: frozenset[str] = field(default_factory=frozenset)
    registry_version: str = REGISTRY_VERSION
    manager_version: str = MANAGER_VERSION

    def __post_init__(self) -> None:
        if self.stale_after_days < 1:
            raise ValueError("ManagerConfig.stale_after_days must be >= 1")
        if not self.symbols:
            raise ValueError("ManagerConfig.symbols must be non-empty")
        if self.auto_admit_min_maturity is not None:
            from ai_trader.strategy_manager.contract import Maturity

            valid = {m.value for m in Maturity}
            if self.auto_admit_min_maturity not in valid:
                raise ValueError(
                    f"ManagerConfig.auto_admit_min_maturity must be one of {sorted(valid)} or "
                    f"None, got {self.auto_admit_min_maturity!r}"
                )
