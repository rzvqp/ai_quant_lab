"""Configuration objects for the Signal Engine.

A single :class:`EngineConfig` instance is supplied to the :class:`~ai_trader.signal_engine.engine.
SignalEngine` constructor and never mutated afterwards — mirrors the ``ScannerConfig``/
``ManagerConfig`` convention (immutable-by-convention configuration, pure query methods given it).
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: The versions this build of the engine emits/targets (architecture §11). Bump deliberately.
SIGNAL_ENGINE_VERSION = "1.0.0"
SIGNAL_SCHEMA_VERSION = "1.0.0"
EXPLANATION_SCHEMA_VERSION = "1.0.0"

#: The Strategy Interface / context-schema MAJOR versions this build supports (architecture §11
#: "Versioning" / API §4 "versions()"). A context or strategy reporting a higher MAJOR degrades to
#: NEED_CONTEXT/INVALID rather than being silently accepted.
DEFAULT_SUPPORTED_INTERFACE_MAJOR = 1
DEFAULT_SUPPORTED_CONTEXT_SCHEMA_MAJOR = 1

#: Default per-strategy evaluation time budget (architecture §5 "Timeout policy": "each strategy
#: evaluation has a bounded time budget"). A generous default for pure-Python strategy evaluation;
#: concrete tuning is explicitly left to the deployer (architecture §9: "concrete numbers are an
#: implementation-tuning concern, set at build").
DEFAULT_EVAL_TIMEOUT_S = 1.0


@dataclass(slots=True)
class SupportedVersions:
    """The Engine's version-support window (``versions()`` result, ``SIGNAL_ENGINE_API.md`` §4)."""

    interface_major: int = DEFAULT_SUPPORTED_INTERFACE_MAJOR
    context_schema_major: int = DEFAULT_SUPPORTED_CONTEXT_SCHEMA_MAJOR

    def __post_init__(self) -> None:
        for name, value in (
            ("interface_major", self.interface_major),
            ("context_schema_major", self.context_schema_major),
        ):
            if value < 1:
                raise ValueError(f"SupportedVersions.{name} must be >= 1, got {value!r}")


@dataclass(slots=True)
class EngineConfig:
    """Immutable-by-convention configuration for one :class:`SignalEngine` instance.

    Attributes:
        supported: the interface/context-schema MAJOR versions this build accepts.
        eval_timeout_s: the per-strategy evaluation wall-clock budget (seconds). Enforced via a
            single-worker executor around each strategy's blocking Strategy API calls — this is a
            *resilience* mechanism (architecture §5), not part of the "pure function of context"
            determinism claim: the wall-clock duration a call happens to take is not itself business
            logic and never influences the STATE decision for a call that completes in time (only
            whether it completed in time at all, a binary fail-safe gate).
        signal_engine_version, signal_schema_version, explanation_schema_version: stamped on every
            emitted signal (architecture §11).
        max_workers: how many strategies may be evaluated concurrently within one cycle
            (architecture §9 "Parallel evaluation": "because strategies are isolated and
            independent, evaluations MAY run in parallel; the Output Collector re-imposes the
            deterministic order before emitting, so parallelism never changes results"). Defaults
            to ``1`` (fully sequential) — the simplest, always-correct implementation of the same
            contract; raising this opts into real concurrency, which the architecture guarantees is
            safe given strategy isolation, but sequential evaluation needs no such guarantee to be
            correct, so it is the conservative default.
    """

    supported: SupportedVersions = field(default_factory=SupportedVersions)
    eval_timeout_s: float = DEFAULT_EVAL_TIMEOUT_S
    signal_engine_version: str = SIGNAL_ENGINE_VERSION
    signal_schema_version: str = SIGNAL_SCHEMA_VERSION
    explanation_schema_version: str = EXPLANATION_SCHEMA_VERSION
    max_workers: int = 1

    def __post_init__(self) -> None:
        if self.eval_timeout_s <= 0:
            raise ValueError("EngineConfig.eval_timeout_s must be > 0")
        if self.max_workers < 1:
            raise ValueError("EngineConfig.max_workers must be >= 1")
